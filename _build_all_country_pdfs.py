"""Build lighter-template PDFs for all 13 non-Italy countries.

Italy is built by _italy_itinerary_build.py and already committed.
Japan-light is written to a separate filename to preserve the existing
cartoon-style desk2destinations-japan.pdf.
"""
from __future__ import annotations

import _country_data as data
from _country_pdf_builder import build_pdf

COUNTRIES = [
    data.JAPAN,
    data.SPAIN,
    data.PORTUGAL,
    data.BELGIUM,
    data.GERMANY,
    data.FRANCE,
    data.NETHERLANDS,
    data.SWITZERLAND,
    data.AUSTRIA,
    data.CZECH,
    data.DENMARK,
    data.SWEDEN,
    data.INDIA,
    data.NEW_ZEALAND,
]


def main():
    for d in COUNTRIES:
        if d.get("slug") == "japan":
            d = dict(d)
            d["slug"] = "japan-light"
        build_pdf(d)


if __name__ == "__main__":
    main()
