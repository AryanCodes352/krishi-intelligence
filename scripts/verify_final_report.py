"""
Verification script for docs/KRISHI_Intelligence_KCC_Report_FINAL.docx
"""

import os
import re
import docx
from docx import Document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX_PATH = os.path.join(BASE_DIR, "docs", "KRISHI_Intelligence_KCC_Report_FINAL.docx")
FIG_DIR = os.path.join(BASE_DIR, "docs", "figures")

doc = Document(DOCX_PATH)

print("=" * 60)
print("AUDIT REPORT: KRISHI_Intelligence_KCC_Report_FINAL.docx")
print("=" * 60)

# 1. Search for forbidden strings
forbidden = [
    "[Faculty Guide Name]",
    "[HOD Name]",
    "22049201000XX",
    "2025–2026",
    "2025-2026",
    "Semester VI",
    "VI Semester"
]

found_forbidden = []

# Check all paragraphs
for i, p in enumerate(doc.paragraphs):
    for f in forbidden:
        if f in p.text:
            found_forbidden.append((f"Paragraph {i}", f, p.text.strip()))

# Check all table cells
for t_idx, t in enumerate(doc.tables):
    for r_idx, row in enumerate(t.rows):
        for c_idx, cell in enumerate(row.cells):
            for f in forbidden:
                if f in cell.text:
                    found_forbidden.append((f"Table {t_idx}[{r_idx},{c_idx}]", f, cell.text.strip()))

if found_forbidden:
    print(f"❌ FAIL: Found {len(found_forbidden)} forbidden occurrences:")
    for loc, f, txt in found_forbidden:
        print(f"  {loc} contains '{f}': {txt[:70]}...")
else:
    print("✓ PASS: Zero forbidden placeholder strings found across all paragraphs and tables!")

# 2. Check Team Members & Rolls
expected_members = [
    ("Aryan", "2404920100101"),
    ("Prabhat Kumar Jha", "2404920100240"),
    ("Priyanshu Kumar", "2404920100259"),
    ("Pratibha Yadav", "2404920100247"),
]

all_doc_text = "\n".join([p.text for p in doc.paragraphs] + [c.text for t in doc.tables for r in t.rows for c in r.cells])

all_members_present = True
for name, roll in expected_members:
    in_text = (name in all_doc_text) and (roll in all_doc_text)
    print(f"  Member {name} ({roll}): {'✓ Present' if in_text else '❌ Missing'}")
    if not in_text:
        all_members_present = False

if all_members_present:
    print("✓ PASS: All 4 members and AKTU roll numbers present in document.")

# 3. Check Faculty Guide & HOD
guide_ok = "Mr. Chand Babu" in all_doc_text
hod_ok = "Mr. Chetan Khemraj" in all_doc_text
print(f"  Project Guide 'Mr. Chand Babu': {'✓ Present' if guide_ok else '❌ Missing'}")
print(f"  HOD 'Mr. Chetan Khemraj': {'✓ Present' if hod_ok else '❌ Missing'}")

# 4. Check Fig 3.1 & Fig 3.2 binary size match
fig_3_1_expected = os.path.getsize(os.path.join(FIG_DIR, "fig_3_1_system_architecture.png"))
fig_3_2_expected = os.path.getsize(os.path.join(FIG_DIR, "fig_3_2_dfd_level_0_and_1.png"))

blob_3_1 = len(doc.part.rels["rId10"].target_part.blob)
blob_3_2 = len(doc.part.rels["rId11"].target_part.blob)

print(f"  Fig 3.1 blob size: {blob_3_1} bytes (Expected: {fig_3_1_expected} bytes) -> {'✓ Match' if blob_3_1 == fig_3_1_expected else '❌ Mismatch'}")
print(f"  Fig 3.2 blob size: {blob_3_2} bytes (Expected: {fig_3_2_expected} bytes) -> {'✓ Match' if blob_3_2 == fig_3_2_expected else '❌ Mismatch'}")

# 5. Check Table 5.1 & Table 5.2 Ordering
p93_text = doc.paragraphs[93].text.strip()
p94_text = doc.paragraphs[94].text.strip()
p207_text = doc.paragraphs[207].text.strip()
p208_text = doc.paragraphs[208].text.strip()
p211_text = doc.paragraphs[211].text.strip()
p212_text = doc.paragraphs[212].text.strip()

print("\n--- Table 5.1 & 5.2 Check ---")
print(f"  List of Tables P93: {p93_text}")
print(f"  List of Tables P94: {p94_text}")
print(f"  Chapter 5 P207: {p207_text}")
print(f"  Chapter 5 P208: {p208_text}")
print(f"  Chapter 5 P211: {p211_text[:90]}...")
print(f"  Chapter 5 P212: {p212_text}")

# 6. Check Fig 4.4 Captions
p103_text = doc.paragraphs[103].text.strip()
p199_text = doc.paragraphs[199].text.strip()
print("\n--- Fig 4.4 Caption Check ---")
print(f"  List of Figures P103: {p103_text}")
print(f"  Section 4.6 P199: {p199_text}")

# 7. Check Code Listings Font and Formatting
print("\n--- Code Listings Check ---")
for t_idx, name in [(6, "Listing 4.1"), (7, "Listing 4.2"), (8, "Listing 4.3")]:
    t = doc.tables[t_idx]
    c = t.cell(0, 0)
    fonts = set()
    sizes = set()
    for p in c.paragraphs:
        for r in p.runs:
            fonts.add(r.font.name)
            sizes.add(r.font.size.pt if r.font.size else None)
    print(f"  {name} (Table {t_idx}): {len(c.paragraphs)} lines | Fonts: {fonts} | Sizes: {sizes}")

# 8. Check Chapter Heading Line Breaks
print("\n--- Chapter Headings XML Check ---")
for p_idx in [108, 128, 147, 173, 205, 223]:
    p = doc.paragraphs[p_idx]
    has_br = "<w:br" in p._p.xml
    print(f"  P{p_idx}: '{repr(p.text)}' | Has <w:br/>: {'✓ YES' if has_br else '❌ NO'}")

# 9. Check settings updateFields
has_update_fields = "<w:updateFields" in doc.settings.element.xml
print(f"\n  Settings has <w:updateFields>: {'✓ YES' if has_update_fields else '❌ NO'}")
print("=" * 60)
