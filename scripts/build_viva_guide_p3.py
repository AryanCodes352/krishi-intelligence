"""
scripts/build_viva_guide_p3.py
Generates the comprehensive Academic Viva & Presentation Guide for Person 3
(Vision & Methodology Engineer — Soil Health Card OCR, Confirmation Gate, SRS & Diagrams).
Document output: docs/viva_guides/Person_3_OCR_Confirmation_and_Methodology_Guide.docx
Strictly formatted according to academic guidelines using python-docx.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "docs", "viva_guides")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_DOCX = os.path.join(OUTPUT_DIR, "Person_3_OCR_Confirmation_and_Methodology_Guide.docx")


def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell padding in twips (1 pt = 20 twips)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def set_cell_left_border_only(cell, color_hex="1E3A8A", sz="36"):
    """Set a thick left border for callout boxes while clearing top, bottom, and right."""
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color_hex}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tc_pr.append(borders)


def add_page_number(run):
    """Insert a dynamic PAGE field."""
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)


def build_guide():
    print("Building Person 3 OCR, Confirmation Gate & Methodology Guide...")
    doc = Document()

    # Page Margins: A4, 1.25" Left (binding), 1" Right, Top, Bottom
    for sec in doc.sections:
        sec.page_width = Inches(8.27)
        sec.page_height = Inches(11.69)
        sec.left_margin = Inches(1.25)
        sec.right_margin = Inches(1.0)
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)

        # Header
        hdr = sec.header
        p_hdr = hdr.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("KRISHI Intelligence — Academic Viva Guide | Person 3 (OCR, Gate & Methodology)")
        r_hdr.font.name = "Times New Roman"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.color.rgb = RGBColor(148, 163, 184)

        # Footer
        ftr = sec.footer
        p_ftr = ftr.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ftr = p_ftr.add_run("Page ")
        r_ftr.font.name = "Times New Roman"
        r_ftr.font.size = Pt(9.5)
        r_ftr.font.color.rgb = RGBColor(100, 116, 139)
        add_page_number(r_ftr)

    # Styles
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Times New Roman'
    font_normal.size = Pt(12)
    font_normal.color.rgb = RGBColor(15, 23, 42)
    style_normal.paragraph_format.line_spacing = 1.25
    style_normal.paragraph_format.space_after = Pt(6)

    def add_p(text, bold=False, italic=False, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, space_before=0, color=RGBColor(15, 23, 42)):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(space_before)
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
        run.font.color.rgb = color
        return p

    def add_h1(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(15)
        run.font.color.rgb = RGBColor(30, 58, 138)  # Navy Blue
        return p

    def add_h2(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_h3(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.bold = True
        run.italic = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(71, 85, 105)
        return p

    def add_callout(text, label="SPEAKER DIRECTIVE / EXAMINER ALERT", border_hex="1E3A8A", bg_hex="EFF6FF"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.rows[0].cells[0]
        cell.width = Inches(6.0)
        set_cell_background(cell, bg_hex)
        set_cell_left_border_only(cell, color_hex=border_hex, sz="36")
        set_cell_margins(cell, top=120, bottom=120, left=180, right=140)

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.2

        if label:
            r_lbl = p.add_run(f"[{label}]\n")
            r_lbl.bold = True
            r_lbl.font.name = 'Times New Roman'
            r_lbl.font.size = Pt(10)
            r_lbl.font.color.rgb = RGBColor(30, 58, 138)

        r_body = p.add_run(text)
        r_body.italic = True
        r_body.font.name = 'Times New Roman'
        r_body.font.size = Pt(10.5)
        r_body.font.color.rgb = RGBColor(15, 23, 42)

        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_after = Pt(4)
        p_sp.paragraph_format.space_before = Pt(0)

    def add_table_data(title, headers, data, col_widths=None):
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_cap.paragraph_format.space_before = Pt(10)
        p_cap.paragraph_format.space_after = Pt(4)
        p_cap.paragraph_format.keep_with_next = True
        run_cap = p_cap.add_run(title)
        run_cap.bold = True
        run_cap.font.name = 'Times New Roman'
        run_cap.font.size = Pt(11)
        run_cap.font.color.rgb = RGBColor(30, 41, 59)

        table = doc.add_table(rows=len(data) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        # Header Row
        hdr_cells = table.rows[0].cells
        for i, h_text in enumerate(headers):
            hdr_cells[i].text = h_text
            set_cell_background(hdr_cells[i], "1E3A8A")
            set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            for r in p.runs:
                r.bold = True
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(255, 255, 255)

        # Data Rows
        for r_idx, row_values in enumerate(data):
            row_cells = table.rows[r_idx + 1].cells
            bg_col = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
            for c_idx, val in enumerate(row_values):
                row_cells[c_idx].text = str(val)
                set_cell_background(row_cells[c_idx], bg_col)
                set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
                p = row_cells[c_idx].paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                if c_idx == 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(9.5)
                    r.font.color.rgb = RGBColor(15, 23, 42)

        if col_widths:
            for row in table.rows:
                for idx, w in enumerate(col_widths):
                    row.cells[idx].width = Inches(w)

        p_post = doc.add_paragraph()
        p_post.paragraph_format.space_before = Pt(0)
        p_post.paragraph_format.space_after = Pt(6)

    # =========================================================================
    # DOCUMENT COVER / TITLE HEADER
    # =========================================================================
    add_p("KCC INSTITUTE OF TECHNOLOGY AND MANAGEMENT, GREATER NOIDA", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(30, 58, 138))
    add_p("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(71, 85, 105))
    add_p("B.Tech 3rd Year (Semester VI) — Mini-Project Academic Viva Defense Guide (Session 2025–2026)", italic=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(6)
    title_p.paragraph_format.space_after = Pt(4)
    run_t = title_p.add_run("KRISHI INTELLIGENCE")
    run_t.bold = True
    run_t.font.name = 'Times New Roman'
    run_t.font.size = Pt(20)
    run_t.font.color.rgb = RGBColor(30, 58, 138)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(14)
    run_sub = sub_p.add_run("PERSON 3 MASTER PLAYBOOK: SOIL HEALTH CARD OCR, CONFIRMATION GATE & METHODOLOGY")
    run_sub.bold = True
    run_sub.font.name = 'Times New Roman'
    run_sub.font.size = Pt(12)
    run_sub.font.color.rgb = RGBColor(217, 119, 6)

    add_callout(
        "THIS PLAYBOOK IS EXCLUSIVELY FOR PERSON 3. Your assigned responsibility covers:\n"
        "1. Engineering Pillar: Soil Health Card OCR Pipeline & Human-in-the-Loop Confirmation Gate (Image/PDF parsing, nutrient extraction "
        "for N, P, K, pH, EC, Organic Carbon, physical sanity bounds, and the locked farmer-review quarantine).\n"
        "2. Documentation Pillar: Software Requirements Specification (SRS), System Methodology & Architecture Diagrams "
        "(Chapter 2: Hardware/Software specs, Functional & Non-Functional requirements; Chapter 3: Fig 3.2 DFD Level 0 & Level 1, "
        "and Fig 3.4 Procedural Sequence Diagram).\n\n"
        "This guide provides every detail, code pointer, and defense answer so you can explain every diagram, formula, and safety invariant "
        "with complete academic authority in 20 minutes.",
        label="PERSON 3 OWNERSHIP CHARTER",
        border_hex="D97706",
        bg_hex="FEF3C7"
    )

    # =========================================================================
    # SECTION 1: ROLE & OWNERSHIP MATRIX
    # =========================================================================
    add_h1("1. Role & Ownership Matrix (Person 3)")

    add_p(
        "In our 4-member project defense for KRISHI Intelligence, Person 3 bridges the gap between raw document vision and life-critical "
        "agronomic safety. While Person 1 introduces the system architecture and Person 2 explains the weather and XGBoost price forecaster, "
        "you own the critical Soil Health Card digitization pipeline, the Human-in-the-Loop safety barrier, and the formal software engineering "
        "methodology diagrams (DFD and Sequence designs)."
    )

    role_table = [
        ["Person 1 (Aryan)", "Lead Architect & Live Demo", "Slides 1–3, Slide 11, Live Demo", "System Architecture, Multi-Agent Risk Engine, Chapter 1 & Synopsis Compilation"],
        ["Person 2", "Data & ML Engineer", "Slides 4–5, ML Viva Defense", "Open-Meteo Telemetry, AGMARKNET Pipelines, XGBoost Forecaster, Chapter 5 Metrics"],
        ["Person 3 (You)", "Vision & Methodology", "Slides 6–7, Methodology Viva", "Soil Health Card OCR, Mandatory Review Gate, Chapter 2 SRS, Chapter 3 DFD & Sequence"],
        ["Person 4", "Database & QA Engineer", "Slides 8–10, QA Viva Defense", "3NF Relational ER Schema, 4-Tier Provenance Engine, 116 Pytest Suite, Limitations/Roadmap"]
    ]
    add_table_data("Table 1.1: 4-Member Team Ownership Matrix & Presentation Handoffs",
                   ["Team Member", "Role Title", "Presentation Ownership", "Technical & Documentation Deliverables"],
                   role_table, col_widths=[1.2, 1.4, 1.4, 2.0])

    add_h2("1.1 Presentation Coordination & Handoff Protocols")
    add_p(
        "You participate in two vital stage handoffs during our 10-minute presentation:"
    )

    add_callout(
        "HOW YOU RECEIVE THE STAGE (From Person 2):\n"
        "Person 2 will conclude Slide 5 (XGBoost Price Forecasting) by stating:\n"
        "\"While our price model accurately predicts market trends, an agricultural decision system cannot succeed without verified, "
        "ground-level soil chemistry. I now hand over the presentation to Person 3 to explain our Soil Health Card OCR pipeline "
        "and human-in-the-loop confirmation gate.\"\n\n"
        "YOUR IMMEDIATE RESPONSE (Step forward, acknowledge Person 2, and address the panel):\n"
        "\"Thank you, Person 2. Respected external examiners and faculty members: In precision agriculture, an unverified or hallucinated "
        "chemical recommendation can burn a farmer's crop and permanently degrade the soil. I will now explain our computer vision pipeline, "
        "our zero-hallucination confirmation gate, and our software design methodology.\"",
        label="HANDOFF INGESTION PROTOCOL",
        border_hex="2563EB",
        bg_hex="EFF6FF"
    )

    add_callout(
        "HOW YOU PASS THE STAGE (To Person 4):\n"
        "After concluding your walkthrough of Slide 7 (DFD & Sequence Design), look towards Person 4 and announce:\n"
        "\"Now that we have examined how external soil documents are parsed and validated into verified state vectors, "
        "I pass the presentation to Person 4 to walk through our 3NF Relational Database Schemas, our Data Provenance Engine, "
        "and our 116-test automated verification suite.\"",
        label="HANDOFF DISPATCH PROTOCOL",
        border_hex="7C3AED",
        bg_hex="F5F3FF"
    )

    # =========================================================================
    # SECTION 2: WORD-FOR-WORD PRESENTATION SPEECH (SLIDES 6 & 7)
    # =========================================================================
    add_h1("2. Word-for-Word Spoken Presentation Script (~2.5 Minutes)")

    add_p(
        "Practice this script out loud until your verbal delivery is confident, punchy, and timed to exactly 2 minutes and 30 seconds."
    )

    add_h2("Part A: Slide 6 — Soil Health Card OCR & Mandatory Confirmation Gate (~75 Seconds)")
    add_callout(
        "[SLIDE CHANGE TO SLIDE 6: Soil Health Card OCR & Mandatory Farmer Confirmation Gate]\n\n"
        "[PAUSE 2 SECONDS — MAKE EYE CONTACT WITH EXAMINERS]\n\n"
        "\"Respected examiners, India's Ministry of Agriculture has distributed over 230 million Soil Health Cards, yet less than 15% of smallholder "
        "farmers follow their recommended dosages due to complex laboratory nomenclature.\n\n"
        "To bridge this gap, we engineered an intelligent document digitization pipeline. As illustrated in the 4-step workflow at the top of Slide 6:\n"
        "In Step 1, the farmer uploads a physical Soil Health Card as a PDF, JPEG, or PNG from their mobile phone.\n"
        "In Step 2, our backend validates file magic bytes, enforces a 10MB limit, and triggers our hybrid OCR engine—using pypdf for digital PDFs "
        "and PyTesseract for camera scans. Our regex parser extracts 12 distinct soil chemical metrics: pH, Electrical Conductivity, Organic Carbon, "
        "primary nutrients Nitrogen, Phosphorus, Potassium, and secondary micronutrients like Sulphur and Zinc.\n\n"
        "However, here lies our most critical safety engineering principle: Step 3 — THE LOCKED REVIEW GATE.\n"
        "In precision agronomy, a computer vision digit misread—such as reading 24 kg/ha of Nitrogen as 240 kg/ha—can lead to catastrophic over-fertilization, "
        "burning the crop and causing severe input debt. Therefore, our system strictly enforces an architectural invariant: Raw OCR outputs are NEVER "
        "written directly to the farm database, and downstream fertilizer engines are strictly locked.\n\n"
        "The farmer is presented with an interactive review modal where every detected nutrient is displayed alongside physical sanity bounds and "
        "its confidence status. The farmer can verify or manually correct any misread digit. Only when the farmer explicitly clicks 'Confirm Soil Profile' "
        "is the active digital twin upgraded in Step 4 from REGIONAL_BASELINE to VERIFIED_LAB_TEST under an immutable audit event.\n\n"
        "Furthermore, as proven by our adversarial stress tests in the bottom-right card, uploading corrupted scans or cartoon images safely triggers "
        "'OCR FAILED' and falls back to a clean manual entry form, preventing 500 server crashes and maintaining true FARMER_ENTERED provenance.\"",
        label="SLIDE 6 SPOKEN SCRIPT",
        border_hex="D97706",
        bg_hex="FEF3C7"
    )

    add_h2("Part B: Slide 7 — System Methodology: DFD & Sequence Design (~75 Seconds)")
    add_callout(
        "[SLIDE CHANGE TO SLIDE 7: System Methodology: Data Flow & Interactive Sequence Design]\n\n"
        "[PAUSE 2 SECONDS — POINT TOWARDS THE DIAGRAMS]\n\n"
        "\"Moving to Slide 7, we present the formal software design methodology that governs our platform, as documented in Chapter 3 of our report.\n\n"
        "On the left, Figure 3.2 illustrates our Data Flow Diagrams. In Figure 3.2(a), our Level 0 Context Diagram establishes the systemic boundaries "
        "between three external entities—the Farmer, the Open-Meteo Weather Service, and the AGMARKNET Mandi Portal—and the centralized KRISHI engine.\n\n"
        "In Figure 3.2(b), our Level 1 Decomposed DFD details how information moves between five core computational processes and five persistent data stores:\n"
        "- Process 1.0 continuously ingests weather telemetry into Data Store D1: Weather Cache.\n"
        "- Process 2.0 ingests Soil Health Cards, enforces our confirmation gate, and writes verified parameters into Data Store D2: Soil Profiles.\n"
        "- Process 3.0 queries daily mandi prices and stores them in Data Store D3: Mandi Cache.\n"
        "- Process 4.0 fuses these streams into our Living Digital Twin, persisted in Data Store D4: Farm State.\n"
        "- And Process 5.0 executes our risk synthesis engine to write immutable advisories into Data Store D5: Advisory Ledger.\n\n"
        "On the right, Figure 3.4 captures the complete chronological sequence of our Human-in-the-Loop safety barrier:\n"
        "When a card is uploaded via the Next.js UI, the FastAPI backend processes the document, stores it with status PENDING_REVIEW in soil_documents, "
        "and halts. The UI displays the review modal. The digital twin state remains strictly unchanged until the farmer confirms the profile. "
        "Upon confirmation, the backend validates physical constraints, assigns the VERIFIED_LAB_TEST provenance badge, triggers digital twin state "
        "synchronization, and instantly updates the farmer dashboard.\n\n"
        "[HANDOFF TO PERSON 4]:\n"
        "Now that we have seen how external soil documents are parsed and validated into verified state vectors, I pass the presentation to Person 4 "
        "to walk through our 3NF Relational Database Schemas, our Data Provenance Engine, and our 116-test automated verification suite.\"",
        label="SLIDE 7 SPOKEN SCRIPT",
        border_hex="1E3A8A",
        bg_hex="EFF6FF"
    )

    # =========================================================================
    # SECTION 3: A-TO-Z TECHNICAL & ACADEMIC DEEP DIVE
    # =========================================================================
    add_h1("3. A-to-Z Technical & Academic Deep Dive (Grounded in Code)")

    add_p(
        "This section details every regex, validation rule, schema model, and diagram arrow in Person 3's engineering vertical. "
        "Use these exact technical specifications to defend your design during oral cross-examination."
    )

    add_h2("3.1 Soil Health Card OCR Extraction Pipeline")
    add_p(
        "Implemented in backend/services/soil_ocr_service.py. The service handles uploaded documents across PDF, JPG, JPEG, and PNG formats."
    )

    add_h3("A. File Upload Security & Magic Byte Validation")
    add_p(
        "In validate_uploaded_file() (lines 47–72 of soil_ocr_service.py), uploads undergo rigorous security screening before processing:\n"
        "1. Size Bounding: Files larger than MAX_FILE_SIZE_BYTES (10 MB = 10,485,760 bytes) are rejected with HTTP 413.\n"
        "2. Magic Byte Inspection (MIME Sniffing Prevention):\n"
        "   - PDF: Header must begin with b'%PDF'\n"
        "   - JPEG/JPG: Header must begin with b'\\xff\\xd8\\xff' or b'\\xff\\xd8'\n"
        "   - PNG: Header must begin with b'\\x89PNG\\r\\n\\x1a\\n'\n"
        "   If a malicious executable renamed as 'card.pdf' is uploaded, magic byte validation rejects it immediately with HTTP 400."
    )

    add_h3("B. Hybrid Dual-Engine Extraction (PDF vs. Camera Scans)")
    add_p(
        "- Digital Vector PDFs: Function extract_text_from_pdf() uses pypdf (PdfReader) to extract clean embedded character streams directly from vector text layers.\n"
        "- Scanned Smartphone Images / Raster PDFs: Function extract_text_from_image() loads bytes via PIL.Image and passes them to pytesseract (Tesseract OCR Engine v5.x) "
        "to extract raw text strings from raster pixel grids."
    )

    add_h3("C. Robust Key-Value Regex Parsing Architecture")
    add_p(
        "In parse_soil_health_card_text() (lines 104–263), regex patterns parse bilingual Indian Soil Health Card formats "
        "(accounting for variations across Central and State government testing labs):"
    )

    regex_table = [
        ["pH (Soil Reaction)", r'(?:Soil\s+Reaction\s*\(?pH\)?|pH\s+Value|p\.H\.|pH)[\s:=|]+([0-9]+(?:\.[0-9]+)?)', "0.0 – 14.0", "6.5 – 7.5"],
        ["Available Nitrogen (N)", r'(?:Available\s+Nitrogen|Nitrogen(?:\s*\(?N\)?)?|Avail\.\s*N)[\s:=|]+([0-9]+(?:\.[0-9]+)?)', "0.0 – 2000.0 kg/ha", "280.0 – 400.0 kg/ha"],
        ["Available Phosphorus (P)", r'(?:Available\s+Phosphorus|Phosphorus(?:\s*\(?P\)?)?|P2O5|Avail\.\s*P)[\s:=|]+([0-9]+(?:\.[0-9]+)?)', "0.0 – 500.0 kg/ha", "20.0 – 40.0 kg/ha"],
        ["Available Potassium (K)", r'(?:Available\s+Potassium|Potassium(?:\s*\(?K\)?)?|K2O|Avail\.\s*K)[\s:=|]+([0-9]+(?:\.[0-9]+)?)', "0.0 – 2000.0 kg/ha", "150.0 – 300.0 kg/ha"],
        ["Organic Carbon (OC)", r'(?:Organic\s+Carbon\s*\(?OC\)?|O\.C\.|OC)[\s:=|]+([0-9]+(?:\.[0-9]+)?)', "0.0 – 10.0 %", "0.75 – 1.5 %"],
        ["Electrical Conductivity (EC)", r'(?:Electrical\s+Conductivity\s*\(?EC\)?|E\.C\.|EC)[\s:=|]+([0-9]+(?:\.[0-9]+)?)', "0.0 – 20.0 dS/m", "0.0 – 1.0 dS/m"],
        ["Micronutrients (S, Zn, Fe, Cu, Mn, B)", r'(?:Available\s+Zinc|Zinc(?:\s*\(?Zn\)?)?|Zn)[\s:=|]+([0-9]+(?:\.[0-9]+)?)', "Physical limits per element", "ICAR reference ppm"]
    ]
    add_table_data("Table 3.1: OCR Key-Value Regular Expression Mappings and Biological Sanity Bounds",
                   ["Nutrient / Parameter", "Primary Regular Expression Pattern", "Absolute Sanity Bounds", "Optimal Agronomic Range"],
                   regex_table, col_widths=[1.5, 2.3, 1.2, 1.0])

    add_h3("D. Agronomic Status Classification & Confidence Metrics")
    add_p(
        "For every detected parameter, the system performs biological range validation against PARAMETER_SPECS:\n"
        "- If value < min or value > max: Flagged as status='INVALID' with an explicit warning note.\n"
        "- If within physical bounds: Categorized into agronomic status:\n"
        "  * 'LOW': Deficient (below optimal minimum, e.g. Nitrogen < 280 kg/ha requires top-dressing).\n"
        "  * 'GOOD': Optimal (within optimal range, e.g. pH 6.5–7.5).\n"
        "  * 'HIGH': Excessive (above optimal maximum, e.g. pH > 8.5 indicates alkalinity; high Nitrogen increases lodging risk).\n"
        "- OCR Status Classification:\n"
        "  * 'SUCCESS': At least 3 core parameters (pH, N, P, K, OC) extracted reliably.\n"
        "  * 'PARTIAL_EXTRACTION': 1 to 2 parameters extracted.\n"
        "  * 'OCR_FAILED': Zero parameters extracted (e.g. blurred scan or cartoon). Populates empty editable template."
    )

    add_h2("3.2 Mandatory Human-in-the-Loop Confirmation Gate (Safety Engineering)")
    add_p(
        "Implemented in backend/routers/soil.py and backend/models/farm.py. The confirmation gate represents our primary defense against "
        "autonomous AI hallucinations."
    )

    add_h3("A. The Quarantine State Machine")
    add_p(
        "1. Upload Phase (POST /api/soil/upload):\n"
        "   - Scanned file is saved to farm-isolated storage: data/uploads/soil/{farm_id}/{uuid}_{filename}.\n"
        "   - Record created in SoilDocument with is_confirmed=False, ocr_status='REVIEW_REQUIRED'.\n"
        "   - Response returns candidate values with extraction_state='REVIEW_REQUIRED'.\n"
        "   - Crucial Safety Barrier: farm.soil_data_available remains FALSE. No record is written to farm_soil_profiles.\n\n"
        "2. Farmer Review Phase (Interactive UI Modal):\n"
        "   - The Next.js frontend displays the review modal.\n"
        "   - Detected values are populated into input fields; undetected fields display empty placeholders.\n"
        "   - Amber alert badge clearly informs the user: 'Review extracted values before confirming.'\n"
        "   - Farmer can edit any misread digit (e.g. changing 450 to 45 kg/ha).\n\n"
        "3. Confirmation Phase (POST /api/soil/confirm):\n"
        "   - Validates that pH is between 0 and 14 and all nutrient values are non-negative.\n"
        "   - Archives previous active profiles: db.query(FarmSoilProfile).filter(...).update({'is_active': False}).\n"
        "   - Creates a new active FarmSoilProfile record with confirmation_status='CONFIRMED'.\n"
        "   - Updates the associated SoilDocument: doc.is_confirmed = True.\n"
        "   - Sets farm.soil_data_available = True.\n"
        "   - Appends an immutable transactional audit entry in FarmEvent table with event_type='SOIL_PROFILE_CONFIRMED'."
    )

    add_h3("B. Provenance Tagging Rules")
    add_p(
        "- 'SOIL_HEALTH_CARD' (Promoted to 'VERIFIED_LAB_TEST' in Digital Twin): Applied when values match the physical card and a valid document_id is linked.\n"
        "- 'FARMER_ENTERED': Applied when the farmer manually inputs or edits values without an official document link or after OCR failure.\n"
        "- 'REGIONAL_BASELINE': Default fallback state when no card has been uploaded. Decision engine uses ICAR district averages."
    )

    add_h2("3.3 Software Requirements Specification (Chapter 2 Walkthrough)")
    add_p(
        "In Chapter 2 of our project report, the system is specified according to IEEE 830 standard guidelines."
    )

    add_h3("A. Hardware & Software Specifications (Tables 2.1 & 2.2)")
    add_p(
        "- Minimum Hardware: Intel Core i5 / AMD Ryzen 5, 8 GB DDR4 RAM, 10 GB SSD, standard broadband.\n"
        "- Production Deployment: Intel Xeon / AMD EPYC (8 vCPUs), 16–32 GB RAM, 50 GB NVMe SSD, 1 Gbps cloud uplink.\n"
        "- Software Stack: FastAPI 0.115+, Uvicorn 0.32+, Pydantic v2, SQLAlchemy 2.0 ORM, SQLite / PostgreSQL, "
        "Next.js 14 App Router (React 18), Tailwind CSS, PyTesseract OCR, pypdf."
    )

    add_h3("B. Functional Requirements (FR-1 through FR-6)")
    add_p(
        "1. FR-1 (Farm Profile Management): Register farm with GPS coordinates, crop, sowing date, target yield, and district.\n"
        "2. FR-2 (Agro-Meteorological Ingestion): Query Open-Meteo for hourly/daily temp, rain, humidity, wind, and FAO-56 ET0.\n"
        "3. FR-3 (GDD & Phenological Stage Progression): Accumulate Growing Degree Days (base 4.0°C) across 8 wheat stages.\n"
        "4. FR-4 (Mandi Forecasting): Ingest AGMARKNET daily arrivals/prices and forecast 30-day prices using XGBoost.\n"
        "5. FR-5 (Soil OCR & Human Confirmation): Ingest Soil Health Cards, extract nutrients, enforce review gate before updating profile.\n"
        "6. FR-6 (Multi-Factor Agronomic Risk Synthesis): Aggregate weather, soil, and price vectors to produce stage-consistent advisories."
    )

    add_h3("C. Non-Functional Requirements (NFR-1 through NFR-4)")
    add_p(
        "1. NFR-1 (Performance & Latency): Sub-250ms API response under cached states; sub-1200ms during live external API round-trips.\n"
        "2. NFR-2 (Data Integrity & Zero Hallucination): Every metric carries an immutable provenance tag. Zero ungrounded advice.\n"
        "3. NFR-3 (High Availability & Fault Tolerance): Graceful fallback to cached/seed baselines during external network dropouts.\n"
        "4. NFR-4 (Cross-Platform Portability): Runs seamlessly on Linux, Windows, and macOS with container-ready architecture."
    )

    add_h2("3.4 System Methodology: DFDs & Sequence Design (Chapter 3 Walkthrough)")

    add_h3("A. Data Flow Diagrams (Figure 3.2 Breakdown)")
    add_p(
        "1. Level 0 Context Diagram (Fig. 3.2a):\n"
        "   - Defines the boundary of KRISHI Intelligence with 3 external entities:\n"
        "     * The Farmer / User: Ingests farm coordinates, crop variety, sowing date, and Soil Health Cards; receives synthesized advisories.\n"
        "     * Open-Meteo Agro-Weather Service: Feeds hourly weather telemetry and 7-day forecasts.\n"
        "     * AGMARKNET Government Portal: Feeds daily modal prices and wholesale arrival volumes.\n\n"
        "2. Level 1 Decomposed Functional DFD (Fig. 3.2b):\n"
        "   - Decomposes the platform into 5 core processes and 5 persistent data stores:\n"
        "     * Process 1.0 (Agro-Weather Ingestion) -> Writes to Data Store D1: Weather Cache\n"
        "     * Process 2.0 (SHC OCR & Confirmation Gate) -> Writes to Data Store D2: Soil Profiles\n"
        "     * Process 3.0 (Mandi Market Ingestion) -> Writes to Data Store D3: Mandi Cache\n"
        "     * Process 4.0 (Farm Digital Twin Synchronizer) -> Writes to Data Store D4: Farm State\n"
        "     * Process 5.0 (Agentic Risk & Decision Engine) -> Writes to Data Store D5: Advisory Ledger"
    )

    add_h3("B. Procedural Sequence Diagram (Figure 3.4 Breakdown)")
    add_p(
        "Figure 3.4 models the complete 11-step chronological lifecycle of document ingestion and state upgrade:\n"
        "1. Farmer uploads scanned Soil Health Card document via Next.js UI.\n"
        "2. UI dispatches multipart POST request to /api/soil/upload.\n"
        "3. FastAPI backend invokes process_soil_health_card_document() to extract candidate chemical concentrations.\n"
        "4. Candidate fields (pH, N, P, K, OC, EC) are parsed with confidence states.\n"
        "5. Document record is stored with status 'REVIEW_REQUIRED' in soil_documents table.\n"
        "6. UI triggers interactive review modal displaying values with alert banner.\n"
        "7. Farmer reviews, corrects any misread digits, and clicks 'Confirm Soil Profile'.\n"
        "8. UI dispatches JSON payload to /api/soil/confirm.\n"
        "9. Backend validates physical constraints and writes active record to farm_soil_profiles with status 'CONFIRMED'.\n"
        "10. DigitalTwinEngine triggers sync_state(), recalculating nutrient deficits and updating farm risk vectors.\n"
        "11. UI instantly upgrades the soil status badge from REGIONAL_BASELINE to VERIFIED_LAB_TEST."
    )

    add_h2("3.5 Current Boundaries ('What We Are Missing Now') vs. 4th-Year Future Scope")
    add_p(
        "Examiners appreciate students who can speak honestly about what their current prototype scopes out."
    )

    limits_table = [
        ["Periodic Lab Testing Latency", "Physical Soil Health Cards are issued once every 2–3 years; mid-season leaching or fertilizer uptake is not monitored in real time.", "Deploy wireless in-situ LoRaWAN IoT soil probes reading continuous NPK, moisture, and EC."],
        ["Image Distortion & Low-Light Scans", "Heavily creased, folded, or low-light smartphone camera photos can degrade Tesseract OCR confidence.", "Integrate on-device OpenCV perspective rectification, shadow removal, and contrast enhancement before OCR."],
        ["Bilingual Layout Scope", "Optimized for standard Central/UP state Soil Health Cards printed in English and Hindi.", "Implement multi-state multilingual template parsers supporting 12 regional languages via IndicOCR."],
        ["Manual Human Intervention", "Requires the farmer to visually inspect and click confirm before advisories unlock.", "Introduce voice-assisted audio confirmation via Bhashini AI ('Did your card read 240 kg Nitrogen? Say Yes or No')."]
    ]
    add_table_data("Table 3.2: Person 3 Module Boundaries vs. 4th-Year Major Project Roadmap",
                   ["Subsystem", "Current 3rd-Year Limitation (What We Scope Out)", "4th-Year Final Year Engineering Expansion"],
                   limits_table, col_widths=[1.3, 2.5, 2.4])

    add_h2("3.6 Codebase Pointer Table (Live Code Demonstration)")
    add_p(
        "If an examiner asks: 'Show me where the confirmation check is implemented' or 'Where is the regex parser?', immediately open these files:"
    )

    code_ptrs = [
        ["backend/services/soil_ocr_service.py", "parse_soil_health_card_text()", "Regex extraction patterns, PARAMETER_SPECS biological bounds, confidence status"],
        ["backend/services/soil_ocr_service.py", "validate_uploaded_file()", "10 MB size limit check and %PDF / JPEG / PNG magic byte header validation"],
        ["backend/routers/soil.py", "upload_soil_document()", "Handles file upload, saves to isolated farm dir, creates SoilDocument with is_confirmed=False"],
        ["backend/routers/soil.py", "confirm_soil_profile()", "Validates pH 0-14, commits FarmSoilProfile, sets is_confirmed=True, logs FarmEvent"],
        ["backend/models/farm.py", "SoilDocument & FarmSoilProfile", "SQLAlchemy 3NF models storing raw extraction JSON and confirmed active lab profiles"],
        ["backend/schemas/soil.py", "SoilConfirmationRequest", "Pydantic v2 validation models for document extraction and profile confirmation"],
        ["backend/tests/test_soil_health_card.py", "TestSoilHealthCardSuite", "10 automated tests verifying file limits, OCR parsing, locked gates, and invalid inputs"]
    ]
    add_table_data("Table 3.3: Person 3 Repository Codebase Pointers",
                   ["File Path in Repository", "Key Class / Function", "Technical Responsibility & Defense Point"],
                   code_ptrs, col_widths=[2.1, 1.8, 2.4])

    # =========================================================================
    # SECTION 4: 15 TOUGH VIVA CROSS-QUESTIONS & HIGH-SCORING ANSWERS
    # =========================================================================
    add_h1("4. 15 Tough Viva Cross-Questions & High-Scoring Answers")

    add_p(
        "These 15 cross-questions cover computer vision, document parsing, software engineering design, and safety invariants. "
        "Review them thoroughly before entering the viva room."
    )

    viva_qa = [
        ("Q1: What happens if the OCR misreads Nitrogen as 450 kg/ha instead of 45 kg/ha?",
         "This scenario illustrates the exact reason why we engineered our Mandatory Farmer Confirmation Gate. If the raw OCR misreads 45 kg/ha as 450 kg/ha, "
         "the value is quarantined in the SoilDocument table with status REVIEW_REQUIRED. It is never committed to the active farm profile. "
         "When the review modal appears, the UI displays 450 kg/ha with a warning badge because it is unusually high compared to typical soil baselines. "
         "The farmer simply taps the input field, corrects the number to 45, and clicks Confirm. Only the verified 45 kg/ha enters the digital twin, "
         "preventing catastrophic fertilizer under-dosing or crop burning."),

        ("Q2: Why not make the OCR pipeline 100% automated without asking the farmer to confirm?",
         "In precision agriculture, fully automated OCR introduces severe life-critical risks. In optical character recognition, physical card folds, "
         "low-resolution phone cameras, shadows, and print bleed cause character confusion—such as mistaking '1' for '7', or '3' for '8'. "
         "If an automated system acts on an OCR misread, it could recommend applying 300 kg of Urea to an already nitrogen-rich soil, destroying the crop "
         "and causing immense financial loss. Our Human-in-the-Loop Confirmation Gate enforces zero machine hallucination, treating OCR as a candidate "
         "accelerator rather than an unquestioned ground truth."),

        ("Q3: What if a farmer does not possess a Soil Health Card at all?",
         "The platform is engineered with graceful degradation. If a farmer has not tested their soil or does not upload a card, the system does not crash or block. "
         "Instead, the Living Farm Digital Twin initializes the soil state using verified regional agro-climatic baselines (REGIONAL_BASELINE) compiled "
         "from Indian Council of Agricultural Research (ICAR) district benchmarks for Central Uttar Pradesh. The farmer is clearly informed via an amber UI banner "
         "that recommendations are based on regional averages rather than lab-verified plot tests."),

        ("Q4: Explain the difference between Level-0 DFD and Level-1 DFD in your report.",
         "A Level-0 DFD (also known as the Context Diagram) defines the high-level boundary of the entire system as a single abstract process bubble interacting "
         "with external entities (the Farmer, Open-Meteo, and AGMARKNET). It shows external inputs and outputs without detailing internal operations. "
         "The Level-1 DFD decomposes this single bubble into five core functional sub-processes (Weather Ingestion 1.0, Soil OCR 2.0, Mandi Ingestion 3.0, "
         "Digital Twin State 4.0, and Risk Synthesis 5.0) and reveals the persistent data stores (D1 through D5) that manage state transitions between them."),

        ("Q5: Walk through the exact chronological steps in your Sequence Diagram (Figure 3.4).",
         "The sequence follows 11 chronological steps: (1) Farmer uploads document via UI. (2) UI sends multipart POST to /api/soil/upload. (3) Backend executes "
         "process_soil_health_card_document(). (4) Candidate nutrients are parsed with confidence states. (5) Record stored as REVIEW_REQUIRED in soil_documents. "
         "(6) UI triggers review modal. (7) Farmer reviews/edits values and clicks confirm. (8) UI dispatches JSON payload to /api/soil/confirm. (9) Backend validates "
         "pH (0-14) and non-negative bounds, creating an active FarmSoilProfile record. (10) DigitalTwinEngine recalculates nutrient deficits via sync_state(). "
         "(11) UI upgrades the provenance badge to VERIFIED_LAB_TEST."),

        ("Q6: What are the current limitations of your OCR pipeline?",
         "Our current 3rd-year prototype has three honest engineering boundaries: (1) Periodic testing latency: It relies on physical Soil Health Cards issued once "
         "every 2–3 years, meaning intra-season fertilizer leaching is not tracked in real-time. (2) Camera angle sensitivity: Severe perspective warping or extreme "
         "shadows from low-end smartphones can reduce Tesseract confidence. (3) Language scope: Currently optimized for standard English and Hindi bilingual formats. "
         "In our 4th-year roadmap, we plan to address these by deploying IoT soil probes and integrating on-device OpenCV perspective rectification."),

        ("Q7: How do you handle creased, skewed, or shadowed phone camera photos?",
         "Currently, our backend enforces magic byte validation and attempts extraction using PyTesseract image processing. If creases or shadows prevent OCR from "
         "reading standard anchor keywords ('Nitrogen', 'pH'), function process_soil_health_card_document() catches the low confidence and returns ocr_status='OCR_FAILED'. "
         "Rather than throwing a 500 error, it returns an empty, pre-structured template. The farmer is presented with a friendly message: 'We couldn\\'t reliably read "
         "this card. Please enter values manually.' This ensures 100% system uptime and smooth UX."),

        ("Q8: What is the difference between pypdf and pytesseract in your pipeline?",
         "They serve complementary roles based on document type. pypdf is a pure-Python library designed for digital vector PDFs (such as official digital cards downloaded "
         "from the soilhealth.dac.gov.in portal); it reads embedded font character streams instantly with 100% accuracy without rasterization. pytesseract is an OCR wrapper "
         "around the Google Tesseract C++ engine used for raster image scans (JPEG/PNG) and scanned PDFs; it analyzes pixel matrices to optically recognize glyphs."),

        ("Q9: How do you prevent adversarial or corrupted image uploads from crashing your server?",
         "We implement defense-in-depth: (1) validate_uploaded_file() checks file size (<= 10MB) and inspects file header magic bytes, rejecting renamed executables. "
         "(2) In soil_ocr_service.py, document processing is wrapped in try-except blocks. (3) If an arbitrary image like a cartoon character is uploaded, "
         "the parser detects zero matching agrochemical patterns and sets ocr_status='OCR_FAILED'. (4) The server returns HTTP 200 with an empty review template "
         "rather than an unhandled 500 internal server error. Automated test test_06_corrupted_image_handling in test_soil_health_card.py validates this behavior."),

        ("Q10: Why is biological range validation (PARAMETER_SPECS) critical during confirmation?",
         "Even when a farmer manually enters data, typos can occur (e.g. typing pH 77 instead of 7.7). In backend/routers/soil.py lines 213–226, the confirmation "
         "handler validates every parameter against strict physical invariants: pH must be between 0.0 and 14.0, and nutrient concentrations (N, P, K, micronutrients) "
         "cannot be negative. If an invalid value is submitted, the API returns HTTP 400 Bad Request with a clear explanatory error, preventing corrupted numbers "
         "from entering the digital twin."),

        ("Q11: What is the difference between SOIL_HEALTH_CARD and FARMER_ENTERED provenance?",
         "SOIL_HEALTH_CARD provenance is assigned when the values originate directly from an uploaded physical document that is stored in our database for auditability; "
         "this promotes the digital twin state to VERIFIED_LAB_TEST. FARMER_ENTERED provenance is assigned when the farmer manually keys in values without an accompanying "
         "document or significantly modifies OCR fields. This distinction maintains transparent provenance: agronomists and insurers know whether data was verified by an "
         "official lab card or entered via farmer self-reporting."),

        ("Q12: What are the Non-Functional Requirements in your Chapter 2 SRS and how do you test them?",
         "Our SRS specifies four key NFRs: (1) Latency: Sub-250ms cached responses and sub-1200ms live API round-trips, verified via our FastAPI benchmark suite. "
         "(2) Data Integrity: Zero hallucinated data, verified by testing that unconfirmed OCR never updates the farm profile. (3) Fault Tolerance: Graceful fallback "
         "to regional baselines during external dropouts, verified by mocked outage tests. (4) Portability: Verified across Linux, macOS, and Windows with zero platform-specific "
         "path dependencies using pathlib.Path."),

        ("Q13: How does confirming a soil profile alter the recommendations generated by the Living Farm Digital Twin?",
         "When a soil profile is confirmed, the digital twin recalculates the farm's soil nutrient deficit vectors. For example, if the regional baseline assumed optimal "
         "Nitrogen (320 kg/ha) but the farmer's confirmed lab test reveals severe deficiency (180 kg/ha), the risk engine detects high nutrient stress. "
         "When the crop advances to Crown Root Initiation (CRI at 150 GDD), the advisory engine automatically prescribes an increased top-dressing dosage of Urea "
         "(e.g. 65 kg/acre instead of standard 45 kg/acre), directly preventing yield penalty."),

        ("Q14: What are Data Stores D1 through D5 in your Level-1 DFD (Figure 3.2b)?",
         "D1 is Weather Cache (stores hourly and 7-day meteorological forecasts and GDD). D2 is Soil Profiles (stores uploaded document metadata, review statuses, "
         "and confirmed NPK concentrations). D3 is Mandi Cache (stores APMC wholesale spot prices and arrival volumes). D4 is Farm State (persists the central living "
         "digital twin entity with crop phenology and stress vectors). D5 is Advisory Ledger (an immutable transactional log storing synthesized farm recommendations "
         "and farmer acknowledgment timestamps)."),

        ("Q15: How will your 4th-year final year project replace periodic Soil Health Cards with real-time IoT telemetry?",
         "In our 4th-year major project roadmap, we will deploy hardware IoT probes equipped with optical NPK sensors, electrical conductivity probes, and frequency-domain "
         "soil moisture sensors directly in the crop root zone. These probes will broadcast continuous telemetry every 6 hours over a low-power LoRaWAN wireless network "
         "to a local gateway. The digital twin will ingest continuous soil moisture and nitrogen depletion data, completely eliminating the 2–3 year latency of physical "
         "paper lab cards and enabling dynamic, precision fertigation.")
    ]

    for q_text, a_text in viva_qa:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.keep_with_next = True
        r_q = p_q.add_run(q_text)
        r_q.bold = True
        r_q.font.name = 'Times New Roman'
        r_q.font.size = Pt(11.5)
        r_q.font.color.rgb = RGBColor(30, 58, 138)

        p_a = doc.add_paragraph()
        p_a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_a.paragraph_format.space_before = Pt(0)
        p_a.paragraph_format.space_after = Pt(6)
        p_a.paragraph_format.line_spacing = 1.2
        r_ans_tag = p_a.add_run("Model Defense Answer: ")
        r_ans_tag.bold = True
        r_ans_tag.font.name = 'Times New Roman'
        r_ans_tag.font.size = Pt(11)
        r_ans_tag.font.color.rgb = RGBColor(217, 119, 6)

        r_a = p_a.add_run(a_text)
        r_a.font.name = 'Times New Roman'
        r_a.font.size = Pt(11)
        r_a.font.color.rgb = RGBColor(15, 23, 42)

    # Save Document
    print(f"Saving guide to: {OUTPUT_DOCX}")
    doc.save(OUTPUT_DOCX)
    print("Person 3 Viva Guide generated successfully!")


if __name__ == "__main__":
    build_guide()
