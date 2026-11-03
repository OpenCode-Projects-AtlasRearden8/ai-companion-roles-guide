# STATUS.md — AI Companion Roles Guide

Built 2026-11-03 by an automated build session for **Asdale Dynamics, LLC**.

## What was built

A complete, self-contained education product: a beginner manual on giving AI a clear
role instead of a vague ask, delivered as Markdown docs plus a generated static HTML
site with two zero-config print workbooks.

- **docs/** — the manual, 8 pages of plain-English Markdown:
  - `00-start-here.md` — start here, the 30-second version
  - `01-why-roles-work.md` — vague asks → vague answers; role/job/boundary habit
  - `02-helper-modes.md` — the five modes: Brainstormer, Editor, Planner, Explainer, Drill Sergeant-Lite
  - `03-boundaries.md` — length/format/tone/scope boundary language that actually works
  - `04-when-roles-break.md` — jargon hallucination, over-helping, role amnesia, agreement machines, advice creep + one-line saves
  - `05-rotating-roles.md` — rotating roles mid-chat, carry-over rule, handoff audit
  - `06-card-deck.md` — the 30-role card deck, each card with a paste-ready sample opening and a boundary tip
  - `07-wrap-up.md` — five-sentence summary, two-week practice plan, honest limits
- **docs/workbooks/** — Markdown sources for the print workbooks
- **build.py** — zero-dependency (Python 3 stdlib only) site generator: Markdown subset renderer, card-deck card grouping, prev/next pagers, landing page
- **site/** — 11 generated pages (`index.html`, 8 manual pages, 2 workbooks) + hand-authored `styles.css` with warm palette and print rules
- **site/workbooks/** — `role-picker-workbook.html`, `routine-workbook.html` — open in a browser, Ctrl+P, done (nav/print-hint/print style hooks already verified)
- **tests/test_site.py** — 28 checks: build runs, page structure, nav/footer credit, internal link resolution, exactly 30 deck cards, workbook print hooks, HTML tag balance, repo hygiene (exact LICENSE line, LLC credit, no secrets, no TODOs), and unit tests for the converter
- **LICENSE** — MIT, copyright line exactly `Copyright (c) 2026 Asdale Dynamics, LLC`
- **README.md** — credits Asdale Dynamics, LLC; run/preview instructions

Tone throughout is warm and jargon-free per Dylan Asdale's style; all health-adjacent content (Health-Literacy Librarian card, routine workbook) is explicitly education-only and points to licensed professionals.

## How to run it

```bash
python3 build.py            # rebuild site/ from docs/
python3 tests/test_site.py  # rebuild + run all 28 checks
python3 -m http.server 8000 --directory site   # optional local preview
```

Or just open `site/index.html` directly in any browser — no server required.

## Verification results

- `python3 build.py` — clean run, 11 pages built, no warnings
- `python3 tests/test_site.py` — **28/28 passed**
- Http smoke test over a real local server: index, deck page, and workbook pages served `200`; unknown page `404`
- All internal links in all generated pages resolve; zero `.md` links leak into HTML
- Card deck verified: exactly 30 `<section class="card">` blocks, numbered 1–30, each with a sample opening and boundary tip
- LICENSE line verified character-exact; README credit verified; no secrets/tokens in any source file

## Known gaps

- The Markdown renderer covers the subset used by docs/ (headings, lists incl. checkboxes, blockquotes, fenced code, bold/italic/code/links, hr) — not full CommonMark; docs must stay within it
- Heading anchors (in-page `#fragment` navigation) are not generated — cross-links are page-level only
- Workbooks are passive print pages: no fill-in interactivity on screen (by design, zero-config print first)
- No search, dark mode, or minification — deliberate scope cut for a single-folder offline product
- Not git-pushed anywhere per instructions; repo is local-only with a single commit
