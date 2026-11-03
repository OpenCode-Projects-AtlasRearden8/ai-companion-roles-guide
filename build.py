#!/usr/bin/env python3
"""Build the AI Companion Roles Guide site from docs/ into site/.

Zero configuration, zero dependencies: Python 3 standard library only.
- docs/*.md            -> site/*.html  (manual pages)
- docs/workbooks/*.md  -> site/workbooks/*.html (print-ready workbooks)
- site/index.html      -> landing page generated from the manual

Run:  python3 build.py
Copyright (c) 2026 Asdale Dynamics, LLC. MIT licensed.
"""

import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
WORKBOOKS = DOCS / "workbooks"
SITE = ROOT / "site"
SITE_WB = SITE / "workbooks"

SITE_TITLE = "AI Companion Roles Guide"

MANUAL_PAGES = [
    "00-start-here",
    "01-why-roles-work",
    "02-helper-modes",
    "03-boundaries",
    "04-when-roles-break",
    "05-rotating-roles",
    "06-card-deck",
    "07-wrap-up",
]

BLURBS = {
    "00-start-here": "The 30-second version of the whole skill, and how to read the manual.",
    "01-why-roles-work": "Why vague asks get vague answers — and the role/job/boundary fix.",
    "02-helper-modes": "The five modes: brainstormer, editor, planner, explainer, drill sergeant-lite.",
    "03-boundaries": "Length, format, tone, scope — boundary language that actually works.",
    "04-when-roles-break": "Jargon hallucination, over-helping, role amnesia, mirrors, mission creep — and the saves.",
    "05-rotating-roles": "Run one conversation through several hats without losing the thread.",
    "06-card-deck": "Thirty starter roles, each with a paste-ready sample opening.",
    "07-wrap-up": "The whole skill in five sentences, plus a two-week plan to make it stick.",
}


# ---------------------------------------------------------------------------
# Tiny Markdown renderer (subset chosen to match docs/ exactly)
# ---------------------------------------------------------------------------

def inline(s: str) -> str:
    """Render inline markdown (code, bold, italic, links) with HTML escaping."""
    parts = re.split(r"(`[^`]+`)", s)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) >= 2:
            out.append("<code>" + html.escape(part[1:-1]) + "</code>")
        else:
            e = html.escape(part)
            e = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", e)
            e = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", e)
            e = re.sub(
                r"\[([^\]]+)\]\(([^)\s]+)\)",
                _sub_link,
                e,
            )
            out.append(e)
    return "".join(out)


def _sub_link(match: re.Match) -> str:
    text, url = match.group(1), match.group(2)
    if url.endswith(".md"):
        url = url[: -len(".md")] + ".html"
    return f'<a href="{url}">{text}</a>'


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:64]


def render_blocks(lines):
    """Parse markdown lines into rendered HTML block strings."""
    blocks = []
    i = 0
    para = []

    def flush():
        nonlocal para
        if para:
            blocks.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped == "":
            flush()
            i += 1
            continue

        if stripped.startswith("```"):
            flush()
            lang = stripped[3:].strip()
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # closing fence
            cls = f' class="lang-{html.escape(lang)}"' if lang else ""
            blocks.append(f"<pre><code{cls}>" + html.escape("\n".join(code_lines)) + "</code></pre>")
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush()
            level = len(m.group(1))
            text = inline(m.group(2))
            blocks.append(f"<h{level}> {text} </h{level}>")
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,})$", stripped):
            flush()
            blocks.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            flush()
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].lstrip())
                i += 1
            blocks.append("<blockquote><p>" + inline(" ".join(quote)) + "</p></blockquote>")
            continue

        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            flush()
            items = []
            checks = []
            ordered = False
            while i < n:
                s = lines[i].strip()
                om = re.match(r"^(\d+)\.\s+(.*)$", s)
                um = re.match(r"^[-*]\s+(.*)$", s)
                cm = re.match(r"^[-*]\s+\[( |x|X)\]\s+(.*)$", s)
                if om:
                    ordered = True
                    items.append(om.group(2))
                elif cm:
                    items.append(cm.group(2))
                    checks.append(cm.group(1).lower() == "x")
                elif um:
                    items.append(um.group(1))
                else:
                    break
                i += 1
            tag = "ol" if ordered else "ul"
            cls = ""
            if checks and not ordered:
                cls = ' class="checks"'
            lis = []
            for idx, item in enumerate(items):
                if checks and idx < len(checks):
                    box = '<span class="box" aria-hidden="true"></span>'
                    lis.append(f'<li class="check">{box} {inline(item)}</li>')
                else:
                    lis.append("<li>" + inline(item) + "</li>")
            blocks.append(f"<{tag}{cls}>" + "".join(lis) + f"</{tag}>")
            continue

        para.append(stripped)
        i += 1

    flush()
    return blocks


def wrap_cards(blocks):
    """Group blocks under each <h3> into a card section (used by the deck)."""
    out = []
    current = None
    for block in blocks:
        if block.startswith("<h3"):
            if current is not None:
                out.append('<section class="card">' + "".join(current) + "</section>")
            current = [block]
        elif current is not None:
            current.append(block)
        else:
            out.append(block)
    if current is not None:
        out.append('<section class="card">' + "".join(current) + "</section>")
    return out


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------

def page_title(blocks) -> str:
    for block in blocks:
        m = re.match(r"<h1> (.*) </h1>", block)
        if m:
            return re.sub(r"<[^>]+>", "", m.group(1))
    return SITE_TITLE


def build_nav(current: str, is_workbook: bool = False) -> str:
    label_map = {
        "00-start-here": "Start Here",
        "01-why-roles-work": "Why Roles Work",
        "02-helper-modes": "Helper Modes",
        "03-boundaries": "Boundaries",
        "04-when-roles-break": "When Roles Break",
        "05-rotating-roles": "Rotating Roles",
        "06-card-deck": "Card Deck",
        "07-wrap-up": "Wrap-Up",
    }
    links = []
    for name in MANUAL_PAGES:
        cls = ' class="active"' if name == current else ""
        links.append(f'<a href="{name}.html"{cls}>{label_map[name]}</a>')
    for wb_name, wb_title in WORKBOOK_TITLES.items():
        cls = ' class="active"' if wb_name == current and is_workbook else ""
        links.append(f'<a href="workbooks/{wb_name}.html"{cls}>{wb_title}</a>')
    return "<nav>" + "".join(links) + "</nav>"


def page_shell(title: str, body: str, body_class: str = "") -> str:
    cls = f' class="{body_class}"' if body_class else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Giving AI a clear role instead of a vague ask - a beginner-friendly manual by Asdale Dynamics, LLC. Education only.">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{'../' if body_class == 'workbook' else ''}styles.css">
</head>
<body{cls}>
{body}
</body>
</html>
"""


FOOTER = """<footer>
<p>AI Companion Roles Guide &middot; education only, never professional advice &middot; free forever</p>
<p>Published by Asdale Dynamics, LLC &middot; <a href="https://opensource.org/license/mit">MIT License</a></p>
</footer>"""


def render_manual_page(stem: str, blocks) -> tuple:
    title = page_title(blocks)
    if stem == "06-card-deck":
        blocks = wrap_cards(blocks)
        body_class = "deck"
    else:
        body_class = ""

    idx = MANUAL_PAGES.index(stem)
    prev_html = next_html = ""
    if idx > 0:
        prev = MANUAL_PAGES[idx - 1]
        prev_html = f'<a class="pn prev" href="{prev}.html">&larr; {PAGETITLES[prev]}</a>'
    if idx < len(MANUAL_PAGES) - 1:
        nxt = MANUAL_PAGES[idx + 1]
        next_html = f'<a class="pn next" href="{nxt}.html">{PAGETITLES[nxt]} &rarr;</a>'
    pager = f'<div class="pager">{prev_html}{next_html}</div>'

    brand = '<p class="brand">AI Companion Roles Guide</p>'
    content = "".join(blocks)
    body = (
        build_nav(stem, False)
        + f'<main class="page">{brand}{content}{pager}</main>'
        + FOOTER
    )
    return title, page_shell(title, body, body_class)


def render_workbook_page(stem: str, blocks) -> tuple:
    title = page_title(blocks)
    nav = (
        '<nav><a href="../index.html">&larr; The Guide</a>'
        '<a href="#" onclick="window.print();return false">Print this workbook</a></nav>'
    )
    hint = (
        '<p class="print-hint">This page is print-ready: open it in any browser and press '
        '<strong>Ctrl+P</strong> (or <strong>Cmd+P</strong> on a Mac). Zero setup required.</p>'
    )
    brand = '<p class="brand">AI Companion Roles Guide &mdash; Print Workbook</p>'
    content = "".join(blocks)
    pager = '<div class="pn home"><a href="../index.html">Back to the guide &larr;</a></div>'
    body = nav + f'<main class="page workbook-page">{brand}{hint}{content}{pager}</main>' + FOOTER
    return title, page_shell(title, body, "workbook")


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------

WORKBOOK_TITLES = {}  # filled during build


def build_index(pagetitles: dict) -> str:
    toc = []
    for stem in MANUAL_PAGES:
        toc.append(
            f'<li><a href="{stem}.html">{html.escape(pagetitles[stem])}</a>'
            f'<span class="blurb">{html.escape(BLURBS.get(stem, ""))}</span></li>'
        )
    wb_toc = []
    for stem, wtitle in WORKBOOK_TITLES.items():
        wb_toc.append(f'<li><a href="workbooks/{stem}.html">{html.escape(wtitle)}</a></li>')

    body = (
        build_nav("", False)
        + f"""<main class="page home">
<p class="brand">AI Companion Roles Guide</p>
<h1>Give the AI a role. Get a better answer.</h1>
<p class="lede">Vague asks get vague answers. This free, beginner-friendly manual shows
you how to pick helper modes, set boundaries, spot broken roles, rotate hats mid-chat &mdash;
with a deck of 30 starter roles, each with a paste-ready opening line.
No jargon, no code, education only, explained like a friend would.</p>
<div class="cta">
<a class="button" href="00-start-here.html">Start the manual &rarr;</a>
<a class="button ghost" href="workbooks/role-picker-workbook.html">Print a workbook</a>
</div>
<h2>Manual</h2>
<ul class="toc">{"".join(toc)}</ul>
<h2>Print workbooks (zero config)</h2>
<p>Open in a browser, press Ctrl+P. No installs, no accounts, no data collection.</p>
<ul class="toc">{"".join(wb_toc)}</ul>
<h2>How this works offline</h2>
<p>Everything is one folder. Rebuild the pages from the Markdown source with
<code>python3 build.py</code>, then open <code>index.html</code> &mdash; or run
<code>python3 -m http.server 8000 --directory site</code> and visit
<code>http://localhost:8000</code>.</p>
</main>"""
        + FOOTER
    )
    title = "AI Companion Roles Guide - Give AI a Clear Role"
    return page_shell(title, body)


def main() -> None:
    global WORKBOOK_TITLES, PAGETITLES
    SITE.mkdir(exist_ok=True)
    SITE_WB.mkdir(exist_ok=True)
    built = []

    # Pass 1: collect titles so prev/next pagers render correctly.
    PAGETITLES = {}
    for stem in MANUAL_PAGES:
        src = DOCS / f"{stem}.md"
        PAGETITLES[stem] = page_title(render_blocks(src.read_text(encoding="utf-8").splitlines()))

    WORKBOOK_TITLES = {}
    for wb_path in sorted(WORKBOOKS.glob("*.md")):
        blocks = render_blocks(wb_path.read_text(encoding="utf-8").splitlines())
        WORKBOOK_TITLES[wb_path.stem] = page_title(blocks)

    # Pass 2: render.
    for stem in MANUAL_PAGES:
        src = DOCS / f"{stem}.md"
        blocks = render_blocks(src.read_text(encoding="utf-8").splitlines())
        title, doc = render_manual_page(stem, blocks)
        out = SITE / f"{stem}.html"
        out.write_text(doc, encoding="utf-8")
        built.append(f"manual:  {out.relative_to(ROOT)}  ({title})")

    for wb_path in sorted(WORKBOOKS.glob("*.md")):
        stem = wb_path.stem
        blocks = render_blocks(wb_path.read_text(encoding="utf-8").splitlines())
        title, doc = render_workbook_page(stem, blocks)
        out = SITE_WB / f"{stem}.html"
        out.write_text(doc, encoding="utf-8")
        built.append(f"workbook: {out.relative_to(ROOT)}  ({title})")

    index_doc = build_index(PAGETITLES)
    (SITE / "index.html").write_text(index_doc, encoding="utf-8")
    built.append(f"landing: {str((SITE / 'index.html').relative_to(ROOT))}")

    for line in built:
        print(line)
    print(f"Done. {len(built)} pages in site/. Open {SITE / 'index.html'}")


if __name__ == "__main__":
    main()
