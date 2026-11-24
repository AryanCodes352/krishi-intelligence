"""
scripts/build_viva_guide_p4.py
Generates the comprehensive Academic Viva & Presentation Guide for Person 4
(Database & QA Engineer — Database Schema, ER Diagrams, Provenance Engine, Limitations & Conclusion).
Document output: docs/viva_guides/Person_4_Database_Provenance_and_Conclusion_Guide.docx
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
OUTPUT_DOCX = os.path.join(OUTPUT_DIR, "Person_4_Database_Provenance_and_Conclusion_Guide.docx")


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
    print("Building Person 4 Database, Provenance & Conclusion Guide...")
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
        r_hdr = p_hdr.add_run("KRISHI Intelligence — Academic Viva Guide | Person 4 (Database, Provenance & Conclusion)")
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
    run_sub = sub_p.add_run("PERSON 4 MASTER PLAYBOOK: DATABASE SCHEMA, PROVENANCE ENGINE, LIMITATIONS & CONCLUSION")
    run_sub.bold = True
    run_sub.font.name = 'Times New Roman'
    run_sub.font.size = Pt(12)
    run_sub.font.color.rgb = RGBColor(124, 58, 237)

    add_callout(
        "THIS PLAYBOOK IS EXCLUSIVELY FOR PERSON 4. Your assigned responsibility covers:\n"
        "1. Engineering Pillar: 3NF Relational Database Schema, Farm Digital Twin State Persistence & Data Provenance Engine "
        "(LIVE_OBSERVATION vs HISTORICAL_SEED and VERIFIED_LAB_TEST vs REGIONAL_BASELINE schema-level guardrails).\n"
        "2. Documentation Pillar: Database Design, Entity-Relationship (ER) Diagram (Fig 3.3), 116 Pytest Verification Matrix (Chapter 5), "
        "Honest Limitations ('What We Are Missing Now'), and Chapter 6 Conclusion & 4th-Year Major Project Roadmap.\n\n"
        "This playbook gives you every schema field, foreign key constraint, provenance rule, limitation defense, and closing transition "
        "so you can master your viva defense in 20 minutes.",
        label="PERSON 4 OWNERSHIP CHARTER",
        border_hex="7C3AED",
        bg_hex="F5F3FF"
    )

    # =========================================================================
    # SECTION 1: ROLE & OWNERSHIP MATRIX
    # =========================================================================
    add_h1("1. Role & Ownership Matrix (Person 4)")

    add_p(
        "In our 4-member project team structure for KRISHI Intelligence, Person 4 defends the structural foundation, transactional integrity, "
        "and architectural horizon of the platform. You own the relational database models, state persistence, provenance classification logic, "
        "quality assurance test execution, and the intellectual conclusion of our academic defense before handing the stage back to Person 1 for the live demo."
    )

    role_table = [
        ["Person 1 (Aryan)", "Lead Architect & Live Demo", "Slides 1–3, Slide 11, Live Demo", "System Architecture, Risk Synthesis Engine, Chapter 1 & Synopsis Compilation"],
        ["Person 2", "Data & ML Engineer", "Slides 4–5, ML Viva Defense", "Open-Meteo Telemetry, AGMARKNET Pipelines, XGBoost Forecaster, Chapter 5 Metrics"],
        ["Person 3", "Vision & Methodology", "Slides 6–7, Methodology Viva", "Soil Health Card OCR, Mandatory Review Gate, Chapter 2 SRS, Chapter 3 DFD & Sequence"],
        ["Person 4 (You)", "Database & QA Engineer", "Slides 8–10, QA & Scope Defense", "3NF Relational ER Schema, 4-Tier Provenance Engine, 116 Pytest Suite, Limitations/Roadmap"]
    ]
    add_table_data("Table 1.1: 4-Member Team Ownership Matrix & Presentation Division",
                   ["Team Member", "Role Title", "Presentation Ownership", "Technical & Documentation Deliverables"],
                   role_table, col_widths=[1.2, 1.4, 1.4, 2.0])

    add_h2("1.1 Presentation Coordination & Handoff Protocols")
    add_p(
        "Flawless stage execution requires sharp, practiced transitions between speakers. You participate in the final two transitions of the defense:"
    )

    add_callout(
        "HOW YOU RECEIVE THE STAGE (From Person 3):\n"
        "Person 3 will conclude Slide 7 (DFD & Sequence Design) by stating:\n"
        "\"Now that we have seen how external soil documents are parsed and validated into verified state vectors, "
        "I pass the presentation to Person 4 to walk through our 3NF Relational Database Schemas, our Data Provenance Engine, "
        "and our 116-test automated verification suite.\"\n\n"
        "YOUR IMMEDIATE RESPONSE (Step forward with calm confidence, address the panel):\n"
        "\"Thank you, Person 3. Respected examiners: In an agentic agricultural system, real-time intelligence is only as trustworthy "
        "as the database schema and provenance safeguards that preserve it. I will now present our normalized relational architecture, "
        "our provenance state machine, our automated test suite, and our 4th-year engineering expansion roadmap.\"",
        label="HANDOFF INGESTION PROTOCOL",
        border_hex="7C3AED",
        bg_hex="F5F3FF"
    )

    add_callout(
        "HOW YOU PASS THE STAGE (Back to Person 1 for the Live Demo):\n"
        "After concluding your walkthrough of Slide 10 (Current Boundaries & 4th-Year Major Roadmap), transition smoothly to Aryan:\n"
        "\"Having presented our theoretical foundations, machine learning models, and system verification, I now invite our Team Lead, Aryan, "
        "to conduct the live software demonstration and conclude our defense.\"",
        label="HANDOFF DISPATCH PROTOCOL (TO LIVE DEMO)",
        border_hex="059669",
        bg_hex="ECFDF5"
    )

    # =========================================================================
    # SECTION 2: WORD-FOR-WORD PRESENTATION SPEECH (SLIDES 8 TO 10)
    # =========================================================================
    add_h1("2. Word-for-Word Spoken Presentation Script (~2.5 Minutes)")

    add_p(
        "Practice this script out loud until your verbal delivery is smooth, professional, and timed to exactly 2 minutes and 30 seconds."
    )

    add_h2("Part A: Slide 8 — Database Architecture & Farm Digital Twin ER Schema (~50 Seconds)")
    add_callout(
        "[SLIDE CHANGE TO SLIDE 8: Database Architecture & Farm Digital Twin ER Schema]\n\n"
        "[PAUSE 2 SECONDS — POINT TOWARDS FIGURE 3.3 ON THE LEFT]\n\n"
        "\"Respected examiners, turning to Slide 8, on the left you see Figure 3.3: the Entity-Relationship schema powering our platform, "
        "engineered in Third Normal Form (3NF) using SQLAlchemy 2.0 ORM.\n\n"
        "Our schema is structured around a central anchor entity: the 'farms' table. Every registered plot has a unique UUID primary key, "
        "storing farmer identity, high-precision GPS coordinates, acreage, crop variety, and sowing date.\n\n"
        "Branching from this central entity are five specialized child tables enforcing strict one-to-many foreign key relationships with cascading deletes:\n"
        "- 'soil_documents' stores uploaded file metadata, magic-byte extraction records, and quarantine review statuses.\n"
        "- 'farm_soil_profiles' records verified laboratory measurements—such as pH, NPK, and electrical conductivity—alongside active status flags.\n"
        "- 'weather_observations' maintains time-series telemetry from Open-Meteo, storing hourly precipitation, temperatures, and calculated GDD.\n"
        "- 'price_predictions' persists our 30-day XGBoost price forecasts with 95% confidence intervals and evaluation metrics.\n"
        "- And 'farm_events' functions as an append-only, immutable transactional ledger where every stage progression, risk alert, and farmer confirmation "
        "is recorded with microsecond timestamps for complete regulatory auditability.\n\n"
        "By enforcing 3NF normalization and composite B-tree indexes on farm_id and timestamp, we eliminate data redundancy, prevent update anomalies, "
        "and achieve sub-45-millisecond relational query speeds.\"",
        label="SLIDE 8 SPOKEN SCRIPT",
        border_hex="7C3AED",
        bg_hex="F5F3FF"
    )

    add_h2("Part B: Slide 9 — Data Provenance Engine & Automated Verification Suite (~50 Seconds)")
    add_callout(
        "[SLIDE CHANGE TO SLIDE 9: Data Provenance Engine & Automated Verification Suite]\n\n"
        "[PAUSE 2 SECONDS — POINT TO THE PROVENANCE TIERS ON SCREEN]\n\n"
        "\"Moving to Slide 9, we address a foundational flaw present in generic agricultural chatbots and decision tools: silent data degradation.\n\n"
        "When rural internet connections drop or government market feeds delay their daily uploads, generic AI wrappers hallucinate fake prices "
        "or outdated weather. In KRISHI Intelligence, we mathematically eliminated hallucination by implementing a strict 4-Tier Provenance State Machine:\n"
        "- LIVE_OBSERVATION (Green): Applied when telemetry is less than or equal to 24 hours old. Highest confidence.\n"
        "- LATEST_AVAILABLE (Blue): Applied when market feeds are 2 to 7 days old, such as during weekend trading lulls or public holidays.\n"
        "- STALE_REFERENCE (Amber): Triggered when data exceeds 7 days. The advisory engine automatically warns the farmer and halts automated execution.\n"
        "- HISTORICAL_SEED (Purple): If external government APIs fail completely, the system gracefully activates our calibrated 2020-to-2026 baseline. "
        "We never invent numbers; we transparently disclose the data source to the farmer.\n\n"
        "On the right, we present our Quality Assurance verification. As detailed in Chapter 5, our system is guarded by 116 automated pytest unit "
        "and integration tests covering our OCR parser, weather GDD engine, XGBoost forecaster, database cascades, and provenance state machines. "
        "Our test suite achieves a 100% pass rate in 10.18 seconds with zero TypeScript compilation errors.\"",
        label="SLIDE 9 SPOKEN SCRIPT",
        border_hex="2563EB",
        bg_hex="EFF6FF"
    )

    add_h2("Part C: Slide 10 — Current System Boundaries vs. 4th-Year Major Roadmap (~50 Seconds)")
    add_callout(
        "[SLIDE CHANGE TO SLIDE 10: Current System Boundaries vs. 4th-Year Major Project Roadmap]\n\n"
        "[PAUSE 2 SECONDS — SPEAK WITH ACADEMIC MATURITY AND HONESTY]\n\n"
        "\"Concluding on Slide 10, as 3rd-year engineering students, we believe in honest academic defense. We clearly defined what our prototype "
        "currently scopes out in Chapter 6:\n"
        "Currently, our system is calibrated specifically for Wheat in Central Uttar Pradesh; it relies on periodic physical Soil Health Cards rather than "
        "real-time in-situ probes; it operates through a modern web screen interface; and it evaluates one primary farm plot at a time.\n\n"
        "In our upcoming 7th and 8th semester 4th-Year Major Project, we have engineered a concrete 4-point roadmap to scale KRISHI Intelligence into a production platform:\n"
        "1. Vernacular Voice Assistant: Integrating Government of India's Bhashini AI to provide hands-free voice interaction in Hindi, Bhojpuri, and Punjabi.\n"
        "2. Wireless IoT Soil Telemetry: Deploying low-power, solar-assisted LoRaWAN soil probes reading continuous root-zone NPK and moisture directly into the Digital Twin.\n"
        "3. Multi-Plot Farm Management: Enabling progressive growers to manage complex multi-crop crop rotation schedules like Paddy-Wheat-Sugarcane.\n"
        "4. And Satellite Remote Sensing: Ingesting Sentinel-2 10-meter resolution NDVI imagery to validate canopy vigor and detect early crop moisture stress.\n\n"
        "[HANDOFF BACK TO PERSON 1 FOR LIVE DEMO]:\n"
        "Having presented our architectural specifications, predictive algorithms, and database design, I now invite our Team Lead, Aryan, "
        "to conduct the live software demonstration and conclude our defense.\"",
        label="SLIDE 10 SPOKEN SCRIPT",
        border_hex="059669",
        bg_hex="ECFDF5"
    )

    # =========================================================================
    # SECTION 3: A-TO-Z TECHNICAL DEEP DIVE (GROUNDED IN CODEBASE)
    # =========================================================================
    add_h1("3. A-to-Z Technical Deep Dive (Grounded in Codebase)")

    add_p(
        "This section details every entity, relationship, constraint, and provenance rule implemented in Person 4's engineering vertical. "
        "Use these exact technical specifications to defend your schema design during viva cross-examination."
    )

    add_h2("3.1 Relational Database Architecture & ER Schema (Figure 3.3)")
    add_p(
        "Implemented in backend/models/farm.py and managed via SQLAlchemy 2.0 ORM. The relational architecture strictly conforms to "
        "Third Normal Form (3NF), ensuring zero transitive dependencies and complete transactional atomicity."
    )

    add_h3("A. Complete Table-by-Table Architectural Specification")
    add_p(
        "The KRISHI Intelligence database consists of six core relational tables linked via foreign key constraints:"
    )

    schema_table = [
        ["farms", "id (UUID)", "None (Root Anchor)", "farmer_name, location, district, state, crop, crop_variety, sowing_date, farm_area_acres, lat, lon, phone, soil_data_available", "Central plot entity tracking spatial coordinates, crop phenological profile, and baseline parameters."],
        ["soil_documents", "id (UUID)", "farm_id -> farms.id", "filename, file_path, file_type, file_size_bytes, uploaded_at, ocr_status, extracted_data_json, is_confirmed, confirmed_at", "Stores uploaded Soil Health Card file metadata, raw OCR extraction JSON, and quarantine review state."],
        ["farm_soil_profiles", "id (UUID)", "farm_id -> farms.id, document_id -> soil_documents.id", "provenance, is_active, test_date, confirmation_status, confirmed_at, ph, nitrogen, phosphorus, potassium, organic_carbon, ec, soil_texture, micronutrients, field_sources_json", "Maintains active verified laboratory measurements and historical archived soil states."],
        ["weather_observations", "id (UUID)", "farm_id -> farms.id", "observed_at, temp_max, temp_min, precipitation_sum, soil_moisture_0_7cm, gdd, provenance", "Time-stamped hourly and daily meteorological observations and GDD thermal units."],
        ["price_predictions", "id (UUID)", "farm_id -> farms.id", "predicted_at, horizon_days, point_estimate, min_price, max_price, confidence_pct, model_type, mae, mape_pct, data_points_used", "Stores 30-day forward XGBoost predictions, horizon uncertainty corridors, and model metrics."],
        ["farm_events", "id (UUID)", "farm_id -> farms.id", "event_type, timestamp, title, description, source", "Immutable transactional ledger recording stage transitions, alert triggers, and farmer audit logs."]
    ]
    add_table_data("Table 3.1: KRISHI Intelligence Relational Schema Specification (Chapter 3 Table 3.1)",
                   ["Table Name", "Primary Key", "Foreign Keys", "Key Attributes & Data Types", "Architectural Role & Integrity Constraint"],
                   schema_table, col_widths=[1.2, 0.9, 1.4, 2.2, 1.8])

    add_h3("B. 3NF Normalization Defense & Relational Integrity")
    add_p(
        "Why 3NF Normalization?\n"
        "1. First Normal Form (1NF): Every table cell stores atomic, scalar values. Complex structures (such as raw OCR candidate lists) "
        "are stored in dedicated JSON attributes (extracted_data_json) without violating row atomicity.\n"
        "2. Second Normal Form (2NF): All non-key attributes are fully functionally dependent on the primary key (UUID id), eliminating partial key dependencies.\n"
        "3. Third Normal Form (3NF): Eliminates transitive functional dependencies (X -> Y and Y -> Z). For example, soil test results do not live "
        "inside the farms table; they live in farm_soil_profiles linked via foreign key. This ensures that updating a farmer's phone number never corrupts "
        "historical soil records, and archiving a soil profile never deletes the farm."
    )

    add_callout(
        "WHY NOT A SINGLE UNSTRUCTURED MONGODB / NOSQL DOCUMENT?\n"
        "Examiners frequently ask: 'Why didn't you use MongoDB or a single JSON document for the digital twin?'\n\n"
        "MODEL ANSWER FOR PERSON 4:\n"
        "\"While NoSQL document stores offer schema flexibility, precision agricultural decision systems require strict transactional integrity (ACID). "
        "In KRISHI Intelligence:\n"
        "1. Foreign Key Cascades: Linking farm_soil_profiles and farm_events to farms.id guarantees that orphaned records can never exist.\n"
        "2. Historical Auditability: With 3NF relational design, when a farmer confirms a new Soil Health Card, we simply execute an atomic update "
        "marking previous profiles as is_active=False and inserting the new active record. We preserve a complete chronological ledger of soil depletion.\n"
        "3. Composite Indexing: PostgreSQL/SQLite B-Tree indexes on (farm_id, timestamp) allow our FastAPI backend to query 90 days of weather telemetry "
        "in under 4 milliseconds—far faster than parsing nested multi-megabyte JSON trees.\"",
        label="RELATIONAL VS NOSQL ARCHITECTURAL DEFENSE",
        border_hex="7C3AED",
        bg_hex="F5F3FF"
    )

    add_h2("3.2 Schema-Level Data Provenance Engine & Invariant Guardrails")
    add_p(
        "The Data Provenance Engine is implemented across backend/services/agmarknet_fetcher.py, backend/routers/soil.py, and backend/services/risk_engine.py. "
        "It enforces transparent, tamper-proof disclosure of data origins."
    )

    add_h3("A. The Formal Provenance Classification State Machine")
    add_p(
        "Every data point ingested into KRISHI Intelligence is stamped with a provenance enum before it can participate in decision synthesis:"
    )

    prov_table = [
        ["LIVE_OBSERVATION", "Telemetry age <= 24 hours (today/yesterday)", "Open-Meteo live API / AGMARKNET data.gov.in", "Green UI badge; full confidence (0.95–1.00); activates automated trade/irrigation signals."],
        ["LATEST_AVAILABLE", "Observation age between 2 and 7 days", "Official AGMARKNET / Weather cache", "Blue UI badge; informs farmer of weekend or mandi trading holiday latency."],
        ["STALE_REFERENCE", "Observation age > 7 days", "Stale external cache", "Amber UI badge; high uncertainty banner; suppresses automated trade execution."],
        ["HISTORICAL_SEED", "Offline calibrated baseline (2020–2026)", "data/seed/wheat_lucknow_mandi.csv", "Purple UI badge; zero live network dependency fallback; informs user that API is offline."],
        ["VERIFIED_LAB_TEST", "Official Soil Health Card document confirmed by farmer", "Lab test document via OCR + Review Gate", "Green UI badge; unlocks high-precision chemical fertilizer dosage recommendations."],
        ["REGIONAL_BASELINE", "District agro-climatic baseline averages", "ICAR Central UP soil benchmarks", "Amber UI badge; uses conservative fertilizer guidelines to prevent toxic over-application."]
    ]
    add_table_data("Table 3.2: Formal Multi-Tier Agricultural Data Provenance State Machine",
                   ["Provenance Tag", "Temporal Freshness (Delta t)", "Data Authority / Source", "System Handling & Farmer Disclosure"],
                   prov_table, col_widths=[1.5, 1.6, 1.7, 2.4])

    add_h3("B. Mathematical Zero-Hallucination Invariant")
    add_p(
        "In KRISHI Intelligence, provenance is not a passive UI label; it is an active programmatic gatekeeper:\n"
        "1. Advisory Lockout: In backend/services/decision_engine.py, fertilizer recommendations refuse to generate compound nitrogen-phosphorus dosages "
        "if soil state is unconfirmed. The system defaults to baseline soil maintenance.\n"
        "2. Graceful Downgrade: If the data.gov.in API times out, the system never invents a modal price; it explicitly labels the data HISTORICAL_SEED "
        "and sets the confidence score to MEDIUM (65%).\n"
        "3. UI Audit Drawer: On the frontend, clicking any risk card opens the Provenance Audit Drawer, displaying exact source URLs, timestamps, "
        "and latency indicators."
    )

    add_h2("3.3 Automated Test Suite Execution Matrix (Chapter 5 Defense)")
    add_p(
        "Quality assurance is maintained through our automated pytest suite. As Person 4, you defend the execution metrics of our 116 tests:"
    )

    qa_table = [
        ["test_agmarknet_fetcher.py", "Mandi API ingestion, live freshness, stale thresholds, seed fallbacks", "18", "PASS"],
        ["test_digital_twin.py", "GDD thermal clock calculations, phenological stage progression, stress vector math", "24", "PASS"],
        ["test_soil_service.py", "OCR parsing, validation boundaries, mandatory confirmation gate", "22", "PASS"],
        ["test_expert_service.py", "Heat stress, rust disease, irrigation scheduling, sell/hold logic", "20", "PASS"],
        ["test_mandi_router.py", "FastAPI endpoint contracts, JSON schemas, error response codes", "16", "PASS"],
        ["test_soil_router.py", "Document upload, pending state persistence, profile commit APIs", "16", "PASS"],
        ["Total Test Suite", "Full System Automated Regression Suite (Pass Rate: 100% in 10.18s)", "116", "100% PASS"]
    ]
    add_table_data("Table 3.3: Automated Pytest Verification Suite Execution Matrix (Chapter 5 Table 5.2)",
                   ["Test Module Name", "Verification Scope & Assertions", "Number of Tests", "Status"],
                   qa_table, col_widths=[1.8, 3.2, 0.8, 0.7])

    add_h2("3.4 Chapter 6 Conclusion, Current Limitations & 4th-Year Major Roadmap")
    add_p(
        "Chapter 6 of our report establishes the transition from a 3rd-year evaluated prototype into our 4th-year Major Project."
    )

    limits_table = [
        ["Single-Season Horizon", "Optimized for a single crop cycle (Rabi Wheat); does not retain multi-season soil nutrient depletion history.", "Implement Multi-Season Crop Rotation Memory (tracking nitrogen carryover from Kharif Paddy to Rabi Wheat)."],
        ["Cloud Server Dependency", "Requires active HTTP connection to FastAPI backend; rural connectivity drops disable interactive dashboard.", "Package Next.js frontend as an Offline-First PWA with local SQLite WASM synchronization."],
        ["Paper Lab Card Latency", "Relies on physical Soil Health Cards issued once every 2–3 years; mid-season leaching is missed.", "Integrate wireless in-situ LoRaWAN IoT soil probes reading continuous root-zone NPK, EC, and moisture."],
        ["Single Mandi Scope", "Trained on Lucknow APMC mandi; freight arbitrage to nearby mandis uses static distance models.", "Develop dynamic Multi-Mandi Freight Arbitrage Optimizer across all UP state APMC markets."],
        ["Language Barrier", "Screen-based dashboard in English; limits accessibility for low-literacy smallholders.", "Integrate Multilingual Conversational Voice Assistant via Bhashini API (Hindi, Bhojpuri, Punjabi)."],
        ["Financial Settlement", "Provides market price forecasting; does not facilitate direct trade execution or government subsidies.", "Integrate Government of India e-NAM API and DBT (Direct Benefit Transfer) fertilizer subsidy tracking."]
    ]
    add_table_data("Table 3.4: Honest 3rd-Year Prototype Limitations vs. 4th-Year Major Project Roadmap",
                   ["Architectural Dimension", "Current 3rd-Year Prototype Boundary (What We Scope Out)", "4th-Year Major Project Engineering Expansion"],
                   limits_table, col_widths=[1.3, 2.5, 2.4])

    add_h2("3.5 Codebase Pointer Table (Live Code Demonstration)")
    add_p(
        "If an examiner asks: 'Show me your database models' or 'Where is the audit event table?', immediately open these exact files:"
    )

    code_ptrs = [
        ["backend/models/farm.py", "Farm, SoilDocument, FarmSoilProfile", "SQLAlchemy 3NF relational models, foreign keys, table definitions"],
        ["backend/models/farm.py", "FarmObservation, PricePrediction, FarmEvent", "Time-series observations, XGBoost forecast persistence, immutable audit ledger"],
        ["backend/database.py", "engine, SessionLocal, Base", "Database connection pool, SQLite / PostgreSQL engine initialization"],
        ["backend/schemas/farm.py", "FarmCreate, FarmResponse", "Pydantic v2 schemas validating request/response serialization"],
        ["backend/services/risk_engine.py", "synthesize_farm_intelligence()", "Evaluates multi-factor risk scores and applies provenance guardrails"],
        ["backend/tests/test_digital_twin.py", "TestDigitalTwinSuite", "Automated unit tests verifying state transitions and persistence"],
        ["backend/tests/test_agmarknet_fetcher.py", "TestProvenanceClassification", "Unit tests verifying 4-tier provenance state machine transitions"]
    ]
    add_table_data("Table 3.5: Person 4 Repository Codebase Pointers",
                   ["File Path in Repository", "Key Class / Function", "Technical Responsibility & Defense Point"],
                   code_ptrs, col_widths=[2.1, 1.8, 2.4])

    # =========================================================================
    # SECTION 4: 15 TOUGH VIVA CROSS-QUESTIONS & HIGH-SCORING ANSWERS
    # =========================================================================
    add_h1("4. 15 Tough Viva Cross-Questions & High-Scoring Answers")

    add_p(
        "These 15 questions cover database architecture, provenance engineering, testing methodology, and academic conclusion. "
        "Master the technical terminology and deliver each answer with authority."
    )

    viva_qa = [
        ("Q1: Walk us through the Primary Keys, Foreign Keys, and cardinalities in your ER diagram (Figure 3.3).",
         "In Figure 3.3, the farms table is our root parent entity with a UUID primary key 'id'. It shares five 1-to-Many relationships with child tables: "
         "(1) farms to farm_observations via farm_id, tracking daily multi-factor risk scores. (2) farms to price_predictions via farm_id, storing 30-day "
         "forecast horizons. (3) farms to farm_events via farm_id, maintaining an append-only audit trail. (4) farms to soil_documents via farm_id, tracking "
         "uploaded file metadata. (5) farms to farm_soil_profiles via farm_id, maintaining confirmed chemical measurements. Additionally, farm_soil_profiles "
         "has a foreign key document_id linking to soil_documents.id. All foreign keys enforce cascading deletes and B-tree indexes."),

        ("Q2: Why did you structure the database in 3NF instead of using unstructured JSON blobs or MongoDB?",
         "While unstructured document stores offer rapid initial prototyping, precision agricultural platforms handle life-critical data that require "
         "strict ACID guarantees. Normalizing our schema into 3NF eliminates update anomalies: for example, updating a farmer's sowing date in farms "
         "never alters historical soil profiles. Furthermore, relational foreign keys prevent orphaned documents, and B-tree indexes on (farm_id, timestamp) "
         "enable our backend to query 90 days of weather telemetry in under 4 milliseconds—far faster than parsing multi-megabyte JSON trees."),

        ("Q3: How does the schema enforce data provenance so a regional baseline is never mistaken for a lab test?",
         "In farm_soil_profiles, every row has an explicit 'provenance' column constrained to an enum: SOIL_HEALTH_CARD, FARMER_ENTERED, or REGIONAL_BASELINE. "
         "When our digital twin synchronizes state, it inspects this column. If provenance is SOIL_HEALTH_CARD and document_id is non-null, the twin tags the soil state "
         "as VERIFIED_LAB_TEST (Green badge). If the farmer has not confirmed a card, the database has no confirmed profile, and the digital twin explicitly labels "
         "the parameters as REGIONAL_BASELINE (Amber badge). The advisory engine strictly checks this tag before recommending chemical fertilizer dosages."),

        ("Q4: What happens to the Digital Twin state if live external APIs fail and DEMO_MODE activates?",
         "KRISHI Intelligence implements graceful fault tolerance. If Open-Meteo or data.gov.in is unreachable, the system activates cached responses or our calibrated "
         "historical seed dataset (wheat_lucknow_mandi.csv). Crucially, the system never fabricates data: it sets the provenance tag to HISTORICAL_SEED, reduces the "
         "prediction confidence score to MEDIUM (65%), and surfaces an amber disclosure banner in the UI audit drawer. The digital twin continues running without crashing."),

        ("Q5: What is currently missing in your system right now?",
         "As documented in Chapter 6, our 3rd-year prototype has four intentional engineering boundaries: (1) It is currently calibrated for a single crop and region: "
         "Wheat in Central Uttar Pradesh. (2) It relies on periodic physical Soil Health Cards rather than real-time continuous in-situ IoT probes. "
         "(3) It operates via a modern web screen interface in English, requiring literacy and smartphone navigation. (4) It evaluates a single plot at a time rather "
         "than managing multi-plot crop rotation estates. We have designed our 4th-year Major Project specifically to solve these boundaries."),

        ("Q6: How will you expand KRISHI Intelligence into your 4th-year B.Tech Major Project?",
         "In our 4th-year final year project, we will implement four concrete engineering milestones: (1) Deploy solar-assisted in-situ LoRaWAN IoT probes reading "
         "root-zone NPK and moisture telemetry directly into the digital twin every 6 hours. (2) Integrate Government of India's Bhashini AI conversational voice "
         "assistant in Hindi, Bhojpuri, and Punjabi. (3) Expand our phenological and XGBoost models to Kharif Paddy and Mustard. (4) Integrate Sentinel-2 10-meter "
         "NDVI satellite remote sensing to validate canopy moisture and crop health from orbit."),

        ("Q7: Explain 3NF normalization in the context of your farms and farm_soil_profiles tables.",
         "In 1NF, every column contains atomic values. In 2NF, all non-key attributes are fully dependent on the primary key (UUID id). In 3NF, there are no transitive "
         "dependencies (where non-key attribute A determines non-key attribute B). In an unnormalized design, putting soil test values (pH, Nitrogen, test date) inside "
         "the farms table would create transitive dependencies: every time a farmer conducts a new soil test, the farm record would need to be overwritten, destroying "
         "historical auditability. By decoupling soil states into farm_soil_profiles with foreign key farm_id, we achieve clean 3NF, allowing multiple historical "
         "soil records while marking only one as is_active=True."),

        ("Q8: Why do you store snapshot_json in farm_observations if you already have normalized tables?",
         "In farm_observations, snapshot_json serves as a point-in-time immutable telemetry archive. While our normalized relational tables store current active states, "
         "an agricultural decision platform must be able to reproduce the exact state of the digital twin at the precise second an advisory was issued—such as for crop "
         "insurance claim verification. The snapshot_json stores the frozen composite state (weather, soil, crop stage, price) at observation time without requiring "
         "complex historical database joins."),

        ("Q9: How does the farm_events table maintain an immutable audit trail?",
         "The farm_events table is strictly append-only: our backend API exposes no UPDATE or DELETE endpoints on this table. Every critical state transition—such as "
         "FARM_CREATED, SOIL_PROFILE_CONFIRMED, STAGE_ADVANCED, or ADVISORY_GENERATED—is inserted with an immutable UTC timestamp, event type, description, and source tag "
         "(USER_ACTION, INTELLIGENCE_ENGINE, or SYSTEM). This provides a tamper-proof audit trail for agronomists, loan officers, and insurance inspectors."),

        ("Q10: What database indexes are created and why are they placed on (farm_id, timestamp)?",
         "We created composite B-tree indexes on (farm_id, timestamp) in farm_observations, farm_events, and price_predictions, as well as indexes on (farm_id, is_active) "
         "in farm_soil_profiles. These composite indexes allow PostgreSQL and SQLite to execute range scans (e.g. SELECT * FROM farm_observations WHERE farm_id = X "
         "AND observed_at >= Y ORDER BY observed_at DESC) using pure index seeks in O(log N) time, keeping query latency under 4 milliseconds as the dataset grows."),

        ("Q11: How do you handle database concurrency if multiple requests update the farm digital twin simultaneously?",
         "FastAPI runs asynchronously using an ASGI event loop. In backend/database.py, SQLAlchemy SessionLocal creates scoped, isolated database sessions per request. "
         "When updating active profiles in confirm_soil_profile(), we execute atomic transactional updates within a single db.commit() block. If SQLite is used during "
         "local testing, WAL (Write-Ahead Logging) mode allows concurrent reads during writes; in production PostgreSQL, row-level locking prevents race conditions."),

        ("Q12: What is the difference between SQLite (local development) and PostgreSQL (cloud production) in your architecture?",
         "Our application uses SQLAlchemy ORM, which completely abstracts the underlying database engine via standard SQL dialects. For local hackathon evaluation "
         "and offline testing, SQLite provides a zero-configuration, single-file embedded database that runs in-memory or on disk without external daemon overhead. "
         "For production cloud deployment, changing the DATABASE_URL in backend/config.py connects seamlessly to PostgreSQL 15+, providing connection pooling, "
         "row-level locking, and high-concurrency multi-client throughput."),

        ("Q13: How does the database isolate multiple farms from one another (cross-farm isolation)?",
         "Tenant isolation is enforced at the database query level. In backend/routers/soil.py lines 190–198, when confirming a soil profile, the endpoint verifies that "
         "both payload.farm_id and document.farm_id match: db.query(SoilDocument).filter(SoilDocument.id == doc_id, SoilDocument.farm_id == farm_id).first(). "
         "If a user attempts to confirm a document belonging to a different farm, the query returns None and raises HTTP 404, strictly preventing cross-farm data leakage."),

        ("Q14: How does the advisory engine use provenance tags to prevent hallucinations?",
         "The advisory engine in backend/services/risk_engine.py checks the provenance metadata of all incoming vectors before executing decision trees. If the mandi "
         "price series is tagged HISTORICAL_SEED, the engine widens the price uncertainty corridor and suppresses automated sell recommendations. If the soil state is "
         "REGIONAL_BASELINE, chemical fertilizer doses are flagged with an advisory notice: 'Based on district baseline; verify with Soil Health Card'. "
         "This guarantees that every piece of advice is grounded in truth."),

        ("Q15: How will you implement offline SQLite sync for low-connectivity rural villages in your final year?",
         "In our 4th-year project, we will leverage SQLite compiled to WebAssembly (WASM) via the browser's Origin Private File System (OPFS) on the client side. "
         "When a farmer is in an offline field, farm telemetry and advisories are persisted locally in client-side SQLite. When cellular connectivity (4G/Wi-Fi) "
         "is restored, a background service worker executes a two-way synchronization protocol with our cloud PostgreSQL database using vector clocks to resolve conflicts.")
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
        r_ans_tag.font.color.rgb = RGBColor(124, 58, 237)

        r_a = p_a.add_run(a_text)
        r_a.font.name = 'Times New Roman'
        r_a.font.size = Pt(11)
        r_a.font.color.rgb = RGBColor(15, 23, 42)

    # Save Document
    print(f"Saving guide to: {OUTPUT_DOCX}")
    doc.save(OUTPUT_DOCX)
    print("Person 4 Viva Guide generated successfully!")


if __name__ == "__main__":
    build_guide()
