# Adding and changing content

Content lives in twelve CSV files under `_data/`. Jekyll reads CSV natively, so
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
| `grades.csv` | The grade distribution chart at the bottom of Teaching |
| `certifications.csv` | The Certifications page |
| `timeline.csv` | The career strip across the home page |

---

## Rules that apply to every file

- **The first column is `#` and is deliberately empty.** Leave it alone. It
  exists to absorb the byte-order mark Excel writes — see the encoding note.
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

## The things not in CSV

### Blog posts

Prose belongs in files, not cells.

**English** — create `_posts/YYYY-MM-DD-a-short-slug.md`:

```markdown
---
title: What I learned porting Bahmni to three clinics
description: One sentence used in previews, search results and the RSS feed.
tags: [health informatics, distributed systems]
---

Write in markdown. Only `title` is required.
```

**Urdu** — create `_bazm/a-slug.html`:

```html
---
title: عنوان
date: 2026-08-20 10:00:00 +0500
lang: ur
dir: rtl
---

<div class="poem">
پہلا مصرع
دوسرا مصرع
</div>
```

`dir: rtl` switches the article body to right-to-left and Nastaliq; the site
header and footer stay left-to-right. Wrap verse in `<div class="poem">` — that
preserves line breaks exactly as typed and centres the couplets, where an
ordinary markdown paragraph would collapse them and ruin the poem.

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
      - title: Notes
        url: /writing/
        note: Technology, data and teaching
      - title: بزمِ انجم
        url: /bazm/
        lang: ur
        note: Urdu poetry and prose
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
