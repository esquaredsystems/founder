# founder

Personal site of Owais A. Hussain — built with [Jekyll](https://jekyllrb.com/)
and served by GitHub Pages.

**Live:** https://esquaredsystems.github.io/founder/

Adding content is one commit. There is no build step to run, no plugins to
install, and no CI to configure — push to `master` and GitHub rebuilds the site.
See **[CONTENT-GUIDE.md](CONTENT-GUIDE.md)** for exactly what file to create for
each kind of update.

---

## How it's laid out

```
_config.yml              site settings + top navigation
_data/                   ALL structured content, as CSV. Edit and commit.
  profile.csv  links.csv  countries.csv  companies.csv
  education.csv  skills.csv  papers.csv  projects.csv
  teaching.csv  grades.csv  certifications.csv  timeline.csv
_projects/               optional write-up per project; metadata lives in
                         projects.csv           -> /projects/<name>/
_posts/                  English blog posts     -> /writing/YYYY/MM/<slug>/
_bazm/                   Urdu blog posts        -> /bazm/<slug>/
_layouts/                default, page, post, project, bazm
_includes/               head, header, footer, icon, countries, world-map.svg
assets/
  css/style.css          the whole stylesheet — design tokens at the top
  js/site.js             dark-mode toggle and the map hover
  img/flags/             country flags (flag-icons, MIT)
  files/certificates/    certificate PDFs and images
index.html               home page
about.md  projects.html  research.html  teaching.html
certifications.html  writing.html  bazm.html  404.html
feed.xml  sitemap.xml    hand-written, so no plugins are needed
```

Two content patterns, used deliberately:

- **CSV** for everything structured — roles, papers, projects, certifications,
  countries, skills, the timeline. Jekyll reads CSV out of `_data/` natively, so
  there is no converter, no build step of our own, and nothing to install. Edit
  in Excel, Sheets or a text editor; commit; done.
- **Collections** (`_posts/`, `_bazm/`, and `_projects/*.md`) for prose. Writing
  belongs in files, not spreadsheet cells.

The whole repo has no dependency beyond Jekyll itself, which GitHub provides.
Nothing in the deployment path can rot.

## Design

One stylesheet, no framework. Colours, fonts and spacing are CSS custom
properties defined at the top of `assets/css/style.css` under `:root` (light)
and `html[data-theme="dark"]` (dark). Changing the accent colour is one line.

Dark mode follows the operating system by default and can be overridden with
the toggle in the header; the choice is stored in `localStorage`.

Fonts are Newsreader (headings), Inter (body) and Noto Nastaliq Urdu (Urdu
text), loaded from Google Fonts with system fallbacks.

## Running it locally (optional)

You do not need this to publish — but if you want a preview before pushing:

**Windows (one-time setup)**

1. Install **Ruby+Devkit (x64)** from
   [rubyinstaller.org](https://rubyinstaller.org/downloads/). At the end of the
   installer let it run `ridk install` and pick option **3** (MSYS2 and MINGW
   development toolchain).
2. Open a new terminal in this folder and run:

```bash
gem install bundler
bundle install          # first time only, a few minutes
bundle exec jekyll serve --livereload --baseurl ""
```

Then open **http://localhost:4000/**

Leave it running: every time you save a file the site rebuilds and the browser
refreshes. Stop it with `Ctrl+C`.

> Because there is a `Gemfile` in this folder, Jekyll insists on being launched
> through Bundler. Always use `bundle exec jekyll serve`, not `jekyll serve` —
> a bare `jekyll` command will fail with `Could not find gem ...`.

On macOS or Linux the same three commands work once Ruby is installed
(`brew install ruby` / `apt install ruby-full build-essential`).

### A note on Ruby 3.4+

Ruby 3.4 dropped `base64` and `bigdecimal` from its default gems. Jekyll 3.10
still needs both — `safe_yaml` uses one and Liquid the other — so the Gemfile
requires them explicitly. Without those two lines `bundle exec jekyll serve`
fails on Ruby 3.4 with a `cannot load such file -- base64` error. If you ever
regenerate this Gemfile from a tutorial written before 2025, add them back.

## URLs and custom domains

This repo lives under the **esquaredsystems** organisation, so GitHub Pages
treats it as a *project* page and serves it from a subpath. That is why
`_config.yml` sets:

```yaml
url: "https://esquaredsystems.github.io"
baseurl: "/founder"
```

If you later:

- **attach a custom domain** (e.g. `owaishussain.com`) — add a `CNAME` file
  containing the bare domain, then set `url` to `https://owaishussain.com` and
  `baseurl` to `""`.
- **move the repo to a personal account named `owaishussain`** — it becomes a
  user page at `https://owaishussain.github.io/`; set `url` to that and
  `baseurl` to `""`.

Every link in the templates uses `relative_url`, so those two lines are the only
thing you change.

## Publishing

In the repo's **Settings → Pages**, set *Source* to **Deploy from a branch**,
branch `master`, folder `/ (root)`. After that, every push to `master` rebuilds
the site within a minute or two.
