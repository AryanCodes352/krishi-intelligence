import docx
import re
import os

doc = docx.Document("docs/KRISHI_Intelligence_KCC_Report upd_2.docx")

print("Total paragraphs:", len(doc.paragraphs))
print("Total tables:", len(doc.tables))

for i, p in enumerate(doc.paragraphs):
    xml = p._p.xml
    if "blip" in xml:
        embeds = re.findall(r'embed="([^"]+)"', xml)
        caption = ""
        if i + 1 < len(doc.paragraphs):
            caption = doc.paragraphs[i+1].text.strip()
        print(f"Paragraph {i} has image(s): {embeds} | Next text: {caption}")
        for eid in embeds:
            part = doc.part.rels[eid].target_part
            print(f"  relId: {eid}, target: {doc.part.rels[eid].target_ref}, part size: {len(part.blob)}")
