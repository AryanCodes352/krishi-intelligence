import docx

doc = docx.Document("docs/KRISHI_Intelligence_KCC_Report_FINAL.docx")

page = 1
for i, p in enumerate(doc.paragraphs):
    xml = p._p.xml
    is_pb = ('type="page"' in xml) or ('w:pageBreakBefore' in xml)
    if is_pb:
        page += 1
        print(f"PAGE BREAK -> Page {page} at P{i:03d}: {repr(p.text[:60])}")
    
    t = p.text.strip()
    if any(t.startswith(prefix) for prefix in [
        "BONAFIDE", "DECLARATION", "ACKNOWLEDGMENT", "ABSTRACT",
        "TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES",
        "CHAPTER 1", "CHAPTER 2", "CHAPTER 3", "CHAPTER 4", "CHAPTER 5", "CHAPTER 6",
        "REFERENCES"
    ]):
        print(f"  FOUND HEADING: P{i:03d} -> {repr(t[:60])} (around Page {page})")
