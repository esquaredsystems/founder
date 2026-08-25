# Adding and changing content

Content lives in fourteen CSV files under `_data/`. Jekyll reads CSV natively, so
there is **no build step, no converter and no dependency** — edit a file, commit,
push. GitHub rebuilds the site.

```
_data/*.csv  ──edit──▶  git commit  ──▶  GitHub Pages rebuilds  ──▶  live
```

You can edit them in Excel, in Google Sheets, in VS Code, or straight in the
GitHub web editor. Read the encoding note at the bottom before using Excel.

---

## What each file controls

| File | Drives |
|---|---|
| `profile.csv` | Name, tagline, contact details, the home page intro, a few page headings |
| `links.csv` | Header/footer social links, external blogs, professional memberships |
| `countries.csv` | The world map and flag row on the home page |
| `companies.csv` | The Currently block on the home page and the career history on About |
| `education.csv` | The degrees list on About |
| `skills.csv` | The skills columns on About |
| `papers.csv` | The Research page and the research block on the home page |
| `projects.csv` | The Projects page and the project cards |
| `teaching.csv` | Course outlines on the Teaching page |
| `trainings.csv` | The Trainings section of the Teaching page |
| `courses/` | Lecture files linked under their matching Teaching course |
| `trainings/` | Slide decks linked under their matching training |
| `grades.csv` | The grade distribution chart at the bottom of Teaching |
| `certifications.csv` | The Certifications page |
| `timeline.csv` | The career strip across the home page |

---

## Rules that apply to every file

- **The first column is `#` and is deliberately empty.** Leave it alone. It
  exists to absorb the byte-order mark Excel writes — see the encoding note.
  It is *not* a row number: nothing reads it, so numbering the rows only
  creates something that goes stale the moment you re-sort or delete a row.
  Every line therefore starts with a bare comma.
- **Text is quoted, numbers are not.** Every text value is wrapped in double
  quotes; a column whose values are all numbers (`year`, `order`, `count`,
  `term`) is left bare, because `projects.csv` is sorted on `order` and the
  grade bars do arithmetic on `count` — quote those and `"10"` sorts below
  `"9"`. A quote inside a value is doubled: `"He said ""no"""`.
- **Leave an empty cell truly empty — never `""`.** Jekyll reads a bare empty
  cell as nothing at all, which is what makes `{% if role.location %}` skip it.
  Write `""` and the cell becomes an empty *string*, which Liquid counts as
  true, and the page renders the separator around a value that isn't there.
- **Excel will drop the quotes** when it re-saves a file, on any value that
  does not strictly need them. That is harmless — nothing depends on the
  quoting — so re-quote at your leisure or not at all.
- **Lists inside one cell** are semicolon-separated: `influence mining; complex networks`
- **Yes/no columns** (`featured`, `primary`, `major`) take the literal word `yes`.
  Anything else counts as no.
- **Blank is fine.** An empty optional field is simply left off the page.
- **Never rename** a file or a column header. The templates match on them.
- Rows appear in file order. `papers.csv` and `timeline.csv` should be kept in
  the order you want them displayed; `projects.csv` sorts by its `order` column,
  highest first.
- Grouping columns (`group` in `skills` and `certifications`; `term` in
  `teaching`; `status` in `companies`) collect rows under a heading. Keep rows
  of the same group together.

---

## A few specifics

**profile.csv** is a `key,value` sheet. To add a new field you also need a line
in `_includes/site-vars.html`, which turns those rows into Liquid variables.

**links.csv** has a `kind` column: `link` (header and footer), `blog` (external
blogs) or `membership`. The last two columns are reused per kind — `extra` is
the blog description or the membership's full name, `extra2` is the blog's
language code or the membership grade.

**countries.csv** is just `code` and `name` — every country is shaded the same
and hovering shows only the name. It needs a matching flag file. Copy the `4x3` SVG from
[flag-icons](https://github.com/lipis/flag-icons) (MIT) into
`assets/img/flags/<code>.svg`, lowercase ISO 3166-1 alpha-2. A row without a
flag file still works — the flag is just a broken image.

The map itself is a static SVG at `_includes/world-map.svg`, committed to the
repo. Regenerate it only if you want a different projection or resolution:

```bash
npm pack world-atlas && tar xzf world-atlas-*.tgz
python3 tools/build_world_map.py package/countries-110m.json
```

---

## Slide decks: `courses/` and `trainings/`

Both folders work the same way. A folder of files is attached to a row of a CSV
by **name**, and nothing but the name connects them:

| | The row | The folder must be called |
|---|---|---|
| Courses | a row of `teaching.csv` | `courses/<the course name, slugified>/` |
| Trainings | a row of `trainings.csv` | `trainings/<whatever is in the `slug` column>/` |

"Slugified" means lowercased with every run of non-letters turned into a single
hyphen — `Digital Logic and Design` becomes `digital-logic-and-design`. Get it
wrong by one character and the course still renders, with its outline, and
simply shows no files. There is no error. **If a course's materials vanish,
check the folder name against the course name first.**

Trainings are freer, because the `slug` column says outright which folder to
use; rename the training and the folder can stay put.

**Keep each folder flat** — files sit directly inside it, no subfolders. They
are listed in **alphabetical order**, and that is the only thing deciding the
order, so name them so alphabetical order is reading order: `Lecture 01`,
`Lecture 02` … Where a session has parts, put the numbering at the front of the
name (`1-1-Introduction`, `1-2-IDE and Conventions`) rather than in a folder.

Any file type works; the extension is shown as a small badge beside the name.

**A training row:**

```csv
#,title,date,venue,slug,summary
,Microservices,July 2026,Ghazali University of Technology,microservices,"One sentence to a short paragraph on what the session covered."
```

`date` and `venue` are free text and both are optional — leave either blank and
that half of the line simply disappears. Rows display **in file order** — the
file currently runs oldest-first, so that is how the page reads. Sorting the
file the other way in Excel is all it takes to flip it.

> **Why these two folders have no leading underscore.** Everything else that
> feeds the site — `_data`, `_writing`, `_includes` — starts with one, and it is
> tempting to match. Don't. Jekyll skips underscore-prefixed folders unless they
> are listed under `include:` in `_config.yml`, and `jekyll serve` reads
> `_config.yml` **once, at startup, and never again**. Add a folder that way and
> its files stay missing until you restart the server, with no error to explain
> it. A plain folder name is copied through with no configuration at all, so a
> new folder of decks works the moment you create it.

---

## The things not in CSV

### Blog posts

One piece, one file in `_writing/`, one page. Every piece uses the same
template — `_layouts/post.html` — which reads the front matter and handles the
rest.

**Filename:** `YYYY-MM-DD.html` — just the date. Use `.md` instead if you want
to write the body in Markdown; `.html` is the right choice for verse. Two pieces
on the same day need something to tell them apart: add anything after the date,
e.g. `2015-06-26-b.html`. The filename is never seen by anyone — `permalink:`
sets the URL.

> **Why `_writing/` and not `_posts/`.** Jekyll only accepts a file in `_posts/`
> if it is named `YYYY-MM-DD-slug.ext`. Shorten it to `2015-06-26.html` and
> Jekyll stops treating it as a post at all — skipped, with no error and no
> warning, and the piece silently vanishes. A collection has no such rule, so
> writing lives in `_writing/` and the redundant slug is gone. Everything else
> behaves the same.

**Front matter:**

```yaml
---
title: What I learned porting Bahmni to three clinics
date: 2026-03-14
permalink: /writing/2026/march/bahmni-sync/
category: technology          # poetry | technology | travel | misc
description: One line, used in previews, search results and the RSS feed.
tags: [health informatics, distributed systems]
---
```

For an Urdu post, add two more lines:

```yaml
lang: ur
dir: rtl
```

That switches the article body to right-to-left and Nastaliq. The site header
and footer stay left-to-right, and mixed-language lists stay aligned on one
edge, so an Urdu title does not drift to the far side of the column.

**Sorting** is by `date`, newest first, everywhere — the writing index, each
category page, the home page and the feed. Nothing else to maintain.

#### Unpublished posts

Add one line to the front matter and the post stays off the site:

```yaml
published: false
```

`published` is Jekyll's own front-matter key, not something bolted on here, and
it is absolute: the post is dropped before the site is even assembled. No page
is written, so there is no URL to leak; it is absent from the writing index,
every category page and their counts, the home page, the RSS feed, the sitemap
and the neighbouring posts' ← → links. Nothing has to remember to filter it out,
which is exactly why this is better than a flag that only hides things.

To publish, set `published: true` or just delete the line. Anything without the
key is published — that is the default.

**To read one while you are working on it**, add `--unpublished` to the serve
command:

```bash
bundle exec jekyll serve --livereload --baseurl "" --unpublished
```

That builds unpublished posts too. They appear in the listing with a yellow
`UNPUBLISHED` badge, and the post itself carries a banner saying it is not on
the live site. The flag is local only — GitHub Pages never sees it, so there is
no way to leave it on by accident.

**Why `permalink` is set per post.** Jekyll has no placeholder for a month's
name, only its number. Spelling the month out means writing the URL by hand:
`/writing/2007/august/ghazal/`. Get it wrong and the page still builds, it just
lives at an odd address — so it is worth a glance.

**Categories** live in `_data/categories.csv` (`slug`, `name`, `name_ur`,
`description`). Adding a fifth category means adding a row there, a page under
`writing/` copied from an existing one, and an entry in the `nav:` dropdown in
`_config.yml`.

#### Verse

Poetry posts get a centred composition — eyebrow, title and poem share one
axis. There are exactly two classes to remember: `.verse` wraps the poem and
`.stanza` wraps each unit of it. A unit is a couplet in a ghazal, a band in a
musaddas, a paragraph in free verse — whatever the form makes it. Put a `<br>`
between lines inside a stanza and a blank line between stanzas:

```html
<div class="verse">
  <p class="stanza">پہلا مصرع<br>
  دوسرا مصرع</p>

  <p class="stanza">پہلا مصرع<br>
  دوسرا مصرع</p>
</div>
```

The lines inside a stanza are separated by line-height; stanzas are separated
by margin. Keeping those independent is the entire point — if both gaps look
the same, the poem reads as a flat list of lines instead of a sequence of
ashaar.

Four optional marks, all used by existing posts:

| Class | What it is for | Example |
|---|---|---|
| `verse__letter` | the letter heading an acrostic stanza | `رمضان` |
| `verse__label` | a section divider inside a poem | `گرہ` in *عروج لکھنا* |
| `stanza--quote` | a stanza that quotes rather than says | the hadith in *وضو* |
| `verse__cite` | a source line under the stanza it belongs to | `المائدہ ۔ ۶` |

`verse__cite` goes *inside* the stanza it refers to, not after it, so the
spacing between stanzas stays even:

```html
<p class="stanza stanza--quote">پہلا مصرع<br>
دوسرا مصرع
<span class="verse__cite">صحیح مسلم ۔ کتاب الطہارۃ</span></p>
```

Do not put verse in a plain markdown paragraph. Markdown collapses single line
breaks, which turns a poem into prose. This is why poems are `.html` files.

A dedication or a note about when the piece was written goes in `source_note:`
in the front matter, not in the body — it is set apart from the poem
automatically.

### Project write-ups

`projects.csv` owns every project's title, org, year, tags and summary. A
project that deserves a longer write-up also gets a file at
`_projects/<slug>.md`, containing only its slug and the prose:

```markdown
---
slug: bubsy
---

The full write-up in markdown.
```

The slug must match the `slug` column. Projects with a file get their own page
at `/projects/<slug>/` and are linked from the list; projects without one appear
in the list as plain text. Delete the file and the project stays listed, just
without a page.

---

## Design and layout

`assets/css/style.css` — the first ~60 lines are design tokens:

- `--accent` / `--accent-hover` / `--accent-soft` — the teal; change all three together
- `--bg`, `--surface`, `--text`, `--border` — light mode; the same names are
  redefined under `html[data-theme="dark"]`
- `--map-land`, `--map-worked`, `--map-visited` — the world map
- `--font-display`, `--font-body`, `--font-urdu` — typefaces. Change these and
  also update the Google Fonts `<link>` in `_includes/head.html`

### Navigation

The `nav:` list in `_config.yml`. Order in the file is order in the header. An
item with a `children:` list becomes a dropdown — the parent still links to its
own page, and the children appear on hover, on keyboard focus, or on tap:

```yaml
  - title: Writing
    url: /writing/
    children:
      - title: All posts
        url: /writing/
        note: Everything, newest first
      - title: Poetry
        url: /writing/poetry/
        note: غزل، نظم اور دیگر کلام
```

`note` is the small grey line under each entry, and `lang: ur` switches that
entry to Nastaliq. Both are optional.

---

## Encoding: read this before editing a CSV in Excel

The data contains em-dashes, `Türkiye`, and Urdu. Those survive only if the file
stays UTF-8.

- **Opening:** double-clicking a CSV in Excel can misread UTF-8 and turn `—`
  into `â€"`. If you see that, close without saving and open via
  **Data → From Text/CSV**, choosing **65001: Unicode (UTF-8)**.
- **Saving:** always choose **CSV UTF-8 (Comma delimited)**. Plain
  "CSV (Comma delimited)" writes your locale's encoding and destroys the Urdu.
- **The `#` column:** CSV UTF-8 writes a byte-order mark at the very start of
  the file. Jekyll folds that mark into the name of the first column, so `code`
  becomes something that no longer matches `code` and every lookup silently
  returns nothing. Parking a column nobody reads at the front makes the files
  safe to round-trip. Don't delete it, don't reorder it.

Google Sheets and VS Code both handle these files correctly with no ceremony.

---

## If something breaks

**A section renders empty.** Almost always a header row that got renamed, or the
`#` column deleted so the BOM ate the first real column name. Open the file in a
text editor and check row 1.

**The build fails on GitHub.** You get an email and a red mark on the commit.
CSV rarely fails a build — a broken quote in a cell is the usual cause.

**A change didn't appear.** Give it a minute or two; GitHub Pages rebuilds
asynchronously. If it still hasn't, check the commit actually included the file.
