"""
scripts/build_viva_guide_p1.py
Generates the comprehensive Academic Viva & Presentation Guide for Person 1 (Aryan - Lead Architect & Demo Runner).
Document output: docs/viva_guides/Person_1_Lead_Architect_and_Demo_Guide.docx
Strictly formatted according to academic guidelines using python-docx.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "docs", "viva_guides")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_DOCX = os.path.join(OUTPUT_DIR, "Person_1_Lead_Architect_and_Demo_Guide.docx")


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
    print("Building Person 1 Viva & Demo Guide...")
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
        r_hdr = p_hdr.add_run("KRISHI Intelligence — Academic Viva Guide | Person 1 (Lead Architect & Demo)")
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
        run.font.color.rgb = RGBColor(30, 58, 138) # Navy Blue
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
        for r_idx, row in enumerate(data):
            row_cells = table.rows[r_idx + 1].cells
            fill_bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row):
                row_cells[c_idx].text = str(val)
                set_cell_background(row_cells[c_idx], fill_bg)
                set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
                p = row_cells[c_idx].paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                align = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 4] else WD_ALIGN_PARAGRAPH.LEFT
                p.alignment = align
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(9.0)
                    r.font.color.rgb = RGBColor(15, 23, 42)

        if col_widths:
            for row in table.rows:
                for c_idx, w in enumerate(col_widths):
                    row.cells[c_idx].width = Inches(w)

        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(0)
        p_after.paragraph_format.space_after = Pt(6)

    # =========================================================================
    # TITLE & HEADER
    # =========================================================================
    add_p("KRISHI INTELLIGENCE — B.TECH MINI PROJECT VIVA & DEFENSE GUIDE", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2, color=RGBColor(30, 58, 138))
    add_p("EXCLUSIVELY FOR PERSON 1: ARYAN (LEAD ARCHITECT & LIVE DEMO RUNNER)", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4, color=RGBColor(71, 85, 105))
    add_p("Department of Computer Science and Engineering | KCC Institute of Technology & Management (CC 492), Greater Noida\nAffiliated to Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow",
          size=10.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

    add_callout(
        "This master preparation guide equips Person 1 (Aryan - Team Lead) with an exhaustive, word-for-word spoken presentation script, "
        "step-by-step live demo click paths, deep architectural defense arguments, and answers to 15 tough examiner cross-questions. "
        "Every explanation is grounded in the actual codebase, schemas, and algorithms of KRISHI Intelligence.",
        label="EXECUTIVE VIVA STRATEGY"
    )

    # =========================================================================
    # SECTION 1: ROLE & OWNERSHIP MATRIX
    # =========================================================================
    add_h1("1. Role & Ownership Matrix (Person 1 — Aryan)")

    add_p(
        "As the Team Lead and Lead Software Architect, Person 1 anchors the presentation, establishes the academic framing, "
        "explains the end-to-end system orchestration, executes the live software demo, and delivers the closing defense. "
        "Person 1 also owns the academic documentation for Chapter 1 and the final compilation of the KCC Project Report."
    )

    headers_role = ["Domain / Phase", "Assigned Presentation Ownership", "Key Deliverables & Code Artifacts", "Handoff Partner"]
    data_role = [
        [
            "Phase 1: Opening\n(Slides 1–3, ~2.5m)",
            "Project Title, Problem Statement, Literature Review & Comparison, High-Level System Architecture.",
            "Chapter 1 of KCC Report, Fig. 3.1 Architecture Diagram, Table 1.1 Comparative Matrix.",
            "Handoff to Person 2\n(Tech Stack & ML)"
        ],
        [
            "Phase 2: Core Engineering\n(Person 1's Module)",
            "Multi-Agent Orchestration, Living Farm Digital Twin State Machine, Multi-Factor Risk Synthesis Engine.",
            "backend/services/risk_engine.py\nbackend/services/decision_engine.py\nfrontend/src/app/farm/[id]/page.tsx",
            "Coordinates team integration"
        ],
        [
            "Phase 3: Live Demo\n(Closing, ~3.0m)",
            "Live browser demonstration: Onboarding, Digital Twin state sync, Mandi net realization, OCR review gate, Sell vs Hold.",
            "run.bat, Next.js frontend (localhost:3000), FastAPI backend (localhost:8000), sample Soil Card.",
            "Receives handoff from Person 4"
        ],
        [
            "Phase 4: Defense & Scope\n(Closing, ~1.0m)",
            "Current 3rd-year architectural boundaries, 4th-year Major Project upgrade roadmap, viva cross-questions.",
            "Chapter 6 of KCC Report, Table 6.1 Limitations vs Roadmap, viva defense cards.",
            "Leads whole-team Q&A"
        ],
        [
            "Documentation Pillar",
            "Chapter 1 (Introduction, Objectives, Scope, Lit Review) & Final KCC Project Report compilation.",
            "docs/KRISHI_Intelligence_KCC_Report.docx (3.72 MB, 11 Figures, 6 Tables, Times New Roman 12pt).",
            "Submitted to Guide & HOD"
        ]
    ]
    add_table_data("Table 1.1: Comprehensive Ownership & Responsibilities of Person 1", headers_role, data_role, [1.4, 1.8, 1.8, 1.0])

    add_h2("1.1 Team Coordination & Verbal Handoff Protocols")
    add_p(
        "Examiners grade team coordination heavily. Transitions between speakers must be sharp, professional, and natural. "
        "Below are the exact verbal cues Person 1 must use:"
    )

    add_callout(
        "\"...Now that we have established how KRISHI's multi-agent orchestrator unifies weather, soil, and market streams into a Living Digital Twin, "
        "I will hand over to Person 2 to unpack our Software Specifications, Open-Meteo agro-weather telemetry, and the mathematical formulation of our XGBoost Mandi Price Forecaster. Person 2, over to you.\"",
        label="OUTGOING HANDOFF 1: PERSON 1 -> PERSON 2 (AT END OF SLIDE 3)"
    )

    add_callout(
        "\"Thank you Person 4 for demonstrating our 100% test pass rate and SQLite schema integrity. Respected evaluators, code and schemas tell only half the story. "
        "I will now transition to the live running application to demonstrate how a farmer in Malihabad, Lucknow interacts with this intelligence in real time...\"",
        label="INCOMING HANDOFF 2: PERSON 4 -> PERSON 1 (START OF LIVE DEMO)"
    )

    # =========================================================================
    # SECTION 2: WORD-FOR-WORD PRESENTATION & LIVE DEMO SCRIPT
    # =========================================================================
    add_h1("2. Word-for-Word Spoken Presentation & Live Demo Script")

    add_h2("2.1 Part A: Opening Speech (Slides 1–3, Exactly 2.5 Minutes)")

    add_p("**[SLIDE 1: TITLE & COVER PAGE]**", bold=True, color=RGBColor(30, 58, 138))
    add_p(
        "\"Good morning respected external examiners, Head of Department [HOD Name], project supervisor [Guide Name], and faculty members. "
        "My name is Aryan Sharma, and along with my team members, we present our 3rd-Year B.Tech Mini Project: "
        "'KRISHI INTELLIGENCE: Multi-Factor Agro-Climatic Digital Twin with Dynamic Provenance Guardrails and Market Price Forecasting'. [PAUSE 2 SECONDS]"
    )
    add_p(
        "In India, smallholder farmers holding less than 2 hectares represent over 85% of cultivable land in states like Uttar Pradesh. "
        "Yet, every season, a wheat farmer faces three completely decoupled uncertainties: unseasonal weather shocks, volatile mandi price collapse, "
        "and blind fertilizer dosage. Our project builds a stateful, physics-informed decision intelligence engine that resolves these decoupled problems into a single actionable truth.\""
    )

    add_p("**[SLIDE CHANGE -> SLIDE 2: PROBLEM STATEMENT & LITERATURE SURVEY]**", bold=True, color=RGBColor(30, 58, 138))
    add_p(
        "\"Respected panel, before writing a single line of code, our team conducted an exhaustive literature survey across existing agricultural solutions, summarized here in our Comparative Matrix. [PAUSE 1 SECOND]"
    )
    add_p(
        "First, traditional government systems like Kisan Suvidha or ICAR text bulletins offer static, calendar-based advice. They do not know what stage the farmer's crop is at today. "
        "Second, computer vision apps like Plantix diagnose leaf diseases from photos, but offer zero market pricing intelligence or weather-adjusted harvest scheduling. "
        "Third, commercial IoT ERPs like Climate FieldView or Cropin deploy in-field hardware probes costing ₹25,000 to ₹50,000 per acre—completely unaffordable for Indian smallholders. "
        "Finally, recent generative AI chatbots like KisanGPT rely on black-box LLMs that frequently hallucinate chemical dosages—recommending lethal fertilizer quantities or fabricating non-existent mandi rates. [PAUSE 2 SECONDS]"
    )
    add_p(
        "KRISHI Intelligence bridges this gap with zero hardware cost. We synthesize open satellite and reanalysis feeds, verified APMC mandi records, and physical Soil Health Cards into a stateful Digital Twin governed by strict mathematical provenance guardrails.\""
    )

    add_p("**[SLIDE CHANGE -> SLIDE 3: SYSTEM ARCHITECTURE & AGENT ORCHESTRATION]**", bold=True, color=RGBColor(30, 58, 138))
    add_p(
        "\"On Slide 3, you see the five-tier system architecture of KRISHI Intelligence. "
        "At the foundation, Layer 1 handles external ingestion: Open-Meteo for 14-day hourly agro-weather, data.gov.in AGMARKNET for commodity prices, and user-uploaded Soil Health Cards. "
        "Layer 2 enforces our core innovation: Provenance Guardrails. We refuse to treat historical data as live, and we refuse to treat raw OCR as confirmed lab data. [PAUSE 1 SECOND]"
    )
    add_p(
        "Layer 3 maintains our central entity: the Living Farm Digital Twin. Implemented in our DigitalTwinEngine, it accumulates daily Growing Degree Days (GDD) with base temperature 4.0°C, "
        "advancing the wheat crop through 8 distinct physiological stages—from Crown Root Initiation to Maturity. "
        "Layer 4 runs our predictive and diagnostic engines: an XGBoost Regressor forecasting 30-day mandi prices with 80% and 95% confidence intervals, coupled with our Multi-Factor Risk Synthesizer. "
        "Finally, Layer 5 delivers actionable cards to the farmer via a reactive Next.js 14 dashboard. [PAUSE 1 SECOND]"
    )
    add_p(
        "To explain our software stack, weather integration, and machine learning formulation, I now hand over to Person 2. Person 2, please take over.\""
    )

    # -------------------------------------------------------------------------
    # PART B: LIVE DEMO
    # -------------------------------------------------------------------------
    add_h2("2.2 Part B: Closing Live Demo Narration (~3 Minutes, Grounded in Real UI)")

    add_callout(
        "Ensure both servers are running via run.bat before your turn. "
        "Keep two tabs ready: Tab 1 = http://localhost:3000 (Next.js Dashboard), Tab 2 = http://localhost:8000/docs (FastAPI Swagger). "
        "Follow the exact sequence below with confident mouse clicks.",
        label="DEMO PRE-FLIGHT CHECK"
    )

    add_p("**[TRANSITION FROM PERSON 4 -> ARYAN TAKES CONTROL OF MOUSE & SCREEN]**", bold=True, color=RGBColor(30, 58, 138))
    add_p(
        "\"Thank you Person 4. Respected examiners, I will now demonstrate the live running KRISHI Intelligence platform. "
        "Here on my screen is our Next.js web application running on port 3000, communicating asynchronously with our FastAPI backend on port 8000.\""
    )

    add_p("**[CLICK 1: HOME PAGE -> ONBOARDING / SELECT FARM]**", bold=True)
    add_p(
        "\"We begin on the dashboard for 'Aryan's Farm', located in Malihabad, Lucknow, cultivating 3.5 acres of HD-2967 Wheat sown on November 15. "
        "Notice the header: the system calculates the crop is at Day 369 (Post-harvest stage). "
        "Immediately, the executive card shows an AI Recommendation: 'Sell within the next 3 days' with Medium Confidence. "
        "Notice the transparency: it tells the farmer that the predicted near-term price of ₹2,544 is ₹61 below reference, and selling today avoids depreciation, securing ₹7,177 in higher net realization.\""
    )

    add_p("**[CLICK 2: NAVIGATION -> TAB 2: DIGITAL TWIN (`/farm/[id]/digital-twin`)]**", bold=True)
    add_p(
        "\"Next, I click on the 'Digital Twin' tab. Here is our living computational state machine. "
        "Observe the Synchronized Farm Intelligence cards: "
        "Our weather stream is LIVE at 22.9°C with 0mm rain risk. "
        "Our soil state shows Sandy Loam with 74% suitability based on our regional baseline. "
        "Our mandi benchmark shows ₹2,605 per quintal. [PAUSE 1 SECOND]"
    )
    add_p(
        "Now look at the Data Provenance & Proven State table below: "
        "Every single metric discloses its data provider, provenance status, and audit description. "
        "Weather is tagged LIVE. Soil is tagged REGIONAL_ESTIMATE. Mandi price is tagged HISTORICAL_SEED. "
        "Down at the bottom is our immutable Farm Events Timeline, showing timestamped events: Farm Registered and Intelligence Analysis Completed. "
        "Every state change is persisted to our SQLite database.\""
    )

    add_p("**[CLICK 3: NAVIGATION -> TAB 5: MARKET INTELLIGENCE (`/farm/[id]/market`)]**", bold=True)
    add_p(
        "\"Now let's examine Market Intelligence. Look at the top banner: "
        "'Showing calibrated regional mandi benchmark data (2020–2026 APMC baseline). Offline resilience mode active.' "
        "Because we did not inject a live government API key, our system refuses to fake a live connection. "
        "Below is our 3-Year Price History chart, plotting 157 weekly observations. [PAUSE 1 SECOND]"
    )
    add_p(
        "Now look at our Nearby Mandi Comparison table—this is a key agronomic innovation. "
        "Notice that Rae Bareli Mandi has a higher nominal price of ₹2,645/quintal. But Rae Bareli is 82 km away, incurring ₹48 in transport costs, yielding a net realization of ₹2,597. "
        "Meanwhile, Lucknow Mandi at 0 km offers ₹2,605 net. "
        "Our decision engine automatically flags Lucknow as [BEST], saving the farmer from an unprofitable journey!\""
    )

    add_p("**[CLICK 4: NAVIGATION -> TAB 6: SOIL HEALTH CARD & CONFIRMATION GATE (`/farm/[id]/soil`)]**", bold=True)
    add_p(
        "\"Now I demonstrate our most critical safety feature: the Soil Health Card OCR Human-in-the-Loop Confirmation Gate. "
        "Currently, our farm is using a regional district baseline with an initial suitability score of 74/100. "
        "I click 'Upload Soil Health Card'. In our test, if a farmer uploads an invalid document or a meme, the OCR safely flags 'OCR FAILED'—it refuses to fabricate numbers. "
        "Instead, it switches the source tags to 'FARMER' and allows manual entry from their physical card. [PAUSE 1 SECOND]"
    )
    add_p(
        "Earlier, we confirmed our verified laboratory values: pH 7.2, Nitrogen 290 kg/ha, Phosphorus 25 kg/ha, and EC 0.7 dS/m. "
        "As soon as we clicked 'Confirm Soil Data', notice what happened: "
        "The badge upgraded to 'FARMER ENTERED'. The test date was recorded. "
        "And look at the Crop Soil Suitability gauge on the right: it immediately recalculated from 74/100 to 82/100! "
        "Our digital twin reacted to real soil evidence!\""
    )

    add_p("**[CLICK 5: NAVIGATION -> TAB 3: DECISION CENTER (`/farm/[id]/decision`)]**", bold=True)
    add_p(
        "\"Finally, I open the Decision Center. Here is our Financial Scenario Matrix: "
        "It evaluates three real-world options: Sell Now (Today), Wait 7 Days, and Wait 15 Days. "
        "Notice the math: for 3.5 acres producing ~52.5 quintals, selling today yields ₹1,36,762 with zero storage cost. "
        "If the farmer waits 7 days, godown storage deducts ₹1,838, and rainfall dampness risk deducts ₹2,137, dropping net realization to ₹1,29,585. "
        "If they wait 15 days, net realization drops further to ₹1,24,382. "
        "The system highlights 'Sell Now' with a gold RECOMMENDED badge. This is quantitative decision support, not generic conversational text.\""
    )

    add_callout(
        "If college Wi-Fi drops during your demo, do NOT panic. Calmly say to the panel: "
        "\"Examiners, notice that even if the internet drops, KRISHI Intelligence does not crash. "
        "Our offline resilience architecture instantly falls back to our calibrated local seeds and in-memory Digital Twin cache with zero downtime.\" "
        "This turns a technical glitch into proof of enterprise resilience!",
        label="COLLEGE WI-FI EMERGENCY CONTINGENCY"
    )

    # -------------------------------------------------------------------------
    # PART C: LIMITATIONS & FUTURE SCOPE
    # -------------------------------------------------------------------------
    add_h2("2.3 Part C: Honest Limitations & 4th-Year Future Scope Pitch (~30 Seconds)")

    add_p(
        "\"Respected evaluators, in developing this 3rd-year Mini Project, we maintained strict engineering boundaries. "
        "Our current prototype intentionally focuses on the wheat monoculture in Central Uttar Pradesh, utilizes periodic lab soil cards rather than live IoT field probes, "
        "and is accessed via an English web dashboard. [PAUSE 1 SECOND]"
    )
    add_p(
        "For our 4th-year Major Project, we have already charted our engineering roadmap: "
        "1. Multi-Crop Expansion to Kharif Paddy and Rabi Mustard; "
        "2. A Vernacular Voice Interface in Hindi and regional dialects using Bhashini AI; "
        "3. Integration of Sentinel-2 10-meter satellite NDVI for canopy moisture tracking; and "
        "4. Edge deployment as a Progressive Web App (PWA) with offline SQLite synchronization. "
        "Thank you. My team and I are now open to your questions.\""
    )

    # =========================================================================
    # SECTION 3: TECHNICAL & ACADEMIC DEEP DIVE
    # =========================================================================
    add_h1("3. A-to-Z Technical & Academic Deep Dive (Grounded in Code)")

    add_h2("3.1 Chapter 1 & Synopsis Breakdown (Defending Chapter 1)")
    add_p(
        "Person 1 owns Chapter 1 of the KCC Project Report. If an examiner questions the premise or academic validity of your literature review, "
        "use the following structured arguments:"
    )
    add_p("• **The Smallholder Triad Problem**: 85% of UP farmers cultivate < 2 hectares. They cannot afford IoT sensors. They suffer from terminal heat shocks (>35°C during grain filling), post-harvest distress selling, and severe nitrogen over-application due to urea subsidies.")
    add_p("• **Project Objectives**: (1) Develop an in-memory Living Digital Twin tracking GDD phenology; (2) Implement strict Data Provenance Guardrails; (3) Train an XGBoost time-series forecaster with 80%/95% CIs; (4) Build an SHC OCR pipeline with mandatory human confirmation; (5) Build a reactive Next.js 14 dashboard.")
    add_p("• **Scope Boundaries**: Calibrated for Wheat (Triticum aestivum) in Lucknow, Hardoi, Sitapur, Barabanki, Unnao. Open-Meteo for weather, AGMARKNET for mandi prices, Ministry of Agriculture SHC templates.")

    add_h2("3.2 System Architecture & Multi-Agent Orchestration Explained")
    add_p(
        "When an examiner asks how KRISHI functions as an 'Agentic' or multi-agent platform, explain the decoupled service architecture:"
    )
    add_p("1. **Data Ingestion Agents**: Independent asynchronous workers continuously poll external providers: weather worker (`weather_service.py`), mandi worker (`agmarknet_fetcher.py`), and soil document parser (`soil_ocr_service.py`).")
    add_p("2. **Guardrail Evaluator Agents**: Before any metric enters the system, provenance workers classify freshness (`LIVE` vs `LATEST` vs `STALE` vs `HISTORICAL_SEED`) and enforce physical limits (pH 0–14, non-negative nutrients).")
    add_p(r"3. **Digital Twin Synchronizer**: The `DigitalTwinEngine` maintains the in-memory state representation of the farm, computing cumulative thermal units (GDD) and soil water depletion ($SM_t = SM_{t-1} + \text{Rain}_t - ET_0 \cdot K_c$).")
    add_p("4. **Decision Synthesis Agents**: The Risk Engine (`risk_engine.py`) aggregates thermal, moisture, and disease vectors. The Decision Engine (`decision_engine.py`) evaluates price trajectories against storage and weather risk penalties.")

    add_h2("3.3 Frontend UI & State Synchronization Explained")
    add_p(
        "The frontend is built on **Next.js 14 App Router** using React 18 and Tailwind CSS: "
        "• Server vs Client Components: High-level layouts are server-rendered for rapid first load (~94 kB JS), while interactive dashboards (`app/farm/[id]/page.tsx`, `app/farm/[id]/soil/page.tsx`) use `'use client'` for reactive state hooks (`useState`, `useEffect`). "
        "• Data Fetching Layer: Encapsulated in `frontend/src/lib/api.ts`, which normalizes API responses, injects authentication headers, handles connection dropouts gracefully, and maps provenance metadata to visual UI badges (`components/shared/DataBadge.tsx`)."
    )

    add_h2("3.4 Current Limitations vs. 4th-Year Future Scope Table")
    headers_lim = ["Architectural Dimension", "Current 3rd-Year Prototype (Working Scope)", "4th-Year Major Project Roadmap (Upgrade)"]
    data_lim = [
        ["Crop Coverage", "Wheat (Triticum aestivum) monoculture calibrated for Central UP.", "Multi-crop engine: Kharif Paddy (Rice) and Rabi Mustard."],
        ["User Interface", "English web dashboard optimized for desktop and mobile browsers.", "Multilingual Voice PWA in Hindi, Bhojpuri, Punjabi via Bhashini AI."],
        ["Soil Telemetry", "Periodic physical Soil Health Card digitization + regional baseline.", "LoRaWAN real-time NPK & capacitance moisture probe integration."],
        ["Satellite Validation", "Open-Meteo meteorological reanalysis at 0.1° grid.", "Sentinel-2 10m NDVI & NDWI canopy moisture satellite validation."],
        ["Offline Execution", "Client-side fallback seeds with local browser caching.", "Full offline SQLite PWA with background ServiceWorker sync."],
        ["Market Expansion", "Lucknow, Unnao, Kanpur, Rae Bareli APMC mandi network.", "Pan-India e-NAM (National Agriculture Market) real-time bidding."]
    ]
    add_table_data("Table 3.1: Current Architectural Boundaries vs. 4th-Year Future Roadmap", headers_lim, data_lim, [1.4, 2.3, 2.3])

    add_h2("3.5 Codebase Pointer Table (Person 1's Live Code Defense)")
    headers_code = ["File Path in Repository", "Key Classes / Functions / Components", "Role in KRISHI Intelligence Architecture"]
    data_code = [
        ["backend/main.py", "app = FastAPI(), include_router(), Base.metadata.create_all()", "Application root; mounts all 8 domain routers, sets up CORS middleware and DB tables."],
        ["backend/routers/farm.py", "router.post('/onboard'), router.get('/{id}')", "Handles farm entity registration, coordinate ingestion, and SQLite persistence."],
        ["backend/routers/intelligence.py", "router.post('/analyze'), analyze()", "Central decision endpoint: aggregates weather, soil, market, runs XGBoost, risk engine, and returns full decision payload."],
        ["backend/services/risk_engine.py", "compute_risk(), _calc_heat_risk(), _calc_disease_risk()", "Multi-factor risk synthesizer evaluating compound thermal, moisture, and phenological threats."],
        ["backend/services/decision_engine.py", "compute_scenarios(), _calc_net_realization()", "Evaluates Sell Today vs Wait 7d vs Wait 15d incorporating storage costs and dampness penalties."],
        ["backend/services/crop_model.py", "get_crop_stage(crop, days_after_sowing)", "Maps days after sowing and cumulative GDD to 8 physiological wheat stages."],
        ["frontend/src/app/farm/[id]/page.tsx", "FarmDashboard(), handleReanalyze()", "Executive dashboard page rendering health index, risk gauges, and primary recommendation."],
        ["frontend/src/app/farm/[id]/digital-twin/page.tsx", "DigitalTwinPage(), ProvenanceTable", "Renders synchronized twin state, GDD phenology, stress vectors, and audit timeline."],
        ["frontend/src/components/shared/DataBadge.tsx", "DataBadge({ type, small })", "Reusable provenance badge component rendering color-coded integrity indicators."],
        ["frontend/src/lib/api.ts", "api.analyzeIntelligence(), fetchWithHandleError()", "Central client API abstraction handling endpoints, fallbacks, and response normalizers."]
    ]
    add_table_data("Table 3.2: Person 1 Master Codebase Navigation & Key Architectural Files", headers_code, data_code, [1.8, 2.0, 2.2])

    # =========================================================================
    # SECTION 4: 15 TOUGH VIVA CROSS-QUESTIONS & ANSWERS
    # =========================================================================
    add_h1("4. 15 Tough Viva Cross-Questions & High-Scoring Answers")

    qa_list = [
        (
            "Q1: Why do you call this an 'Agentic' or 'Multi-Agent' platform instead of just a standard rule-based Python script or ChatGPT wrapper?",
            "\"Sir, a simple script executes a rigid, linear sequence, and a ChatGPT wrapper sends unstructured prompts to a third-party LLM that hallucinates facts. "
            "KRISHI is agentic because it deploys independent, decoupled computational services with autonomous responsibilities: "
            "an Agro-Weather Agent that continuously tracks thermal accumulation, a Market Agent that evaluates price trajectories, an OCR Extraction Agent that parses documents, "
            "and a Provenance Guardrail Agent that independently audits data freshness. "
            "Our central Orchestrator in backend/routers/intelligence.py evaluates these diverse streams asynchronously and resolves conflicting evidence mathematically rather than guessing text.\""
        ),
        (
            "Q2: How does your system resolve conflicting signals—for example, if today's Mandi price is very high, but the Weather model predicts heavy rainfall in 48 hours?",
            "\"That is exactly where our multi-factor risk engine excels. A naive price tracker would simply say 'Sell'. "
            "However, our Decision Engine (backend/services/decision_engine.py) computes Net Realization across horizons. "
            "If heavy rain is forecast in 48 hours, the Weather Risk penalty increases dramatically because unharvested standing crops face lodging, while threshed grain faces moisture damage during transit. "
            "The system evaluates: Realization = Price - Storage_Cost - Rain_Penalty. "
            "If transport is impossible or moisture risk exceeds the price gain, the orchestrator triggers an urgent advisory: harvest immediately before the rain window, or store in certified dry godowns.\""
        ),
        (
            "Q3: What exactly is a 'Digital Twin' in agriculture? Is it just a database record or a true simulation?",
            "\"In industrial engineering, a Digital Twin is an in-memory computational surrogate of a physical entity that mirrors its real-time state. "
            "In KRISHI, our DigitalTwinEngine is not a static database row; it is a dynamic state machine. "
            "Every day, it accumulates thermal energy via Growing Degree Days (GDD) with base temperature 4.0°C. "
            "It advances the crop through 8 physiological stages (Germination to Maturity), dynamically calculates crop water depletion using stage-specific coefficients ($K_c$), "
            "and tracks live thermal and moisture stress vectors. If ambient temperatures exceed 35°C during the milk stage, the twin registers thermal shock and modifies all downstream advisories.\""
        ),
        (
            "Q4: How do you mathematically guarantee that your system never fabricates or hallucinates data?",
            "\"We enforce an immutable Data Provenance State Machine in Layer 2. "
            "Every agricultural observation entering the system is tagged: LIVE (<=1 day old from official API), LATEST_AVAILABLE (2-7 days old), STALE (>7 days old), or HISTORICAL_SEED (calibrated fallback). "
            "Our Pydantic schemas enforce that data_type and provenance are required fields. "
            "If external APIs fail or are absent, the system explicitly labels data as HISTORICAL_SEED and alerts the user. Under no circumstance does our code allow a historical number to be marked as LIVE.\""
        ),
        (
            "Q5: Why did you use Next.js 14 App Router for the frontend instead of a simple React Single Page Application (SPA)?",
            "\"Next.js 14 App Router provides three critical architectural benefits: "
            "First, Server-Side Rendering (SSR) and optimized bundle compilation produce a shared JavaScript bundle of only 87 kB, ensuring instantaneous loading even on slow 3G rural mobile networks. "
            "Second, the App Router directory structure provides nested layouts (app/farm/[id]/layout.tsx), keeping navigation headers mounted while sub-pages hydrate dynamically. "
            "Third, TypeScript strict type checking ensures compile-time contract enforcement between our FastAPI Pydantic schemas and frontend interfaces.\""
        ),
        (
            "Q6: How did you compile and validate the final project report to match KCC Institute guidelines?",
            "\"As Team Lead, I oversaw the compilation of our 41-page project report strictly adhering to the KCC circular (CC 492). "
            "We built an automated document compilation pipeline (scripts/build_kcc_docx.py) using python-docx. "
            "It enforces Times New Roman 12pt, 1.5 line spacing, 1.25-inch left binding margin, figure captions strictly BELOW figures, and table captions strictly ABOVE tables. "
            "All 11 figures were generated programmatically at 300 DPI without AI clipart, and 6 authentic UI screenshots were captured directly from our running application via Playwright.\""
        ),
        (
            "Q7: What happens if the farmer has an unusual farm size (e.g., 0.5 acres vs 50 acres)? Does the decision engine scale linearly?",
            "\"Our agronomic and financial algorithms normalize all calculations by area. "
            "Crop water demand and fertilizer requirements are calculated in kg/hectare and scaled by farm_area_acres. "
            "For economic decisions, total yield is estimated using target yield quintals per hectare ($Y = \text{Yield}_{\text{target}} \times \text{Area}$). "
            "Gross revenue, godown storage carrying costs (₹5/quintal/day), and transport costs are multiplied across total quintals, ensuring exact financial projections whether a farmer has 0.5 acres or 50 acres.\""
        ),
        (
            "Q8: Why is your system restricted to Wheat in Central Uttar Pradesh? Isn't that a severe limitation?",
            "\"In academic software engineering, depth of validation is far more valuable than broad, shallow generalization. "
            "Agronomic crop models require precise physiological parameters: base temperature, thermal unit thresholds for each growth stage, stage-specific crop coefficients ($K_c$), and disease susceptibility windows. "
            "By rigorously calibrating our Digital Twin for Wheat in Lucknow and neighboring districts using 1,460 daily AGMARKNET records and ICAR soil maps, we achieved high predictive precision (MAPE 3.82%). "
            "Our architecture is completely modular—adding Rice or Mustard simply requires plugging in new phenology thresholds without changing the core engine.\""
        ),
        (
            "Q9: What is the purpose of the Farm Events & Activity Timeline at the bottom of the Digital Twin page?",
            "\"It serves as an immutable transactional audit log. In enterprise applications, tracking data provenance requires knowing not just what the current state is, but how and when it got there. "
            "Our farm_events table logs every critical action: FARM_CREATED (user registration), ANALYSIS_RECORDED (decision snapshot), and SOIL_CARD_CONFIRMED. "
            "This provides traceability if an advisory is ever audited for agronomic compliance.\""
        ),
        (
            "Q10: Explain how your nearby Mandi comparison works. Why would a farmer sell in Lucknow if Rae Bareli offers a higher price?",
            "\"That is one of our primary economic innovations. Traditional mandi apps display nominal spot prices. "
            "A farmer might see Rae Bareli offering ₹2,645/quintal compared to Lucknow's ₹2,605/quintal and think they will earn ₹40 more per quintal. "
            "However, our system incorporates a transport cost function: $C_{\text{transport}} = \text{Distance} \times \text{Rate}_{\text{per km}}$. "
            "Rae Bareli is 82 km away, costing ₹48/quintal in transport, reducing net realization to ₹2,597. "
            "Lucknow is 0 km away, yielding ₹2,605 net. Our engine flags Lucknow as [BEST], saving the farmer from an unprofitable trip.\""
        ),
        (
            "Q11: What is the role of Pydantic in your backend architecture?",
            "\"Pydantic v2 acts as our data validation and contract enforcement boundary. "
            "In backend/schemas/, we define strict schemas for farm onboarding, weather requests, soil parameters, and decision payloads. "
            "If an external API returns malformed JSON, or if a user inputs an impossible soil pH like 15.0 or negative nitrogen, Pydantic immediately rejects the request with HTTP 422 Unprocessable Entity, "
            "preventing corrupted data from entering the Digital Twin or database.\""
        ),
        (
            "Q12: If an examiner asks you to show the database right now, where is it and how do you inspect it?",
            "\"Our database is stored in krishi.db in the root project directory, managed via SQLite 3. "
            "We have 6 normalized relational tables: farms, farm_observations, farm_soil_profiles, soil_documents, price_predictions, and farm_events. "
            "I can query it immediately using sqlite3 in the terminal, or open it in DB Browser for SQLite to show our persistent records, foreign key constraints, and confirmed soil profiles.\""
        ),
        (
            "Q13: How does your frontend communicate with the backend? Are there CORS issues?",
            "\"Our FastAPI backend configures CORSMiddleware in backend/main.py, allowing cross-origin requests from our Next.js frontend running on http://localhost:3000. "
            "All client calls are encapsulated in frontend/src/lib/api.ts using fetchWithHandleError(), which handles network timeouts, normalizes API keys, and maps error codes to user-friendly alert banners.\""
        ),
        (
            "Q14: What was the hardest bug you personally solved during this project?",
            "\"One significant architectural bug was handling stale Next.js webpack cache chunks during hot reloads when switching between dev and production builds. "
            "Another critical challenge was synchronizing calendar date-drift in our automated test assertions: because live dates advance every day, hardcoded price assertions in test_expert_service.py drifted. "
            "I refactored the test suite to assert on structured semantic keys rather than static numbers, ensuring our 116 automated tests remain 100% resilient across any calendar year.\""
        ),
        (
            "Q15: Summarize KRISHI Intelligence's core contribution to Computer Science and Agriculture in 30 seconds.",
            "\"KRISHI Intelligence demonstrates that precision agricultural decision support does not require cost-prohibitive IoT sensors or hallucination-prone generative AI. "
            "By combining physics-informed phenological modeling (Growing Degree Days), verified machine learning time-series regression (XGBoost), "
            "strict multi-state data provenance guardrails, and human-in-the-loop document verification, we have built a dependable, transparent, and scalable operational platform tailored to the realities of Indian smallholder farmers.\""
        )
    ]

    for q_text, a_text in qa_list:
        add_h2(q_text)
        add_p(a_text)

    # Save document
    print(f"Saving compiled guide to: {OUTPUT_DOCX}")
    doc.save(OUTPUT_DOCX)
    print("Person 1 Viva Guide successfully generated!")


if __name__ == "__main__":
    build_guide()
