"""Inject 'Download PDF' download cards before </main> on every country page.

Idempotent: if the page already references the country slug in a download
link, skip it.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent

CARD_TEMPLATE = (
    '            <!-- pdf-download-card -->\n'
    '            <div style="margin: 32px auto; max-width: 720px; padding: 20px; '
    'background: var(--bg-primary); border: 1px solid var(--border-color); '
    'border-radius: 12px; text-align: center;">\n'
    '                <p style="margin-bottom: 12px; color: var(--text-secondary); '
    'font-size: 0.95rem;">Take this itinerary with you offline.</p>\n'
    '                <a href="assets/pdfs/desk2destinations-{slug}.pdf" download '
    'class="btn btn-primary" style="padding: 10px 24px; display: inline-block;">'
    '&#x2B07; Download {country} PDF (Free)</a>\n'
    '                <p style="margin-top: 10px; font-size: 0.8rem; '
    'color: var(--text-secondary);">A paid version with day-by-day expenses '
    'and bookings is coming soon.</p>\n'
    '            </div>\n'
)

JAPAN_LIGHT_CARD = (
    '            <!-- pdf-download-card-japan-light -->\n'
    '            <div style="margin: 16px auto 32px; max-width: 720px; padding: 20px; '
    'background: var(--bg-primary); border: 1px solid var(--border-color); '
    'border-radius: 12px; text-align: center;">\n'
    '                <p style="margin-bottom: 12px; color: var(--text-secondary); '
    'font-size: 0.95rem;">Prefer a leaner read? Try the lighter, text-first edition.</p>\n'
    '                <a href="assets/pdfs/desk2destinations-japan-light.pdf" download '
    'class="btn btn-primary" style="padding: 10px 24px; display: inline-block;">'
    '&#x2B07; Download Japan PDF &mdash; Lighter Edition</a>\n'
    '            </div>\n'
)

GROUPS = [
    ("italy",          "Italy",          ["italy-rome.html", "italy-amalfi.html", "italy-florence.html", "italy-venice.html"]),
    ("spain",          "Spain",          ["spain-madrid.html", "spain-seville.html", "spain-toledo.html", "barcelona.html"]),
    ("portugal",       "Portugal",       ["portugal-porto.html", "portugal-lisbon.html", "portugal-faro.html"]),
    ("belgium",        "Belgium",        ["belgium-bruges.html"]),
    ("germany",        "Germany",        ["germany-berlin.html", "germany-hamburg.html", "germany-munich.html", "germany-blackforest.html", "germany-stuttgart.html"]),
    ("france",         "France",         ["france-paris.html", "france-paris-2025.html", "france-strasbourg.html"]),
    ("netherlands",    "Netherlands",    ["netherlands-amsterdam.html", "netherlands-rotterdam.html"]),
    ("switzerland",    "Switzerland",    ["switzerland-zurich.html", "switzerland-interlaken.html", "switzerland-lucerne.html", "switzerland-bern.html", "switzerland-montreux.html"]),
    ("austria",        "Austria",        ["austria-vienna.html", "austria-salzburg.html", "austria-werfen.html", "austria-hallstatt.html"]),
    ("czech-republic", "Czech Republic", ["czech-prague.html"]),
    ("denmark",        "Denmark",        ["denmark-copenhagen.html"]),
    ("sweden",         "Sweden",         ["sweden-malmo.html"]),
    ("india",          "India",          ["india-andamans.html", "india-karnataka.html", "india-maharashtra.html", "india-telangana-hyderabad.html", "india-westbengal-kolkata.html", "india-southroadtrip-2025.html"]),
    ("new-zealand",    "New Zealand",    ["nz-south.html", "nz-north.html"]),
]

JAPAN_PAGES = ["japan.html", "japan-tokyo.html", "japan-kyoto.html",
               "japan-osaka.html", "japan-hiroshima.html", "japan-sapporo.html"]


def inject(path: Path, snippet: str, marker: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return False
    if "</main>" not in text:
        print(f"  ! {path.name}: no </main>, skipped")
        return False
    new_text = text.replace("</main>", snippet + "        </main>", 1)
    path.write_text(new_text, encoding="utf-8")
    return True


def main():
    written = 0
    skipped = 0
    for slug, country, pages in GROUPS:
        snippet = CARD_TEMPLATE.format(slug=slug, country=country)
        marker = f"desk2destinations-{slug}.pdf"
        for p in pages:
            path = HERE / p
            if not path.exists():
                print(f"  ? missing {p}")
                continue
            if inject(path, snippet, marker):
                print(f"  + {p}")
                written += 1
            else:
                skipped += 1

    for p in JAPAN_PAGES:
        path = HERE / p
        if not path.exists():
            continue
        if inject(path, JAPAN_LIGHT_CARD, "desk2destinations-japan-light.pdf"):
            print(f"  + {p} (japan-light)")
            written += 1
        else:
            skipped += 1

    print(f"\nWrote {written} pages, {skipped} already had a card.")


if __name__ == "__main__":
    main()
