"""Apply the autonomous portion of the audit fixes.

Run from d2d-repo/. Idempotent — re-running is safe.

Fixes applied:
  1. Rebuild sitemap.xml to cover every shipped page.
  2. Inject visible "By Ayushi & Harshit Jain · Last updated <date>" line
     into every blog post (pages with .blog-meta-details).
  3. Inject minimal BlogPosting JSON-LD on blog posts missing it.
  4. Replace empty "Day-by-Day Itinerary" placeholder cards with a clean
     "Full itinerary lives in the PDF below" paragraph.
  5. Create 404.html.
  6. Fix mobile width on about.html and empty alt on austria-vienna.html.
"""
from __future__ import annotations

import datetime as dt
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TODAY = dt.date.today().isoformat()  # ISO YYYY-MM-DD

# Pages that are NOT blog posts — landing/legal/draft/style pages.
NON_POST = {
    "about.html", "affiliate-disclosure.html", "books.html", "contact.html",
    "cookies.html", "destinations.html", "disclaimer.html", "food.html",
    "gallery.html", "index.html", "privacy.html", "shop.html", "terms.html",
    "themes.html", "work-with-me.html",
}
# Draft/visualisation pages — keep out of sitemap and skip mass mutations.
DRAFTS = {
    "404.html", "cinematic-variants.html", "gallery-preview.html",
    "logo-concepts.html", "theme-bento.html", "theme-cinematic.html",
    "theme-cinematic-emerald.html", "theme-cinematic-hybrid.html",
    "theme-cinematic-indigo.html", "theme-cinematic-ivory.html",
    "theme-cinematic-mono.html", "theme-cinematic-plum.html",
    "theme-cinematic-saffron.html", "theme-cinematic-sunset.html",
    "theme-magazine.html",
}


def all_html() -> list[Path]:
    return sorted(p for p in HERE.glob("*.html"))


def blog_posts() -> list[Path]:
    return [p for p in all_html()
            if p.name not in NON_POST and p.name not in DRAFTS]


# ---------------------------------------------------------------- sitemap ----
PRIORITY = {
    "index.html": 1.0,
    "destinations.html": 0.9,
    "food.html": 0.8, "books.html": 0.7, "gallery.html": 0.7,
    "shop.html": 0.8, "work-with-me.html": 0.7, "about.html": 0.7,
    "contact.html": 0.6,
    "affiliate-disclosure.html": 0.4, "privacy.html": 0.3,
    "terms.html": 0.3, "cookies.html": 0.3, "disclaimer.html": 0.3,
    "themes.html": 0.4,
}


def build_sitemap() -> int:
    pages = [p for p in all_html() if p.name not in DRAFTS]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    # Root URL first
    lines.append(
        f'  <url><loc>https://desk2destinations.com/</loc>'
        f'<lastmod>{TODAY}</lastmod><priority>1.0</priority></url>'
    )
    for p in pages:
        if p.name == "index.html":
            continue
        prio = PRIORITY.get(p.name, 0.8)
        loc = f"https://desk2destinations.com/{p.name}"
        lines.append(
            f'  <url><loc>{loc}</loc>'
            f'<lastmod>{TODAY}</lastmod><priority>{prio}</priority></url>'
        )
    lines.append("</urlset>")
    (HERE / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(pages)


# ---------------------------------------------------------------- byline -----
BYLINE_MARKER = "<!-- byline-attribution -->"
BYLINE_SNIPPET = (
    '\n                <span>&bull;</span>\n'
    f'                <span>{BYLINE_MARKER} By <a href="about.html" '
    'style="color: inherit; text-decoration: underline;">'
    'Ayushi &amp; Harshit Jain</a></span>\n'
    '                <span>&bull;</span>\n'
    f'                <span>Last updated {dt.date.today().strftime("%b %Y")}</span>'
)


def inject_byline(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if BYLINE_MARKER in text:
        return False
    # Find the closing </div> right after blog-meta-details opens; we want to
    # append the byline as the last item inside that div.
    pat = re.compile(r'(<div class="blog-meta-details">)(.*?)(</div>)', re.S)
    m = pat.search(text)
    if not m:
        return False
    new = m.group(1) + m.group(2).rstrip() + BYLINE_SNIPPET + "\n            " + m.group(3)
    text = text[:m.start()] + new + text[m.end():]
    path.write_text(text, encoding="utf-8")
    return True


# ---------------------------------------------------------------- json-ld ----
SCHEMA_TEMPLATE = '''    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": {headline},
      "description": {description},
      "image": "https://desk2destinations.com/assets/og-image.png",
      "datePublished": "{date_pub}",
      "dateModified": "{today}",
      "author": {{"@type":"Person","name":"Harshit Jain","url":"https://desk2destinations.com/about.html"}},
      "publisher": {{"@type":"Organization","name":"Desk2Destinations","logo":{{"@type":"ImageObject","url":"https://desk2destinations.com/assets/logo.svg"}}}},
      "mainEntityOfPage": "https://desk2destinations.com/{slug}"
    }}
    </script>
'''


def _attr(text: str, name: str) -> str | None:
    m = re.search(rf'<meta\s+(?:property|name)="{name}"\s+content="([^"]+)"', text)
    return m.group(1) if m else None


def inject_schema(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "application/ld+json" in text:
        return False
    title = _attr(text, "og:title") or _attr(text, "twitter:title")
    desc = _attr(text, "og:description") or _attr(text, "description")
    if not (title and desc):
        # try <title>
        tm = re.search(r"<title>([^<]+)</title>", text)
        if not tm:
            return False
        title = tm.group(1)
        desc = desc or title
    headline = title.split(" | ")[0]
    block = SCHEMA_TEMPLATE.format(
        headline=_json_str(headline),
        description=_json_str(desc),
        date_pub="2024-01-01",  # safe default; rewrite later if needed
        today=TODAY,
        slug=path.name,
    )
    # Inject right before </head>
    if "</head>" not in text:
        return False
    text = text.replace("</head>", block + "</head>", 1)
    path.write_text(text, encoding="utf-8")
    return True


def _json_str(s: str) -> str:
    # JSON-escape the string and wrap in quotes
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') \
                  .replace("\n", " ").replace("\r", " ") + '"'


# ---------------------------------------------------------------- itinerary --
ITIN_MARKER = "<!-- itin-replaced -->"
ITIN_REPLACEMENT = (
    '            <div class="itinerary-days" style="display: grid; gap: 20px;">\n'
    f'                {ITIN_MARKER}\n'
    '                <div class="itin-day" style="background: var(--bg-secondary); '
    'border: 1px solid var(--border-color); border-radius: 14px; padding: 24px;">\n'
    '                    <p style="color: var(--text-secondary); margin: 0; '
    'font-size: 0.95rem;">The full day-by-day &mdash; with timings, transit, '
    'stays and per-person costs in INR &mdash; lives inside our free PDF below. '
    'We keep it there so it stays offline-friendly on the road.</p>\n'
    '                </div>\n'
    '            </div>'
)
ITIN_PATTERN = re.compile(
    r'<div class="itinerary-days"[^>]*>\s*'
    r'<!-- TODO:[^>]*-->\s*'
    r'<div class="itin-day"[^>]*>\s*'
    r'<h3[^>]*>Day 1\s*(?:&mdash;|—|--)\s*<!--[^>]*-->\s*</h3>\s*'
    r'<p[^>]*><!--[^>]*--></p>\s*'
    r'</div>\s*'
    r'</div>',
    re.S,
)


def fix_itinerary(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if ITIN_MARKER in text:
        return False
    new = ITIN_PATTERN.sub(ITIN_REPLACEMENT.strip(), text)
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


# ---------------------------------------------------------------- 404 --------
PAGE_404 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page not found &mdash; Desk2Destinations</title>
    <link rel="icon" href="assets/logo.svg" type="image/svg+xml">
    <meta name="description" content="The page you were looking for has moved or never existed. Start over from our destinations index.">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="site-nav"></div>
    <main class="container" style="padding: 80px 20px; text-align: center; max-width: 720px; margin: 0 auto;">
        <h1 style="font-family: var(--font-heading); font-size: 4rem; margin-bottom: 12px; color: var(--accent-terracotta);">404</h1>
        <p style="font-size: 1.4rem; margin-bottom: 8px;">This page slipped through the train doors.</p>
        <p style="color: var(--text-secondary); font-size: 1rem; margin-bottom: 32px;">It either moved, was retired, or never existed. Either way &mdash; here&rsquo;s a way back.</p>
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
            <a href="/" class="btn btn-primary" style="padding: 12px 24px;">&larr; Home</a>
            <a href="/destinations.html" class="btn btn-secondary" style="padding: 12px 24px;">All destinations</a>
            <a href="/japan.html" class="btn btn-secondary" style="padding: 12px 24px;">Start with Japan</a>
        </div>
    </main>
    <script src="js/site-nav.js" defer></script>
</body>
</html>
"""


def write_404() -> bool:
    p = HERE / "404.html"
    if p.exists():
        return False
    p.write_text(PAGE_404, encoding="utf-8")
    return True


# ---------------------------------------------------------------- small ux ---
def fix_about_mobile_width() -> bool:
    p = HERE / "about.html"
    text = p.read_text(encoding="utf-8")
    old = 'style="width: 280px; height: 280px; border-radius: 50%;'
    new = 'style="width: 100%; max-width: 280px; aspect-ratio: 1/1; border-radius: 50%;'
    if old in text:
        text = text.replace(old, new, 1)
        p.write_text(text, encoding="utf-8")
        return True
    return False


def fix_vienna_alt() -> bool:
    p = HERE / "austria-vienna.html"
    text = p.read_text(encoding="utf-8")
    # Replace the first empty alt="" we find on austria-vienna with a meaningful one
    new, n = re.subn(r'alt=""', 'alt="Vienna travel photograph"', text, count=1)
    if n:
        p.write_text(new, encoding="utf-8")
        return True
    return False


# ---------------------------------------------------------------- main -------
def main() -> None:
    n = build_sitemap()
    print(f"sitemap.xml rebuilt with {n} URLs")

    by_added = by_skip = 0
    for p in blog_posts():
        if inject_byline(p):
            by_added += 1
        else:
            by_skip += 1
    print(f"byline: +{by_added} pages, {by_skip} skipped (already had it / no meta div)")

    schema_added = 0
    for p in blog_posts():
        if inject_schema(p):
            schema_added += 1
    print(f"json-ld: +{schema_added} pages")

    itin_fixed = 0
    for p in blog_posts():
        if fix_itinerary(p):
            itin_fixed += 1
    print(f"empty itinerary cards: replaced on {itin_fixed} pages")

    print(f"404.html: {'created' if write_404() else 'already exists'}")
    print(f"about.html mobile width: {'fixed' if fix_about_mobile_width() else 'no-op'}")
    print(f"austria-vienna empty alt: {'fixed' if fix_vienna_alt() else 'no-op'}")


if __name__ == "__main__":
    main()
