"""
Script to apply:
1. KCC Institutes Logo on Cover Page with tuned spacing so Page 1 never spills.
2. Word tab stops with WD_TAB_LEADER.DOTS at Inches(6.5) on TOC, List of Tables, List of Figures.
"""

import os
import re
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DOCX_PATH = os.path.join(DOCS_DIR, "KRISHI_Intelligence_KCC_Report_FINAL.docx")
LOGO_PATH = os.path.join(DOCS_DIR, "kcc_logo.png")


def update_cover_page(doc):
    print("Updating Cover Page...")
    
    # Check if logo is already inserted
    already_has_logo = False
    for p in doc.paragraphs[:15]:
        if "blip" in p._p.xml:
            already_has_logo = True
            break
            
    if not already_has_logo:
        # Find paragraph with "Submitted by:"
        submitted_by_idx = None
        for i, p in enumerate(doc.paragraphs[:15]):
            if p.text.strip().lower() == "submitted by:":
                submitted_by_idx = i
                break
                
        if submitted_by_idx is not None:
            # Insert logo paragraph before "Submitted by:"
            p_logo = doc.paragraphs[submitted_by_idx].insert_paragraph_before()
            p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_logo.paragraph_format.space_before = Pt(3)
            p_logo.paragraph_format.space_after = Pt(8)
            p_logo.paragraph_format.line_spacing = 1.0
            run = p_logo.add_run()
            run.add_picture(LOGO_PATH, width=Inches(1.45))
            print("  Inserted KCC Logo before 'Submitted by:' (width=1.45 inches)")
    else:
        print("  Cover page already has logo image.")

    # Remove any empty paragraphs between students and Semester/Supervisor
    # Find cover page range (up to the first page break)
    cover_end_idx = None
    for i, p in enumerate(doc.paragraphs[:25]):
        xml = p._p.xml
        if ('type="page"' in xml) or ('w:pageBreakBefore' in xml):
            cover_end_idx = i
            break
            
    # Iterate through cover page paragraphs and adjust spacing
    # Re-scan cover paragraphs
    cover_paras = doc.paragraphs[:cover_end_idx]
    
    # First, delete any completely empty paragraphs before the page break
    to_remove = []
    for i, p in enumerate(cover_paras):
        if not p.text.strip() and "blip" not in p._p.xml:
            to_remove.append(p)
    for p in to_remove:
        p._p.getparent().remove(p._p)
        print("  Removed empty paragraph from cover page.")

    # Now re-fetch cover paragraphs and set compact, elegant spacing
    # Find new cover_end_idx
    for i, p in enumerate(doc.paragraphs[:25]):
        xml = p._p.xml
        if ('type="page"' in xml) or ('w:pageBreakBefore' in xml):
            cover_end_idx = i
            break

    for i in range(cover_end_idx):
        p = doc.paragraphs[i]
        t = p.text.strip()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        
        if "blip" in p._p.xml:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.0
        elif t.startswith("KRISHI INTELLIGENCE"):
            p.paragraph_format.space_after = Pt(3)
        elif t.startswith("Multi-Factor Agro-Climatic"):
            p.paragraph_format.space_after = Pt(10)
        elif t.startswith("A MINI-PROJECT REPORT"):
            p.paragraph_format.space_after = Pt(3)
        elif t.startswith("Submitted in partial"):
            p.paragraph_format.space_after = Pt(2)
        elif t.startswith("BACHELOR OF TECHNOLOGY"):
            p.paragraph_format.space_after = Pt(1)
        elif t == "IN":
            p.paragraph_format.space_after = Pt(1)
        elif t.startswith("COMPUTER SCIENCE"):
            p.paragraph_format.space_after = Pt(8)
        elif t.startswith("Submitted by:"):
            p.paragraph_format.space_after = Pt(2)
        elif t.startswith("ARYAN"):
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.1
        elif t.startswith("B.Tech 3rd Year, Semester V"):
            p.paragraph_format.space_after = Pt(6)
        elif t.startswith("Under the Supervision"):
            p.paragraph_format.space_after = Pt(1)
        elif t.startswith("Mr. Chand Babu"):
            p.paragraph_format.space_after = Pt(1)
        elif t.startswith("Assistant Professor"):
            p.paragraph_format.space_after = Pt(8)
        elif t.startswith("DEPARTMENT OF COMPUTER SCIENCE"):
            p.paragraph_format.space_after = Pt(1)
        elif t.startswith("KCC INSTITUTE OF TECHNOLOGY"):
            p.paragraph_format.space_after = Pt(1)
        elif t.startswith("(Affiliated to Dr."):
            p.paragraph_format.space_after = Pt(1)
        elif t.startswith("Knowledge Park III"):
            p.paragraph_format.space_after = Pt(2)
        elif t.startswith("ACADEMIC SESSION"):
            p.paragraph_format.space_after = Pt(0)
            
    print("  Cover page spacing tuned successfully.")


def update_toc_tabs(doc):
    print("Updating Table of Contents, List of Tables, List of Figures with Tab Stops...")
    
    # Regex to match: (title) + (dots/spaces) + (page_num)
    pattern = re.compile(r"^(.*?)(?:\s+(?:\.\s*)+|\s*\.{2,}\s*|\s{3,})([ivx0-9]+)$", re.IGNORECASE)
    
    # Locate range from "TABLE OF CONTENTS" to "CHAPTER 1"
    start_idx = None
    end_idx = None
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t == "TABLE OF CONTENTS":
            start_idx = i + 1
        elif t.startswith("CHAPTER 1"):
            end_idx = i
            break
            
    if start_idx is None or end_idx is None:
        print("  ❌ Could not find TOC section boundaries.")
        return
        
    print(f"  TOC/LOT/LOF range: Paragraphs {start_idx} to {end_idx}")
    
    converted_count = 0
    for i in range(start_idx, end_idx):
        p = doc.paragraphs[i]
        raw_text = p.text.strip()
        if not raw_text or raw_text.startswith("LIST OF"):
            continue
            
        m = pattern.match(raw_text)
        if m:
            title = m.group(1).rstrip()
            page = m.group(2).strip()
            
            # Determine styling hierarchy
            is_main_heading = (
                title.strip().startswith("Chapter ") or
                title.strip() in [
                    "Bonafide Certificate", "Declaration", "Acknowledgment",
                    "Abstract / Synopsis", "List of Tables", "List of Figures",
                    "References / Bibliography"
                ]
            )
            
            # Clear text
            p.text = ""
            
            # Clear existing tab stops and add standard right tab stop with dotted leader at 6.5 inches
            p.paragraph_format.tab_stops.clear_all()
            p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2.5)
            p.paragraph_format.line_spacing = 1.15
            
            r_title = p.add_run(title)
            r_title.font.name = "Times New Roman"
            r_title.font.size = Pt(10.5)
            r_title.font.bold = is_main_heading
            r_title.font.color.rgb = RGBColor(15, 23, 42)
            
            r_tab = p.add_run("\t")
            
            r_page = p.add_run(page)
            r_page.font.name = "Times New Roman"
            r_page.font.size = Pt(10.5)
            r_page.font.bold = is_main_heading
            r_page.font.color.rgb = RGBColor(15, 23, 42)
            
            converted_count += 1
        else:
            print(f"  Warning: unmatched line P{i}: {repr(raw_text)}")
            
    print(f"  Successfully converted {converted_count} entries to native Word tab stops with dotted leaders.")


def main():
    print(f"Loading document: {DOCX_PATH}")
    doc = Document(DOCX_PATH)
    
    update_cover_page(doc)
    update_toc_tabs(doc)
    
    print(f"Saving updated document: {DOCX_PATH}")
    doc.save(DOCX_PATH)
    print("Done!")


if __name__ == "__main__":
    main()
