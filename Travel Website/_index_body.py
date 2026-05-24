"""Inject extracted body text from each HTML page into search-index.json as a 'body' field."""
import json
import re
from pathlib import Path

root = Path(r"c:/Users/670242584/Downloads/Travel Website-20260523T212822Z-3-001/Travel Website")
idx_path = root / "search-index.json"
entries = json.loads(idx_path.read_text(encoding="utf-8"))

TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
WS_RE = re.compile(r"\s+")

def extract(html_path: Path) -> str:
    if not html_path.exists():
        return ""
    t = html_path.read_text(encoding="utf-8", errors="ignore")
    # Prefer <main> body if present, else everything between <body>
    m = re.search(r"<main[^>]*>(.*?)</main>", t, re.S | re.I)
    if not m:
        m = re.search(r"<body[^>]*>(.*?)</body>", t, re.S | re.I)
    chunk = m.group(1) if m else t
    chunk = SCRIPT_RE.sub(" ", chunk)
    chunk = TAG_RE.sub(" ", chunk)
    chunk = chunk.replace("&nbsp;", " ").replace("&amp;", "&").replace("&ndash;", "-").replace("&#39;", "'")
    chunk = WS_RE.sub(" ", chunk).strip()
    # Cap to keep index reasonable
    return chunk[:40000]

updated = 0
for e in entries:
    url = e.get("url", "")
    if not url or not url.endswith(".html"):
        continue
    body = extract(root / url)
    if body:
        e["body"] = body
        updated += 1

idx_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Updated {updated} entries with body text")

# Regenerate the inlined JS
js_path = root / "search-index.js"
js_path.write_text("window.SEARCH_INDEX = " + json.dumps(entries, ensure_ascii=False) + ";\n", encoding="utf-8")
print(f"Wrote {js_path.name} ({js_path.stat().st_size} bytes)")
