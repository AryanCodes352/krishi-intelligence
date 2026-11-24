import docx

doc = docx.Document("docs/KRISHI_Intelligence_KCC_Report_FINAL.docx")

print("=== COVER PAGE PARAGRAPHS (0 to 25) ===")
for i in range(25):
    p = doc.paragraphs[i]
    xml = p._p.xml
    has_page_break = ('w:br' in xml and 'type="page"' in xml) or ('w:pageBreakBefore' in xml)
    sp_b = p.paragraph_format.space_before
    sp_a = p.paragraph_format.space_after
    ls = p.paragraph_format.line_spacing
    print(f"P{i:02d} [pb={has_page_break}] sp_b={sp_b} sp_a={sp_a} ls={ls}: {repr(p.text)}")

print("\n=== TOC, LOT, LOF PARAGRAPHS (43 to 108) ===")
for i in range(43, 108):
    p = doc.paragraphs[i]
    print(f"P{i:02d}: {repr(p.text)}")
