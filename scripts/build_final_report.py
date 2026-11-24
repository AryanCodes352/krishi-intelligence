"""
Script to apply all 7 exact updates to KRISHI_Intelligence_KCC_Report upd_2.docx
and produce docs/KRISHI_Intelligence_KCC_Report_FINAL.docx
"""

import os
import re
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
INPUT_DOCX = os.path.join(DOCS_DIR, "KRISHI_Intelligence_KCC_Report upd_2.docx")
OUTPUT_DOCX = os.path.join(DOCS_DIR, "KRISHI_Intelligence_KCC_Report_FINAL.docx")
FIGURES_DIR = os.path.join(DOCS_DIR, "figures")

FIG_3_1_PNG = os.path.join(FIGURES_DIR, "fig_3_1_system_architecture.png")
FIG_3_2_PNG = os.path.join(FIGURES_DIR, "fig_3_2_dfd_level_0_and_1.png")


def set_cell_margins_and_borders(cell, fill_hex="F8FAFC", border_hex="CBD5E1"):
    """Applies clean padding, background shading and subtle border to a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    
    # Background Shading
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)
    
    # Cell Borders
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="{border_hex}"/>\n'
        f'  <w:left w:val="single" w:sz="12" w:space="0" w:color="10B981"/>\n'  # 1.5pt emerald left accent stripe
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{border_hex}"/>\n'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="{border_hex}"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)
    
    # Cell Margins / Padding (top/bottom: 120 dxa = 6pt, left/right: 200 dxa = 10pt)
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>\n'
        f'  <w:top w:w="140" w:type="dxa"/>\n'
        f'  <w:left w:w="220" w:type="dxa"/>\n'
        f'  <w:bottom w:w="140" w:type="dxa"/>\n'
        f'  <w:right w:w="220" w:type="dxa"/>\n'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def format_code_listing(table, code_text):
    """Formats a 1x1 table into a clean multi-line Consolas code block."""
    cell = table.cell(0, 0)
    set_cell_margins_and_borders(cell, fill_hex="F8FAFC", border_hex="CBD5E1")
    
    # Remove all existing paragraphs in cell completely
    for p in list(cell.paragraphs):
        p._p.getparent().remove(p._p)
    
    lines = code_text.strip().split("\n")
    for line in lines:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        
        run = p.add_run(line if line.strip() else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(15, 23, 42)  # Slate 900


def main():
    print(f"Loading: {INPUT_DOCX}")
    doc = Document(INPUT_DOCX)
    
    # -------------------------------------------------------------------------
    # 1. Update Front Matter Metadata (Cover Page, Bonafide, Declaration, Ack)
    # -------------------------------------------------------------------------
    print("Applying Update 1: Front Matter Metadata...")

    # Cover Page (P7 to P18)
    # P7: 'Submitted by:'
    doc.paragraphs[8].text = (
        "ARYAN (Team Lead) — University Roll No: 2404920100101\n"
        "PRABHAT KUMAR JHA — University Roll No: 2404920100240\n"
        "PRIYANSHU KUMAR — University Roll No: 2404920100259\n"
        "PRATIBHA YADAV — University Roll No: 2404920100247"
    )
    doc.paragraphs[8].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in doc.paragraphs[8].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
    
    # Clear redundant P9 ('University Roll No: 22049201000XX')
    doc.paragraphs[9].text = ""
    
    # P10: 'B.Tech 3rd Year, Semester VI' -> 'B.Tech 3rd Year, Semester V'
    doc.paragraphs[10].text = "B.Tech 3rd Year, Semester V"
    doc.paragraphs[10].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in doc.paragraphs[10].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = False

    # P12: Faculty Guide Name
    doc.paragraphs[12].text = "Mr. Chand Babu"
    doc.paragraphs[12].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in doc.paragraphs[12].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True

    # P18: Session
    doc.paragraphs[18].text = "ACADEMIC SESSION: 2026–2027"
    doc.paragraphs[18].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in doc.paragraphs[18].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True

    # Bonafide Certificate (P24, P25, Table 0)
    doc.paragraphs[24].text = (
        'This is to certify that the Mini-Project Report entitled "KRISHI INTELLIGENCE: '
        'Multi-Factor Agro-Climatic Digital Twin with Dynamic Provenance Guardrails and Market Price Forecasting", '
        'submitted by Aryan (University Roll No: 2404920100101), Prabhat Kumar Jha (University Roll No: 2404920100240), '
        'Priyanshu Kumar (University Roll No: 2404920100259), and Pratibha Yadav (University Roll No: 2404920100247) '
        'in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer '
        'Science and Engineering from KCC Institute of Technology and Management (CC 492), Greater Noida, affiliated to '
        'Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow, is a bonafide record of original work carried out '
        'under our supervision and guidance during the academic session 2026–2027.'
    )
    doc.paragraphs[24].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in doc.paragraphs[24].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    # Table 0: Certificate Signatures
    t0 = doc.tables[0]
    t0.cell(0, 0).text = (
        "______________________________\n"
        "Mr. Chand Babu\n"
        "Project Guide / Supervisor\n"
        "Assistant Professor, Dept. of CSE\n"
        "KCC ITM, Greater Noida"
    )
    for p in t0.cell(0, 0).paragraphs:
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)

    t0.cell(0, 1).text = (
        "______________________________\n"
        "Mr. Chetan Khemraj\n"
        "Head of Department\n"
        "Professor & HOD, Dept. of CSE\n"
        "KCC ITM, Greater Noida"
    )
    for p in t0.cell(0, 1).paragraphs:
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)

    # Declaration (P27, P28, P29)
    doc.paragraphs[27].text = (
        'We hereby declare that this Mini-Project Report entitled "KRISHI INTELLIGENCE: '
        'Multi-Factor Agro-Climatic Digital Twin with Dynamic Provenance Guardrails and Market Price Forecasting" '
        'is an authentic record of our own research and development work carried out at KCC Institute of Technology '
        'and Management, Greater Noida, under the guidance of Mr. Chand Babu, Assistant Professor, '
        'Department of Computer Science and Engineering.'
    )
    doc.paragraphs[27].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in doc.paragraphs[27].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    doc.paragraphs[28].text = (
        'We further declare that this report has not been submitted previously to any other university or '
        'institution for the award of any degree or diploma. All sources of literature, datasets, APIs, and '
        'software libraries utilized during the development of this project have been duly cited and acknowledged.'
    )
    doc.paragraphs[28].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in doc.paragraphs[28].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    doc.paragraphs[29].text = (
        "Aryan (Roll No: 2404920100101)\n"
        "Prabhat Kumar Jha (Roll No: 2404920100240)\n"
        "Priyanshu Kumar (Roll No: 2404920100259)\n"
        "Pratibha Yadav (Roll No: 2404920100247)\n"
        "B.Tech CSE, 3rd Year (V Semester)\n"
        "KCC Institute of Technology and Management, Greater Noida"
    )
    doc.paragraphs[29].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in doc.paragraphs[29].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)

    # Acknowledgment (P32 to P36)
    doc.paragraphs[32].text = (
        "We express our deepest gratitude and sincere thanks to our respected Director and to Mr. Chetan Khemraj, "
        "Head of the Department of Computer Science and Engineering, KCC Institute of Technology and Management, "
        "for providing state-of-the-art laboratory infrastructure, computational facilities, and an encouraging "
        "academic environment that fostered the conceptualization and development of this project."
    )
    doc.paragraphs[32].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in doc.paragraphs[32].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    doc.paragraphs[33].text = (
        "We are profoundly indebted to our project supervisor, Mr. Chand Babu, Assistant Professor, "
        "Department of Computer Science and Engineering, for their invaluable guidance, constructive criticism, "
        "constant motivation, and intellectual mentorship throughout the stages of system architectural design, "
        "algorithm formulation, implementation, and empirical verification."
    )
    doc.paragraphs[33].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in doc.paragraphs[33].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    doc.paragraphs[34].text = (
        "We also extend our sincere appreciation to all faculty members, technical lab assistants, and "
        "administrative staff of the Department of Computer Science and Engineering for their continuous "
        "support and cooperation."
    )
    doc.paragraphs[34].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in doc.paragraphs[34].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    doc.paragraphs[35].text = (
        "Finally, we express our heartfelt indebtedness to our parents, family members, and peers for their "
        "unyielding encouragement, patience, and inspiration, without which the successful completion of this "
        "B.Tech Mini-Project would not have been possible."
    )
    doc.paragraphs[35].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in doc.paragraphs[35].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    doc.paragraphs[36].text = (
        "Aryan • Prabhat Kumar Jha • Priyanshu Kumar • Pratibha Yadav\n"
        "B.Tech CSE, 3rd Year (V Semester)"
    )
    doc.paragraphs[36].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in doc.paragraphs[36].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True

    # -------------------------------------------------------------------------
    # 2. Swap Fig. 3.1 & Fig. 3.2 with Fixed Diagram PNGs
    # -------------------------------------------------------------------------
    print("Applying Update 2: Swapping Fig 3.1 and Fig 3.2 PNGs...")
    with open(FIG_3_1_PNG, "rb") as f:
        doc.part.rels["rId10"].target_part._blob = f.read()
    print(f"  Swapped Fig 3.1 (rId10) with {FIG_3_1_PNG}")

    with open(FIG_3_2_PNG, "rb") as f:
        doc.part.rels["rId11"].target_part._blob = f.read()
    print(f"  Swapped Fig 3.2 (rId11) with {FIG_3_2_PNG}")

    # -------------------------------------------------------------------------
    # 3. Swap Table 5.1 & Table 5.2 Ordering (List of Tables & Chapter 5)
    # -------------------------------------------------------------------------
    print("Applying Update 3: Swapping Table 5.1 & Table 5.2 Ordering...")
    # List of Tables (P93 & P94)
    doc.paragraphs[93].text = "Table 5.1: Comprehensive Automated Test Suite Execution Matrix (Pytest Suite)  . . 33"
    for r in doc.paragraphs[93].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)

    doc.paragraphs[94].text = "Table 5.2: Mandi Price Prediction Quantitative Performance Metrics  . . 35"
    for r in doc.paragraphs[94].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)

    # Chapter 5 Prose & Captions
    # P207: "As detailed in Table 5.2..." -> "As detailed in Table 5.1..."
    doc.paragraphs[207].text = (
        "The system incorporates an extensive automated test suite implemented in pytest and pytest-asyncio. "
        "The test suite contains 116 tests covering all API endpoints, digital twin state transitions, "
        "provenance classifications, and the OCR confirmation gate. As detailed in Table 5.1, all 116 tests "
        "pass with 100% success rate."
    )
    for r in doc.paragraphs[207].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    # P208: Table Caption
    doc.paragraphs[208].text = "Table 5.1: Comprehensive Automated Test Suite Execution Matrix (Pytest Suite)"
    for r in doc.paragraphs[208].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True

    # P211: "As documented in Table 5.1..." -> "As documented in Table 5.2..."
    doc.paragraphs[211].text = (
        "The XGBoost Regressor was trained on historical AGMARKNET daily modal prices for Wheat in Lucknow Mandi "
        "(2021–2024, 1,460 observations) and evaluated on a held-out test split of 90 days. As documented in "
        "Table 5.2 and Fig. 5.1(a), the model achieved a Mean Absolute Error of ₹84.30/quintal (MAPE of 3.82%) "
        "and an R² of 0.887, demonstrating strong predictive accuracy within the APMC market context."
    )
    for r in doc.paragraphs[211].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    # P212: Table Caption
    doc.paragraphs[212].text = "Table 5.2: Mandi Price Prediction Quantitative Performance Metrics"
    for r in doc.paragraphs[212].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True

    # -------------------------------------------------------------------------
    # 4. Align Fig. 4.4 Caption with Screenshot Content (Section 4.6 & List of Figures)
    # -------------------------------------------------------------------------
    print("Applying Update 4: Aligning Fig 4.4 Caption...")
    # List of Figures (P103)
    doc.paragraphs[103].text = (
        "Fig. 4.4: Granular Soil Intelligence Center Showing ICAR-NBSS&LUP Regional Baseline, "
        "Nutrient Evaluations, and Suitability Score  . . 31"
    )
    for r in doc.paragraphs[103].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)

    # Section 4.6 (P199)
    doc.paragraphs[199].text = (
        "Fig. 4.4: Granular Soil Intelligence Center Showing ICAR-NBSS&LUP Regional Baseline, "
        "Nutrient Evaluations, and Suitability Score"
    )
    for r in doc.paragraphs[199].runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.bold = True

    # -------------------------------------------------------------------------
    # 5. Format Python Code Listings (Listing 4.1, 4.2, 4.3)
    # -------------------------------------------------------------------------
    print("Applying Update 5: Formatting Python Code Listings...")
    
    code_listing_4_1 = (
        "def get_crop_stage(crop: str, days_after_sowing: int) -> str:\n"
        "    if crop.lower() == 'wheat':\n"
        "        if days_after_sowing <= 10:\n"
        "            return 'Germination'\n"
        "        if days_after_sowing <= 25:\n"
        "            return 'Seedling'\n"
        "        if days_after_sowing <= 45:\n"
        "            return 'Tillering'\n"
        "        if days_after_sowing <= 65:\n"
        "            return 'Jointing'\n"
        "        if days_after_sowing <= 80:\n"
        "            return 'Booting'\n"
        "        if days_after_sowing <= 90:\n"
        "            return 'Heading/Flowering'\n"
        "        if days_after_sowing <= 115:\n"
        "            return 'Grain Filling'\n"
        "        if days_after_sowing <= 140:\n"
        "            return 'Maturity'\n"
        "        return 'Post-harvest'\n"
        "    return 'Unknown'"
    )
    format_code_listing(doc.tables[6], code_listing_4_1)

    code_listing_4_2 = (
        "# Freshness thresholds for AGMARKNET observation classification\n"
        "LIVE_THRESHOLD_DAYS = 1              # <= 1 day old  -> LIVE\n"
        "LATEST_AVAILABLE_THRESHOLD_DAYS = 7  # 2 to 7 days   -> LATEST_AVAILABLE\n"
        "# > 7 days old -> STALE; triggers fallback to HISTORICAL_SEED\n"
        "\n"
        "def classify_mandi_provenance(record_date: date) -> str:\n"
        "    age_days = (date.today() - record_date).days\n"
        "    if age_days <= LIVE_THRESHOLD_DAYS:\n"
        "        return 'LIVE'\n"
        "    elif age_days <= LATEST_AVAILABLE_THRESHOLD_DAYS:\n"
        "        return 'LATEST_AVAILABLE'\n"
        "    else:\n"
        "        return 'STALE'"
    )
    format_code_listing(doc.tables[7], code_listing_4_2)

    code_listing_4_3 = (
        "@router.post('/confirm', response_model=SoilProfileResponse)\n"
        "def confirm_soil_profile(payload: SoilConfirmationRequest, db: Session = Depends(get_db)):\n"
        "    farm = db.query(Farm).filter(Farm.id == payload.farm_id).first()\n"
        "    if not farm:\n"
        "        raise HTTPException(status_code=404, detail='Farm not found')\n"
        "\n"
        "    # Validate physical chemical feasibility constraints\n"
        "    ph = payload.parameters.get('ph')\n"
        "    if ph is not None and (ph < 0.0 or ph > 14.0):\n"
        "        raise HTTPException(status_code=400, detail='Invalid pH. Must be 0.0-14.0')\n"
        "\n"
        "    # Set immutable provenance tag based on origin authority\n"
        "    profile_prov = 'SOIL_HEALTH_CARD' if payload.document_id else 'FARMER_ENTERED'\n"
        "\n"
        "    # Deactivate previous active profiles (preserve historical audit trail)\n"
        "    db.query(FarmSoilProfile).filter(FarmSoilProfile.farm_id == payload.farm_id).update({'is_active': False})\n"
        "\n"
        "    # Commit new verified soil profile to persistent store\n"
        "    new_profile = FarmSoilProfile(farm_id=payload.farm_id, provenance=profile_prov, is_active=True, ...)\n"
        "    db.add(new_profile)\n"
        "    db.commit()\n"
        "    return new_profile"
    )
    format_code_listing(doc.tables[8], code_listing_4_3)

    # -------------------------------------------------------------------------
    # 6. Ensure Chapter Heading Line Breaks (CHAPTER 1 through CHAPTER 6)
    # -------------------------------------------------------------------------
    print("Applying Update 6: Verifying Chapter Heading Line Breaks...")
    chapter_titles = [
        (108, "CHAPTER 1", "INTRODUCTION"),
        (128, "CHAPTER 2", "SYSTEM SPECIFICATIONS & REQUIREMENTS"),
        (147, "CHAPTER 3", "DESIGN / METHODOLOGY / ARCHITECTURE"),
        (173, "CHAPTER 4", "IMPLEMENTATION / CODING SNAPSHOTS"),
        (205, "CHAPTER 5", "TESTING, RESULTS & ANALYSIS"),
        (223, "CHAPTER 6", "CONCLUSION & FUTURE SCOPE"),
    ]

    for p_idx, ch_label, ch_title in chapter_titles:
        p = doc.paragraphs[p_idx]
        p.text = ""  # Clear text and rebuild with explicit <w:br/>
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        r1 = p.add_run(ch_label)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(16)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(30, 41, 59)
        
        # Add explicit Word XML break
        br_elem = OxmlElement('w:br')
        r1._r.append(br_elem)
        
        r2 = p.add_run(ch_title)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(14)
        r2.font.bold = True
        r2.font.color.rgb = RGBColor(30, 41, 59)

    # -------------------------------------------------------------------------
    # 7. Mark TOC Field Dirty & Update Fields in Settings
    # -------------------------------------------------------------------------
    print("Applying Update 7: Marking TOC / Fields as Dirty...")
    # Enable updateFields in word/settings.xml
    settings_element = doc.settings.element
    update_fields = OxmlElement('w:updateFields')
    update_fields.set(qn('w:val'), 'true')
    settings_element.append(update_fields)

    # Mark any fldSimple or fldChar in body as dirty
    for elem in doc._body._element.iter():
        tag = elem.tag.split('}')[-1]
        if tag in ['fldSimple', 'fldChar']:
            elem.set(qn('w:dirty'), 'true')

    # Save to final output
    print(f"Saving final report to: {OUTPUT_DOCX}")
    doc.save(OUTPUT_DOCX)
    print("Document successfully saved!")


if __name__ == "__main__":
    main()
