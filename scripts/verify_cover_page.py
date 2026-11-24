import docx

doc = docx.Document("docs/KRISHI_Intelligence_KCC_Report_FINAL.docx")

print("=== COVER PAGE PARAGRAPHS DETAIL ===")
for i in range(22):
    p = doc.paragraphs[i]
    xml = p._p.xml
    is_pb = ('type="page"' in xml) or ('w:pageBreakBefore' in xml)
    sp_a = p.paragraph_format.space_after.pt if p.paragraph_format.space_after else 0
    sp_b = p.paragraph_format.space_before.pt if p.paragraph_format.space_before else 0
    ls = p.paragraph_format.line_spacing
    has_img = "blip" in xml
    print(f"P{i:02d} [pb={is_pb}, img={has_img}] sp_b={sp_b:4.1f} sp_a={sp_a:4.1f} ls={ls}: {repr(p.text[:65])}")
    if is_pb:
        print("--- END OF PAGE 1 (PAGE BREAK FOUND) ---")
        break
