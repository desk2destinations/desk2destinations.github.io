"""Wire Klook affiliate AID 124253 across every klook.com link in the repo.

Three replacement patterns:
  - Bare https://www.klook.com/  ->  https://www.klook.com/?aid=124253
  - .../?aid=YOUR_ID              ->  .../?aid=124253
  - .../?aid= (empty)             ->  .../?aid=124253

Idempotent — re-running is safe.
"""
from __future__ import annotations

from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
AID = "124253"

PATTERNS = [
    # bare root url, no query
    (re.compile(r'href="https://www\.klook\.com/?"'),
     f'href="https://www.klook.com/?aid={AID}"'),
    # placeholder AID
    (re.compile(r'(href="https://www\.klook\.com[^"]*?\?aid=)YOUR_ID([^"]*?")'),
     rf'\g<1>{AID}\g<2>'),
    # empty aid
    (re.compile(r'(href="https://www\.klook\.com[^"]*?\?aid=)(?=&|")'),
     rf'\g<1>{AID}'),
]


def main():
    touched = 0
    for p in sorted(HERE.glob("*.html")):
        text = p.read_text(encoding="utf-8")
        new = text
        for pat, rep in PATTERNS:
            if callable(rep):
                new = pat.sub(rep, new)
            else:
                new = pat.sub(rep, new)
        if new != text:
            p.write_text(new, encoding="utf-8")
            touched += 1
            print(f"  + {p.name}")
    print(f"\nUpdated {touched} files with AID={AID}")


if __name__ == "__main__":
    main()
