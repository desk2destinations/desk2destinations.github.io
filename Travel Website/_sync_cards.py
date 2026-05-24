"""Sync destinations.html card date+read-time spans with each linked page's blog-meta-details."""
import re
from pathlib import Path

root = Path(r"c:/Users/670242584/Downloads/Travel Website-20260523T212822Z-3-001/Travel Website")
dest = root / "destinations.html"
text = dest.read_text(encoding="utf-8")

card_re = re.compile(
    r'(<article class="dest-card[^>]*>.*?<div class="dest-meta">\s*'
    r'<span><svg[^<]+<path[^/]+/></svg>\s*)([^<]+)(</span>\s*'
    r'<span><svg[^<]+<path[^/]+/></svg>\s*)([^<]+)(</span>\s*</div>.*?'
    r'<a href="([^"]+\.html)" class="dest-link")',
    re.S
)

def extract_meta(page_path):
    if not page_path.exists():
        return None, None
    t = page_path.read_text(encoding="utf-8")
    m = re.search(r'blog-meta-details">(.*?)</div>', t, re.S)
    if not m:
        return None, None
    block = m.group(1)
    spans = re.findall(r'<span[^>]*>([^<]+)</span>', block)
    spans = [s.strip() for s in spans if s.strip() and s.strip() != '•' and s.strip() != '&bull;']
    date = read = None
    for s in spans:
        if 'min read' in s.lower() or 'min' == s.lower().split()[-1] if s else False:
            read = s
        elif re.search(r'\d{4}', s) and not 'min' in s.lower():
            date = s
    # fallback: last is usually read
    if read is None and spans and 'min' in spans[-1].lower():
        read = spans[-1]
    if date is None:
        for s in spans:
            if re.search(r'\d{4}', s):
                date = s
                break
    return date, read

changes = 0
def repl(m):
    global changes
    pre_date, old_date, pre_read, old_read, post, href = m.groups()
    page = root / href
    date, read = extract_meta(page)
    new_date = date if date else old_date.strip()
    new_read = read if read else old_read.strip()
    if new_date != old_date.strip() or new_read != old_read.strip():
        changes += 1
        print(f"  {href}: '{old_date.strip()}' / '{old_read.strip()}' -> '{new_date}' / '{new_read}'")
    return f"{pre_date}{new_date}{pre_read}{new_read}{post}"

new_text = card_re.sub(repl, text)
dest.write_text(new_text, encoding="utf-8")
print(f"\n{changes} cards updated")
