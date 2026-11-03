#!/usr/bin/env python3
"""Page checks for the AI Companion Roles Guide.

Run:  python3 tests/test_site.py
Rebuilds the site first, then verifies structure, links, counts, and hygiene.
Standard library only.
"""

import re
import subprocess
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
SITE_WB = SITE / "workbooks"

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
WORKBOOKS = ["role-picker-workbook", "routine-workbook"]


def build():
    result = subprocess.run(
        [sys.executable, "build.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise AssertionError(f"build.py failed:\n{result.stdout}\n{result.stderr}")


class TagBalance(HTMLParser):
    """Track whether structural tags stay balanced (void elements ignored)."""

    VOID = {"meta", "link", "br", "hr", "img", "input"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()


def parse_charset_ok(text):
    return '<meta charset="utf-8">' in text


class TestBuildAndFiles(unittest.TestCase):
    def test_00_build_runs_clean(self):
        build()  # raises on failure

    def test_all_manual_pages_built(self):
        for stem in MANUAL_PAGES:
            self.assertTrue((SITE / f"{stem}.html").is_file(), f"missing {stem}.html")

    def test_all_workbooks_built(self):
        for stem in WORKBOOKS:
            self.assertTrue((SITE_WB / f"{stem}.html").is_file(), f"missing {stem}.html")

    def test_landing_and_stylesheet_exist(self):
        self.assertTrue((SITE / "index.html").is_file())
        self.assertTrue((SITE / "styles.css").is_file())


class TestPageStructure(unittest.TestCase):
    def setUp(self):
        build()

    def test_every_page_has_title_and_charset(self):
        pages = list(SITE.glob("*.html")) + list(SITE_WB.glob("*.html"))
        self.assertGreaterEqual(len(pages), 11)
        for page in pages:
            text = page.read_text(encoding="utf-8")
            self.assertIn("<title>", text, str(page))
            self.assertIn("</title>", text, str(page))
            self.assertTrue(parse_charset_ok(text), f"no charset meta in {page.name}")
            self.assertIn('lang="en"', text, str(page))

    def test_manual_pages_have_nav_and_footer_credit(self):
        for stem in MANUAL_PAGES:
            text = (SITE / f"{stem}.html").read_text(encoding="utf-8")
            self.assertIn("<nav>", text, stem)
            self.assertIn("Asdale Dynamics, LLC", text, stem)
            self.assertIn("education only", text, stem)

    def test_prev_next_pager_on_manual_pages(self):
        first = (SITE / "00-start-here.html").read_text(encoding="utf-8")
        middle = (SITE / "03-boundaries.html").read_text(encoding="utf-8")
        last = (SITE / "07-wrap-up.html").read_text(encoding="utf-8")
        self.assertNotIn('class="pn prev"', first)
        self.assertIn('class="pn prev"', middle)
        self.assertIn('class="pn next"', middle)
        self.assertNotIn('class="pn next"', last)

    def test_landing_links_everything(self):
        text = (SITE / "index.html").read_text(encoding="utf-8")
        for stem in MANUAL_PAGES:
            self.assertIn(f'href="{stem}.html"', text, stem)
        for stem in WORKBOOKS:
            self.assertIn(f'href="workbooks/{stem}.html"', text, stem)


class TestInternalLinks(unittest.TestCase):
    def setUp(self):
        build()

    def test_no_unconverted_markdown_links_in_site(self):
        for page in list(SITE.glob("*.html")) + list(SITE_WB.glob("*.html")):
            text = page.read_text(encoding="utf-8")
            for match in re.finditer(r'href="([^"]+)"', text):
                url = match.group(1)
                self.assertFalse(url.endswith(".md"), f"{page.name} links to .md: {url}")

    def test_all_internal_links_resolve(self):
        pages = list(SITE.glob("*.html")) + list(SITE_WB.glob("*.html"))
        checked = 0
        for page in pages:
            text = page.read_text(encoding="utf-8")
            for match in re.finditer(r'href="([^"]+)"', text):
                url = match.group(1)
                if url.startswith(("http://", "https://")) or url == "#":
                    continue
                target = (page.parent / url).resolve()
                self.assertTrue(target.exists(), f"{page.name} -> broken link {url}")
                checked += 1
        self.assertGreater(checked, 60)


class TestCardDeck(unittest.TestCase):
    def setUp(self):
        build()

    def test_deck_has_exactly_30_cards(self):
        text = (SITE / "06-card-deck.html").read_text(encoding="utf-8")
        cards = re.findall(r'<section class="card">', text)
        self.assertEqual(len(cards), 30)
        numbers = re.findall(r"<h3> (\d+)\. ", text)
        self.assertEqual(len(numbers), 30)
        self.assertEqual([int(n) for n in numbers], list(range(1, 31)))

    def test_every_card_has_an_opening_block(self):
        text = (SITE / "06-card-deck.html").read_text(encoding="utf-8")
        cards = text.split('<section class="card">')[1:]
        for card in cards:
            self.assertIn("<pre><code>", card, "card missing sample opening")
            self.assertIn("Boundary tip", card, "card missing boundary tip")

    def test_health_card_is_education_only(self):
        text = (SITE / "06-card-deck.html").read_text(encoding="utf-8")
        self.assertIn("Health-Literacy Librarian", text)
        self.assertIn("Education only, no advice", text)


class TestWorkbooks(unittest.TestCase):
    def setUp(self):
        build()

    def test_workbook_pages_are_print_ready(self):
        styles = (SITE / "styles.css").read_text(encoding="utf-8")
        self.assertIn("@media print", styles)
        for stem in WORKBOOKS:
            text = (SITE_WB / f"{stem}.html").read_text(encoding="utf-8")
            self.assertIn('class="workbook"', text, stem)
            self.assertIn("window.print", text, stem)
            self.assertIn('href="../styles.css"', text, stem)

    def test_checkboxes_render_in_workbooks(self):
        picker = (SITE_WB / "role-picker-workbook.html").read_text(encoding="utf-8")
        routine = (SITE_WB / "routine-workbook.html").read_text(encoding="utf-8")
        self.assertIn('class="check"', picker)
        self.assertIn('class="box"', picker)
        self.assertIn("Day 07", routine)
        self.assertIn("Day 14", routine)


class TestHtmlWellformedness(unittest.TestCase):
    def setUp(self):
        build()

    def test_structural_tags_balance(self):
        pages = list(SITE.glob("*.html")) + list(SITE_WB.glob("*.html"))
        for page in pages:
            parser = TagBalance()
            parser.feed(page.read_text(encoding="utf-8"))
            parser.close()
            self.assertEqual(parser.stack, [], f"{page.name}: unclosed tags {parser.stack}")


class TestRepoHygiene(unittest.TestCase):
    def test_license_line_is_exact(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC\n", text)
        self.assertIn("Permission is hereby granted", text)

    def test_readme_credits_llc(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", text)
        self.assertIn("MIT", text)

    def test_no_secrets_in_source(self):
        pattern = re.compile(
            r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]+",
            re.IGNORECASE,
        )
        for path in list(ROOT.glob("*.py")) + list(DOCS.rglob("*.md")):
            self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")), str(path))

    def test_no_todo_markers_in_published_pages(self):
        for page in list(SITE.glob("*.html")) + list(SITE_WB.glob("*.html")):
            self.assertNotIn("TODO", page.read_text(encoding="utf-8"), str(page))


class TestMarkdownConverter(unittest.TestCase):
    """Unit checks for the tiny renderer in build.py."""

    def setUp(self):
        sys.path.insert(0, str(ROOT))
        import build  # noqa: E402

        self.build = build

    def test_headings(self):
        from build import render_blocks

        blocks = render_blocks(["# Title", "", "## Sub"])
        self.assertEqual(blocks[0], "<h1> Title </h1>")
        self.assertEqual(blocks[1], "<h2> Sub </h2>")

    def test_bold_italic_code(self):
        from build import render_blocks

        blocks = render_blocks(["Read **this** and *that* plus `x = 1`."])
        self.assertIn("<strong>this</strong>", blocks[0])
        self.assertIn("<em>that</em>", blocks[0])
        self.assertIn("<code>x = 1</code>", blocks[0])

    def test_html_is_escaped_outside_code(self):
        from build import render_blocks

        blocks = render_blocks(["a < b & c"])
        self.assertIn("&lt; b &amp; c", blocks[0])

    def test_markdown_links_become_html_links(self):
        from build import render_blocks

        blocks = render_blocks(["see [the deck](06-card-deck.md) now"])
        self.assertIn('href="06-card-deck.html"', blocks[0])

    def test_fenced_code_preserved_and_escaped(self):
        from build import render_blocks

        blocks = render_blocks(["```", "Use & <stuff>", "```"])
        self.assertIn("<pre><code>", blocks[0])
        self.assertIn("Use &amp; &lt;stuff&gt;", blocks[0])

    def test_ordered_and_unordered_lists(self):
        from build import render_blocks

        ul = render_blocks(["- one", "- two"])
        self.assertEqual(ul[0], "<ul><li>one</li><li>two</li></ul>")
        ol = render_blocks(["1. one", "2. two"])
        self.assertEqual(ol[0], "<ol><li>one</li><li>two</li></ol>")

    def test_checkbox_list(self):
        from build import render_blocks

        blocks = render_blocks(["- [ ] unchecked", "- [x] done"])
        self.assertIn('class="checks"', blocks[0])
        self.assertIn('class="check"', blocks[0])
        self.assertEqual(blocks[0].count('<span class="box"'), 2)

    def test_blockquote(self):
        from build import render_blocks

        blocks = render_blocks(["> sage words"])
        self.assertEqual(blocks[0], "<blockquote><p>sage words</p></blockquote>")


if __name__ == "__main__":
    unittest.main(verbosity=1)
