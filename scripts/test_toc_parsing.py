import docx
import re

doc = docx.Document("docs/KRISHI_Intelligence_KCC_Report_FINAL.docx")

entries = []
for i in range(45, 107):
    p = doc.paragraphs[i]
    t = p.text.strip()
    if not t or t.startswith("LIST OF"):
        continue
    entries.append((i, p.text))

print(f"Total entries found: {len(entries)}")

# Regex pattern to match: (title) + (dots/spaces) + (page_num)
pattern = re.compile(r"^(.*?)(?:\s+(?:\.\s*)+|\s*\.{2,}\s*|\s{3,})([ivx0-9]+)$", re.IGNORECASE)

failed = 0
for idx, text in entries:
    m = pattern.match(text)
    if m:
        title = m.group(1).rstrip()
        page = m.group(2).strip()
        print(f"P{idx:02d} -> Title: {repr(title)} | Page: {repr(page)}")
    else:
        print(f"❌ FAILED TO MATCH P{idx}: {repr(text)}")
        failed += 1

print(f"\nFailed count: {failed} out of {len(entries)}")
