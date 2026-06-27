"""One-shot cleanup: strip dead affiliate UI from all destination pages.

Patterns:
- A/B: must-visit-box block with affiliate cards + an orange shop/PDF CTA.
       Keep the orange CTA, drop everything else, rewrite heading.
- C:   <section class="affiliate-section"> "Book This Trip" block.
       Delete the whole section.

Run from repo root. Prints a per-file report. Idempotent.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent

SKIP_FILES = {
    "affiliate-disclosure.html",
    "work-with-me.html",
}

THEME_PREFIXES = ("theme-", "cinematic-")


def is_destination_page(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if any(path.name.startswith(p) for p in THEME_PREFIXES):
        return False
    return path.suffix == ".html"


def strip_pattern_c(html: str) -> tuple[str, bool]:
    """Remove <section class="affiliate-section">...</section> and surrounding comments."""
    pattern = re.compile(
        r"\n?[ \t]*<!--\s*=+\s*BOOKING / AFFILIATE BLOCK\s*=+\s*-->\s*"
        r"<section\s+class=\"affiliate-section\".*?</section>\s*"
        r"<!--\s*=+\s*END AFFILIATE BLOCK\s*=+\s*-->\s*\n?",
        re.DOTALL,
    )
    new_html, n = pattern.subn("\n", html)
    if n:
        return new_html, True
    fallback = re.compile(
        r"\n?[ \t]*<section\s+class=\"affiliate-section\".*?</section>\s*\n?",
        re.DOTALL,
    )
    new_html, n = fallback.subn("\n", html)
    return new_html, bool(n)


SHOP_LINK_PATTERN = re.compile(
    r'<a\s+href="(shop\.html|[^"]*\.pdf[^"]*)"[^>]*>.*?</a>',
    re.DOTALL | re.IGNORECASE,
)

MUST_VISIT_SECTION_PATTERN = re.compile(
    r'(\n?[ \t]*<!--[^<]*AFFILIATE RESOURCES[^>]*-->\s*)?'
    r'<section\s+class="container"[^>]*>\s*'
    r'<div\s+class="must-visit-box"[^>]*>'
    r'(?P<inner>.*?)'
    r'</div>\s*'
    r'(<!--\s*/affiliate block\s*-->\s*)?'
    r'</section>',
    re.DOTALL,
)


def looks_like_dead_affiliate_box(inner_html: str) -> bool:
    if 'href="#"' in inner_html:
        return True
    if "YOUR_ID" in inner_html:
        return True
    if "Affiliate links" in inner_html or "links below are affiliate" in inner_html:
        return True
    return False


def replace_ab_block(html: str) -> tuple[str, bool]:
    """Replace dead must-visit-box blocks with a slim shop CTA, preserving the orange card."""
    changed = False

    def replacer(match: re.Match[str]) -> str:
        nonlocal changed
        inner = match.group("inner")
        if not looks_like_dead_affiliate_box(inner):
            return match.group(0)
        shop_card_match = SHOP_LINK_PATTERN.search(inner)
        if not shop_card_match:
            changed = True
            return ""
        shop_card = shop_card_match.group(0).strip()
        rewritten = (
            '\n    <section class="container" style="padding: 40px 0;">\n'
            '        <div class="must-visit-box" style="background:linear-gradient(135deg, rgba(255,126,95,0.06), rgba(254,180,123,0.06)); border-left:4px solid var(--accent-terracotta);">\n'
            '            <div style="display:grid; grid-template-columns: minmax(260px, 480px); justify-content:center;">\n'
            f'                {shop_card}\n'
            '            </div>\n'
            '        </div>\n'
            '    </section>\n'
        )
        changed = True
        return rewritten

    new_html = MUST_VISIT_SECTION_PATTERN.sub(replacer, html)
    return new_html, changed


def process_file(path: Path) -> dict[str, bool]:
    original = path.read_text(encoding="utf-8")
    html = original
    html, c_changed = strip_pattern_c(html)
    html, ab_changed = replace_ab_block(html)
    if html != original:
        path.write_text(html, encoding="utf-8")
    return {"c": c_changed, "ab": ab_changed}


def main() -> int:
    files = sorted(p for p in ROOT.iterdir() if is_destination_page(p))
    c_count = 0
    ab_count = 0
    touched: list[str] = []
    for path in files:
        result = process_file(path)
        if result["c"] or result["ab"]:
            touched.append(path.name)
            c_count += int(result["c"])
            ab_count += int(result["ab"])
    print(f"Files touched: {len(touched)}")
    print(f"Pattern C removed in: {c_count}")
    print(f"Pattern A/B rewritten in: {ab_count}")
    for name in touched:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
