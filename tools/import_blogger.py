#!/usr/bin/env python3
"""
Import a Blogger/Blogspot backup XML into this Jekyll site.

Usage
-----
    python3 tools/import_blogger.py BACKUP.xml --target posts
    python3 tools/import_blogger.py BACKUP.xml --target bazm

`--target posts` writes English posts into `_posts/`  (the Writing section).
`--target bazm`  writes Urdu posts into `_bazm/`      (the Urdu section).

What it does
------------
* Reads posts, their labels, their original Blogspot URL, and their comments.
* Skips drafts unless you pass --include-drafts.
* Keeps the post body as HTML rather than converting it to markdown. Blogger
  bodies carry meaningful <br> line breaks (verse) and <pre> blocks (shell and
  code), and a markdown round-trip damages both. Files are therefore written
  with a .html extension, which Jekyll renders with front matter but without
  running it through kramdown. New posts you write by hand can still be .md.
* Strips Blogger's inline junk: font tags, style attributes, empty spans,
  MsoNormal classes, and the trailing "Posted by" cruft.
* Rewrites every Blogger-hosted image URL to a local path under
  assets/img/blog/, and writes the download list to tools/blog-images.txt for
  fetch_blog_images.ps1 to pull down.
* Attaches comments to their post as front-matter data, rendered read-only by
  _includes/comments.html.

Nothing is fetched from the network here — this is a pure file transform.
"""

import argparse
import os
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse, unquote

from bs4 import BeautifulSoup, NavigableString

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "app": "http://www.w3.org/2007/app",
    "thr": "http://purl.org/syndication/thread/1.0",
}

KIND_SCHEME = "http://schemas.google.com/g/2005#kind"
LABEL_SCHEME = "http://www.blogger.com/atom/ns#"

IMAGE_HOSTS = (
    "bp.blogspot.com",
    "blogger.googleusercontent.com",
    "lh3.googleusercontent.com",
    "lh4.googleusercontent.com",
    "lh5.googleusercontent.com",
    "lh6.googleusercontent.com",
    "photos.google.com",
    "1.bp.blogspot.com",
    "2.bp.blogspot.com",
    "3.bp.blogspot.com",
    "4.bp.blogspot.com",
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def parse_ts(value):
    """Blogger timestamps look like 2015-01-10T21:04:00.000+05:00."""
    if not value:
        return None
    value = value.strip()
    value = re.sub(r"\.\d+", "", value)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def yaml_quote(text):
    if text is None:
        text = ""
    text = str(text).replace("\\", "\\\\").replace('"', '\\"')
    text = text.replace("\n", " ").strip()
    return '"%s"' % text


def slug_from_url(url, fallback_date, seen):
    """
    Prefer Blogger's own slug so the shape of old links stays recognisable.
    Blogger URLs look like /2015/01/some-title.html — take `some-title`.
    Urdu posts often get an auto slug like `blog-post_31`, which is ugly but
    stable; those fall back to a date-based name instead.
    """
    name = ""
    if url:
        path = unquote(urlparse(url).path)
        name = os.path.splitext(os.path.basename(path))[0]

    if not name or re.fullmatch(r"blog-post(_\d+)?", name):
        name = fallback_date.strftime("%Y-%m-%d") if fallback_date else "post"

    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^A-Za-z0-9\-]+", "-", name).strip("-").lower()
    if not name:
        name = fallback_date.strftime("%Y-%m-%d") if fallback_date else "post"

    base, n = name, 2
    while name in seen:
        name = "%s-%d" % (base, n)
        n += 1
    seen.add(name)
    return name


def looks_like_verse(node):
    """
    A block is treated as verse when it is short lines separated by <br> and
    contains no sentence-ending punctuation runs. Urdu poetry on Blogger is
    almost always a single <div> or <p> full of <br> tags.
    """
    breaks = len(node.find_all("br"))
    if breaks < 3:
        return False
    text = node.get_text("\n", strip=True)
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if len(lines) < 4:
        return False
    long_lines = [ln for ln in lines if len(ln) > 90]
    return len(long_lines) <= len(lines) * 0.2


# --------------------------------------------------------------------------
# cleaning
# --------------------------------------------------------------------------

def clean_html(raw, images, mark_verse):
    soup = BeautifulSoup(raw or "", "html.parser")

    # Blogger wraps everything in presentational junk.
    for tag in soup.find_all(["font", "o:p"]):
        tag.unwrap()
    for tag in soup.find_all(True):
        for attr in ("style", "class", "id", "face", "color", "size",
                     "cellpadding", "cellspacing", "border", "align",
                     "bgcolor", "width", "height", "trbidi", "dir"):
            tag.attrs.pop(attr, None)

    # Drop empty spans and divs left behind.
    for tag in soup.find_all(["span", "div"]):
        if not tag.attrs and not tag.get_text(strip=True) and not tag.find(["img", "br", "iframe"]):
            tag.decompose()
    for tag in soup.find_all("span"):
        if not tag.attrs:
            tag.unwrap()

    # Blogger's lightbox wrappers: <a href="big.jpg"><img src="small.jpg"></a>
    for a in soup.find_all("a"):
        img = a.find("img")
        if img and a.get("href") and any(h in a["href"] for h in IMAGE_HOSTS):
            a.replace_with(img)

    # Rewrite image sources to local paths and record what to download.
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src:
            continue
        if any(h in src for h in IMAGE_HOSTS):
            local = local_image_path(src)
            images[src] = local
            img["src"] = "{{ '%s' | relative_url }}" % local
        img.attrs.pop("border", None)
        if not img.get("alt"):
            img["alt"] = ""
        img["loading"] = "lazy"

    if mark_verse:
        for node in soup.find_all(["div", "p"]):
            if node.find(["div", "p", "pre", "table"]):
                continue
            if looks_like_verse(node):
                node.name = "div"
                node["class"] = "poem"

    html = str(soup).strip()
    html = re.sub(r"(\s*<br\s*/?>\s*){3,}", "\n<br>\n", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html


def local_image_path(url):
    path = unquote(urlparse(url).path)
    name = os.path.basename(path) or "image"
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name)
    if not os.path.splitext(name)[1]:
        name += ".jpg"
    return "/assets/img/blog/" + name


def summarise(html, limit=200):
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xml")
    ap.add_argument("--target", choices=["posts", "bazm"], required=True)
    ap.add_argument("--include-drafts", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    import xml.etree.ElementTree as ET
    tree = ET.parse(args.xml)
    root = tree.getroot()

    posts, comments = [], defaultdict(list)

    for entry in root.findall("atom:entry", NS):
        kind = ""
        labels = []
        for cat in entry.findall("atom:category", NS):
            scheme, term = cat.get("scheme", ""), cat.get("term", "")
            if scheme == KIND_SCHEME:
                kind = term.rsplit("#", 1)[-1]
            elif scheme == LABEL_SCHEME:
                labels.append(term)

        if kind == "post":
            control = entry.find("app:control", NS)
            draft = control is not None and (control.findtext("app:draft", "", NS) or "").strip() == "yes"
            if draft and not args.include_drafts:
                continue
            alt = ""
            for link in entry.findall("atom:link", NS):
                if link.get("rel") == "alternate" and link.get("type") == "text/html":
                    alt = link.get("href", "")
            posts.append({
                "id": entry.findtext("atom:id", "", NS),
                "title": (entry.findtext("atom:title", "", NS) or "").strip(),
                "published": parse_ts(entry.findtext("atom:published", "", NS)),
                "content": entry.findtext("atom:content", "", NS) or "",
                "labels": labels,
                "url": alt,
                "draft": draft,
            })

        elif kind == "comment":
            ref = ""
            reply = entry.find("thr:in-reply-to", NS)
            if reply is not None:
                ref = reply.get("ref", "")
            author = entry.find("atom:author", NS)
            comments[ref].append({
                "author": (author.findtext("atom:name", "", NS) or "").strip() if author is not None else "",
                "author_url": (author.findtext("atom:uri", "", NS) or "").strip() if author is not None else "",
                "date": parse_ts(entry.findtext("atom:published", "", NS)),
                "content": entry.findtext("atom:content", "", NS) or "",
            })

    posts.sort(key=lambda p: p["published"] or datetime.min)

    outdir = os.path.join(REPO, "_posts" if args.target == "posts" else "_bazm")
    is_urdu = args.target == "bazm"
    os.makedirs(outdir, exist_ok=True)

    images, seen, written = {}, set(), 0

    for post in posts:
        date = post["published"]
        slug = slug_from_url(post["url"], date, seen)
        body = clean_html(post["content"], images, mark_verse=is_urdu)

        # A handful of posts on the Urdu blog are actually in English.
        rtl = is_urdu and bool(re.search(r"[؀-ۿ]", post["title"] + body[:400]))

        fm = ["---"]
        fm.append("title: %s" % yaml_quote(post["title"] or "(untitled)"))
        if date:
            fm.append('date: %s' % date.strftime("%Y-%m-%d %H:%M:%S %z"))
        fm.append("description: %s" % yaml_quote(summarise(body)))
        if post["labels"]:
            fm.append("tags: [%s]" % ", ".join(yaml_quote(l) for l in post["labels"]))
        if is_urdu:
            fm.append("lang: %s" % ("ur" if rtl else "en"))
            fm.append("dir: %s" % ("rtl" if rtl else "ltr"))
        if post["url"]:
            fm.append("source_url: %s" % yaml_quote(post["url"]))
        if post["draft"]:
            fm.append("published: false")

        for c in sorted(comments.get(post["id"], []), key=lambda c: c["date"] or datetime.min):
            if not fm[-1].startswith("comments:"):
                if "comments:" not in fm:
                    fm.append("comments:")
            fm.append("  - author: %s" % yaml_quote(c["author"] or "Anonymous"))
            if c["author_url"]:
                fm.append("    author_url: %s" % yaml_quote(c["author_url"]))
            if c["date"]:
                fm.append("    date: %s" % c["date"].strftime("%Y-%m-%d %H:%M:%S %z"))
            text = BeautifulSoup(c["content"], "html.parser").get_text("\n", strip=True)
            fm.append("    content: |")
            for line in text.split("\n"):
                fm.append("      " + line)
        fm.append("---")

        if args.target == "posts":
            fname = "%s-%s.html" % (date.strftime("%Y-%m-%d") if date else "1970-01-01", slug)
        else:
            fname = "%s.html" % slug

        out = "\n".join(fm) + "\n\n" + body + "\n"
        if args.dry_run:
            print("would write %-60s (%d comments)" % (fname, len(comments.get(post["id"], []))))
        else:
            with open(os.path.join(outdir, fname), "w", encoding="utf-8") as fh:
                fh.write(out)
        written += 1

    manifest = os.path.join(REPO, "tools", "blog-images.txt")
    mode = "a" if os.path.exists(manifest) and args.target == "bazm" else "w"
    if not args.dry_run:
        with open(manifest, mode, encoding="utf-8") as fh:
            for remote, local in sorted(images.items()):
                fh.write("%s\t%s\n" % (remote, local))

    print("posts written : %d -> %s" % (written, os.path.relpath(outdir, REPO)))
    print("images to fetch: %d (listed in tools/blog-images.txt)" % len(images))
    total_comments = sum(len(v) for v in comments.values())
    print("comments       : %d" % total_comments)


if __name__ == "__main__":
    sys.exit(main())
