# AI Companion Roles Guide

*Giving AI a clear role instead of a vague ask — explained like a friend would.*

Vague asks get vague answers. When you tell an AI *what job it is doing today* — brainstormer, editor, planner, explainer, gentle routine-coach — the answers get sharper, shorter, and more useful. This is a beginner-friendly manual for exactly that: picking helper modes, setting boundaries, spotting when a role breaks, rotating roles mid-chat, and a deck of 30 starter roles with ready-to-paste sample openings.

- **Who it is for:** complete beginners, students, working parents, shift workers — anyone who talks to an AI and wants better answers without learning jargon.
- **What it is not:** it is never medical, legal, or financial advice. It is education only, in a warm voice.

## What is inside

| Path | What it is |
| --- | --- |
| `docs/` | The manual, in plain Markdown (8 pages, including a 30-role card deck) |
| `site/` | A static HTML site built from the docs — works offline from a single folder |
| `site/workbooks/` | Zero-config print workbooks: open in a browser, press Ctrl+P |
| `build.py` | Rebuilds the site from the docs (Python 3, standard library only) |
| `tests/test_site.py` | Runs the page checks (links, titles, print styles, card count) |

The manual covers:

1. Why vague asks get vague answers
2. The five helper modes (brainstormer, editor, planner, explainer, drill sergeant-lite)
3. Setting boundaries in prompts
4. When a role breaks (jargon hallucination, over-helping, and friends)
5. Rotating roles mid-chat
6. The 30-role card deck with sample openings
7. Pick-your-role workbook, in print form
8. A Gentle wrap-up

## How to use it

Everything is local-first and free forever. No accounts, no keys, no data leaves your machine.

```bash
# Rebuild the site from the docs
python3 build.py

# Preview the site locally
python3 -m http.server 8000 --directory site

# Run the page checks
python3 tests/test_site.py
```

Then open `http://localhost:8000` — or simply double-click `site/index.html`. The print workbooks are ordinary pages with print styles; open one and print. That is the whole configuration.

## Privacy notes

- No secrets, API keys, or personal data are included or required.
- The check scripts never send anything anywhere.

## Health & routines caution

This guide talks about habits, routines, and study roles for education only. It never gives medical advice, and no role card should be used to self-treat a health condition. When health comes up, the Health-Literacy Librarian card points you toward asking a licensed professional — not replacing one.

## License & credit

MIT licensed. See [LICENSE](LICENSE). Built and maintained by **Asdale Dynamics, LLC**, as part of Dylan Asdale's beginner-friendly AI education series (*The Massive AI Manual*, and more at the hub site). Copyright (c) 2026 Asdale Dynamics, LLC.
