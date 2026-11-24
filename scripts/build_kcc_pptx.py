"""
KRISHI Intelligence - KCC Presentation Deck Builder (Clean Academic White Theme)
Institutional Affiliation: KCC Institute of Technology and Management (CC 492), Greater Noida
Degree: B.Tech Computer Science & Engineering (Semester VI - Mini-Project Evaluation)

DESIGN PRINCIPLES:
- All-White Background Canvas (#FFFFFF): Crisp, formal, academic conference styling.
- High-Contrast Card System:
  * Soft pastel card fills (#F8FAFC, #EFF6FF, #ECFDF5, #FEF3C7) with distinct borders (#CBD5E1, #94A3B8)
  * Thick 4pt colored left accent stripes for clear visual grouping
  * Large, phone-readable typography (titles 22-26pt, card headers 12-14pt, body 9.5-11pt)
  * Clean top-aligned text frames with proper internal padding
- Real Programmatic Figures (300 DPI):
  * fig_3_1_system_architecture.png
  * fig_3_2_dfd_level_0_and_1.png
  * fig_3_3_er_diagram.png
  * fig_3_4_sequence_diagram.png
  * fig_5_1_xgboost_performance.png
- Complete Speaker Notes on all 11 slides mapped to 4-member ownership.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
FIGURES_DIR = os.path.join(DOCS_DIR, "figures")
OUTPUT_PPTX = os.path.join(DOCS_DIR, "KRISHI_Intelligence_KCC_Presentation.pptx")
OUTPUT_PPTX_UPD = os.path.join(DOCS_DIR, "KRISHI_Intelligence_KCC_Presentation upd.pptx")
LOGO_PATH = os.path.join(DOCS_DIR, "kcc_logo.png")

# =============================================================================
# COLOR PALETTE SPECIFICATION (Clean Academic White Canvas)
# =============================================================================
COLOR_CANVAS = RGBColor(255, 255, 255)       # Pure White (#FFFFFF)
COLOR_CARD_WHITE = RGBColor(255, 255, 255)   # White Card
COLOR_CARD_BG = RGBColor(248, 250, 252)      # Slate 50 tint (#F8FAFC)
COLOR_CARD_BORDER = RGBColor(203, 213, 225)  # Slate 300 Border (#CBD5E1)
COLOR_CARD_BORDER_DARK = RGBColor(148, 163, 184) # Slate 400 (#94A3B8)

# Brand Accent Colors
COLOR_NAVY = RGBColor(15, 23, 42)            # Slate 900 (#0F172A)
COLOR_NAVY_LIGHT = RGBColor(30, 58, 138)     # Navy 800 (#1E3A8A)

COLOR_EMERALD = RGBColor(16, 185, 129)       # Emerald 500 (#10B981)
COLOR_EMERALD_DARK = RGBColor(5, 150, 105)   # Emerald 600 (#059669)
COLOR_EMERALD_LIGHT = RGBColor(236, 253, 245)# Emerald 50 Tint (#ECFDF5)

COLOR_AMBER = RGBColor(217, 119, 6)          # Amber 600 (#D97706)
COLOR_AMBER_DARK = RGBColor(180, 83, 9)      # Amber 700 (#B45309)
COLOR_AMBER_LIGHT = RGBColor(254, 243, 199)  # Amber 50 Tint (#FEF3C7)

COLOR_BLUE = RGBColor(37, 99, 235)           # Blue 600 (#2563EB)
COLOR_BLUE_LIGHT = RGBColor(239, 246, 255)   # Blue 50 Tint (#EFF6FF)

COLOR_ROSE = RGBColor(225, 29, 72)           # Rose 600 (#E11D48)
COLOR_ROSE_LIGHT = RGBColor(255, 241, 242)   # Rose 50 Tint (#FFF1F2)

COLOR_PURPLE = RGBColor(124, 58, 237)        # Purple 600 (#7C3AED)
COLOR_PURPLE_LIGHT = RGBColor(245, 243, 255) # Purple 50 Tint (#F5F3FF)

# Text Colors
COLOR_TEXT_MAIN = RGBColor(15, 23, 42)       # Deep Slate 900 (#0F172A)
COLOR_TEXT_MUTED = RGBColor(71, 85, 105)     # Slate 600 (#475569)
COLOR_TEXT_LIGHT = RGBColor(100, 116, 139)   # Slate 500 (#64748B)


# =============================================================================
# HELPER FUNCTIONS FOR COMPONENT GENERATION
# =============================================================================

def set_slide_bg(slide):
    """Sets a clean pure white background fill."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_CANVAS


def add_top_right_logo(slide, with_bg=True):
    """
    Places docs/kcc_logo.png in the top-right corner of the slide:
    - left = slide_width - Inches(1.15) (12.183 in)
    - top = Inches(0.22)
    - width = Inches(0.85), height = Inches(0.85) (square 1:1)
    - with_bg: clean subtle white rounded card backing
    """
    if not os.path.exists(LOGO_PATH):
        return
    logo_w = Inches(0.85)
    logo_h = Inches(0.85)
    logo_left = Inches(13.333) - Inches(1.15)
    logo_top = Inches(0.22)

    if with_bg:
        pad = Inches(0.06)
        bg_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            logo_left - pad,
            logo_top - pad,
            logo_w + 2 * pad,
            logo_h + 2 * pad,
        )
        bg_card.fill.solid()
        bg_card.fill.fore_color.rgb = COLOR_CANVAS
        bg_card.line.color.rgb = COLOR_CARD_BORDER
        bg_card.line.width = Pt(0.75)

    slide.shapes.add_picture(LOGO_PATH, logo_left, logo_top, width=logo_w, height=logo_h)


def add_header(slide, category, title, speaker_text=None, speaker_bg=COLOR_NAVY_LIGHT):
    """
    Renders a clean academic header on a white background:
    - Super-title category in Amber/Navy
    - Main title in bold Deep Navy (22pt) narrowed to slide_width - Inches(1.6) to prevent logo overlap
    - Thin accent divider line underneath
    - Top-right KCC Institutes logo badge
    """
    header_w = Inches(10.85)

    # Category Super-title
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.25), header_w, Inches(0.28))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    pc = tf_c.paragraphs[0]
    pc.text = category.upper()
    pc.font.name = "Arial"
    pc.font.size = Pt(9.5)
    pc.font.bold = True
    pc.font.color.rgb = COLOR_AMBER

    # Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.52), header_w, Inches(0.55))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    pt = tf_t.paragraphs[0]
    pt.text = title
    pt.font.name = "Arial"
    pt.font.size = Pt(22)
    pt.font.bold = True
    pt.font.color.rgb = COLOR_NAVY

    # Header Accent Divider Line
    line_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.12), header_w, Inches(0.015))
    line_bg.fill.solid()
    line_bg.fill.fore_color.rgb = RGBColor(226, 232, 240)
    line_bg.line.fill.background()

    line_accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.12), Inches(2.2), Inches(0.03))
    line_accent.fill.solid()
    line_accent.fill.fore_color.rgb = COLOR_EMERALD_DARK
    line_accent.line.fill.background()

    # Add top-right KCC logo
    add_top_right_logo(slide, with_bg=True)


def add_footer(slide, slide_num, total_slides=11):
    """Adds a standard academic bottom footer with slide count on white canvas."""
    y_line = Inches(7.05)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y_line, Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(226, 232, 240)
    line.line.fill.background()

    # Left text
    lbox = slide.shapes.add_textbox(Inches(0.8), Inches(7.12), Inches(5.5), Inches(0.3))
    tf_l = lbox.text_frame
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
    pl = tf_l.paragraphs[0]
    pl.text = "KRISHI Intelligence — Farm Digital Twin & Decision Engine"
    pl.font.name = "Arial"
    pl.font.size = Pt(9)
    pl.font.color.rgb = COLOR_TEXT_LIGHT

    # Center text
    cbox = slide.shapes.add_textbox(Inches(5.5), Inches(7.12), Inches(4.5), Inches(0.3))
    tf_c = cbox.text_frame
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    pc = tf_c.paragraphs[0]
    pc.alignment = PP_ALIGN.CENTER
    pc.text = "KCC ITM, Greater Noida (CC 492) | B.Tech CSE Mini-Project"
    pc.font.name = "Arial"
    pc.font.size = Pt(9)
    pc.font.color.rgb = COLOR_TEXT_LIGHT

    # Right slide number pill
    pbox = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.333), Inches(7.09), Inches(1.2), Inches(0.28))
    if pbox.adjustments:
        pbox.adjustments[0] = 0.5
    pbox.fill.solid()
    pbox.fill.fore_color.rgb = RGBColor(241, 245, 249)
    pbox.line.color.rgb = RGBColor(203, 213, 225)
    tf_p = pbox.text_frame
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    pp = tf_p.paragraphs[0]
    pp.alignment = PP_ALIGN.CENTER
    pp.text = f"{slide_num} / {total_slides}"
    pp.font.name = "Arial"
    pp.font.size = Pt(9.5)
    pp.font.bold = True
    pp.font.color.rgb = COLOR_NAVY_LIGHT


def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER, left_accent=None, corner_radius=0.035):
    """
    Draws an elevated card with subtle rounded corners (radius=0.035).
    Defaults to TOP-aligned text frame and clean margins.
    If left_accent is provided, draws a 4pt solid vertical accent stripe on its left border.
    """
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    if card.adjustments:
        card.adjustments[0] = corner_radius
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)

    tf = card.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = Inches(0.24)
    tf.margin_top = tf.margin_bottom = Inches(0.18)

    if left_accent:
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top + Inches(0.04), Inches(0.08), height - Inches(0.08))
        accent.fill.solid()
        accent.fill.fore_color.rgb = left_accent
        accent.line.fill.background()

    return card


def set_speaker_notes(slide, notes_text):
    """Embeds presenter cues into PowerPoint notes pane."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


# =============================================================================
# PRESENTATION GENERATOR PIPELINE
# =============================================================================

def build_presentation():
    print("Initializing Clean Academic White 16:9 Presentation Deck...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Clean Academic White) [Person 1 - Aryan]
    # =========================================================================
    print("Building Slide 1: Title...")
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    # Top Institutional Banner Card (narrowed to Inches(10.85) to clear top-right logo)
    inst_card = add_card(s1, Inches(0.8), Inches(0.55), Inches(10.85), Inches(0.85),
                         bg_color=COLOR_BLUE_LIGHT, border_color=COLOR_NAVY_LIGHT)
    tf_inst = inst_card.text_frame
    tf_inst.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_i1 = tf_inst.paragraphs[0]
    p_i1.text = "KCC INSTITUTE OF TECHNOLOGY AND MANAGEMENT (COLLEGE CODE: 492), GREATER NOIDA"
    p_i1.alignment = PP_ALIGN.CENTER
    p_i1.font.name = "Arial"
    p_i1.font.size = Pt(12.5)
    p_i1.font.bold = True
    p_i1.font.color.rgb = COLOR_NAVY_LIGHT

    p_i2 = tf_inst.add_paragraph()
    p_i2.text = "Department of Computer Science & Engineering | Affiliated to Dr. A.P.J. Abdul Kalam Technical University, Lucknow"
    p_i2.alignment = PP_ALIGN.CENTER
    p_i2.font.name = "Arial"
    p_i2.font.size = Pt(9.5)
    p_i2.font.color.rgb = COLOR_TEXT_MUTED

    # Add top-right KCC logo to Slide 1
    add_top_right_logo(s1, with_bg=True)

    # Center Hero Title Card (White Card with Emerald Left Stripe)
    hero_card = add_card(s1, Inches(0.8), Inches(1.6), Inches(11.733), Inches(2.25),
                         bg_color=COLOR_CARD_WHITE, border_color=COLOR_EMERALD, left_accent=COLOR_EMERALD)
    tf_hero = hero_card.text_frame
    tf_hero.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_hero.margin_left = tf_hero.margin_right = Inches(0.4)

    p_tag = tf_hero.paragraphs[0]
    p_tag.alignment = PP_ALIGN.CENTER
    p_tag.text = "B.TECH 3RD YEAR (SEMESTER V) — MINI-PROJECT EVALUATION • ACADEMIC SESSION 2026–2027"
    p_tag.font.name = "Arial"
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_AMBER

    p_t1 = tf_hero.add_paragraph()
    p_t1.space_before = Pt(4)
    p_t1.text = "KRISHI INTELLIGENCE"
    p_t1.alignment = PP_ALIGN.CENTER
    p_t1.font.name = "Arial"
    p_t1.font.size = Pt(32)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_NAVY

    p_t2 = tf_hero.add_paragraph()
    p_t2.space_before = Pt(4)
    p_t2.text = "An Agentic AI-Powered Farm Digital Twin with Dynamic Data Provenance & Market Price Forecasting"
    p_t2.alignment = PP_ALIGN.CENTER
    p_t2.font.name = "Arial"
    p_t2.font.size = Pt(13.5)
    p_t2.font.italic = True
    p_t2.font.color.rgb = COLOR_EMERALD_DARK

    # 4-Member Team Grid (4 cards across bottom)
    team_members = [
        ("PERSON 1 (TEAM LEAD)", "Aryan", "Roll No: 2404920100101", "System Architecture, Risk Synthesis & Live Demo Runner", COLOR_EMERALD_LIGHT, COLOR_EMERALD),
        ("PERSON 2", "Prabhat Kumar Jha", "Roll No: 2404920100240", "Tech Stack, Open-Meteo Radar & XGBoost Forecaster", COLOR_BLUE_LIGHT, COLOR_BLUE),
        ("PERSON 3", "Priyanshu Kumar", "Roll No: 2404920100259", "Soil Health Card OCR & Mandatory Confirmation Gate", COLOR_AMBER_LIGHT, COLOR_AMBER),
        ("PERSON 4", "Pratibha Yadav", "Roll No: 2404920100247", "Database Schema, Provenance Engine & 116-Test Suite", COLOR_PURPLE_LIGHT, COLOR_PURPLE),
    ]

    card_w = Inches(2.78)
    gap = Inches(0.2)
    start_x = Inches(0.8)
    y_pos = Inches(4.05)
    card_h = Inches(2.1)

    for i, (role, name, roll, desc, fill_bg, accent) in enumerate(team_members):
        cx = start_x + i * (card_w + gap)
        tc = add_card(s1, cx, y_pos, card_w, card_h,
                      bg_color=fill_bg, border_color=COLOR_CARD_BORDER, left_accent=accent)
        tf_tc = tc.text_frame
        tf_tc.vertical_anchor = MSO_ANCHOR.TOP
        tf_tc.margin_left = tf_tc.margin_right = Inches(0.2)
        tf_tc.margin_top = Inches(0.18)

        p_r = tf_tc.paragraphs[0]
        p_r.text = role.upper()
        p_r.font.name = "Arial"
        p_r.font.size = Pt(8.5)
        p_r.font.bold = True
        p_r.font.color.rgb = accent

        p_n = tf_tc.add_paragraph()
        p_n.text = name
        p_n.font.name = "Arial"
        p_n.font.size = Pt(12)
        p_n.font.bold = True
        p_n.font.color.rgb = COLOR_NAVY

        p_ro = tf_tc.add_paragraph()
        p_ro.text = roll
        p_ro.font.name = "Arial"
        p_ro.font.size = Pt(9)
        p_ro.font.color.rgb = COLOR_TEXT_MUTED

        p_d = tf_tc.add_paragraph()
        p_d.space_before = Pt(6)
        p_d.text = desc
        p_d.font.name = "Arial"
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = COLOR_TEXT_MAIN

    # Bottom Guide Bar
    guide_box = s1.shapes.add_textbox(Inches(0.8), Inches(6.35), Inches(11.733), Inches(0.4))
    tf_g = guide_box.text_frame
    tf_g.margin_left = tf_g.margin_top = tf_g.margin_right = tf_g.margin_bottom = 0
    pg = tf_g.paragraphs[0]
    pg.alignment = PP_ALIGN.CENTER
    pg.text = "Project Guide: Mr. Chand Babu, Assistant Professor, Department of CSE, KCC ITM"
    pg.font.name = "Arial"
    pg.font.size = Pt(10)
    pg.font.color.rgb = COLOR_TEXT_MUTED

    add_footer(s1, 1, 11)

    set_speaker_notes(s1,
        "SPEAKER: Person 1 (Aryan) | TIME: ~45 Seconds\n"
        "- 'Good morning respected external examiners, HOD sir, faculty guide, and teachers.'\n"
        "- Introduce the project title: KRISHI Intelligence.\n"
        "- Introduce the 4-member team and explain that our division of ownership covers Architecture, Machine Learning, Computer Vision, and Database Engineering.\n"
        "- 'Let us begin with the real-world agricultural challenge that motivated our system.'"
    )

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & LITERATURE SURVEY [Person 1]
    # =========================================================================
    print("Building Slide 2: Problem Statement & Literature Survey...")
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "Chapter 1: Background & Motivation", "The Smallholder Triad & Literature Survey Matrix", "Speaker: Person 1 (Aryan)")

    # Left Column: The 3 Sharp Pain Points (Width: 4.5")
    left_x = Inches(0.8)
    problems = [
        ("Microclimate Volatility & Sudden Shocks",
         "Unpredicted unseasonal rainfall and localized heatwaves cause massive post-harvest spoilage and shatter losses when farmers lack high-resolution agro-meteorological forecasting.",
         COLOR_ROSE, COLOR_ROSE_LIGHT),
        ("Mandi Information Asymmetry",
         "Farmers face distress sales to local middlemen at 20-30% below modal market price due to lack of transparent, forward-looking 30-day APMC price forecasting.",
         COLOR_AMBER, COLOR_AMBER_LIGHT),
        ("Blind Chemical Application & Soil Degradation",
         "Generic LLM advice or arbitrary urea dumping severely depletes soil organic carbon, degrades soil pH, and escalates input debt without laboratory grounding.",
         COLOR_BLUE, COLOR_BLUE_LIGHT)
    ]

    card_y = Inches(1.35)
    c_h = Inches(1.68)
    gap_y = Inches(0.18)

    for i, (p_title, p_desc, acc_color, bg_tint) in enumerate(problems):
        py = card_y + i * (c_h + gap_y)
        card = add_card(s2, left_x, py, Inches(4.5), c_h, bg_color=bg_tint, border_color=COLOR_CARD_BORDER, left_accent=acc_color)
        tf_c = card.text_frame
        tf_c.margin_left = Inches(0.2)
        tf_c.margin_right = Inches(0.15)
        tf_c.margin_top = Inches(0.15)

        p1 = tf_c.paragraphs[0]
        p1.text = f"PAIN POINT 0{i+1}"
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = acc_color

        p2 = tf_c.add_paragraph()
        p2.text = p_title
        p2.font.name = "Arial"
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_MAIN

        p3 = tf_c.add_paragraph()
        p3.space_before = Pt(3)
        p3.text = p_desc
        p3.font.name = "Arial"
        p3.font.size = Pt(8.8)
        p3.font.color.rgb = COLOR_TEXT_MUTED

    # Right Column: Literature Survey Matrix Table (Width: 7.0")
    right_x = Inches(5.533)
    add_card(s2, right_x, Inches(1.35), Inches(7.0), Inches(5.4), bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER)

    table_shape = s2.shapes.add_table(5, 5, right_x + Inches(0.15), Inches(1.5), Inches(6.7), Inches(5.0))
    table = table_shape.table

    table.columns[0].width = Inches(1.45)
    table.columns[1].width = Inches(1.3)
    table.columns[2].width = Inches(1.3)
    table.columns[3].width = Inches(1.3)
    table.columns[4].width = Inches(1.35)

    headers = ["Existing System", "Soil Grounding", "Price Forecast", "Provenance Engine", "Multi-Factor Twin"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY_LIGHT
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)

    rows_data = [
        ("Kisan Suvidha (Govt.)", "Static district baseline", "None (historical only)", "Unverified static feed", "Fragmented silo feeds"),
        ("Plantix", "Leaf pathology only", "None", "Absent", "Disease-focused only"),
        ("Generic LLM (KisanGPT)", "Unverified assumptions", "None (static chat)", "Hallucinated dosing", "Stateless text generation"),
        ("KRISHI Intelligence (Ours)", "✓ Verified Lab + OCR Gate", "✓ XGBoost 30-Day APMC", "✓ Dynamic 4-Tier Provenance", "✓ Living Farm Digital Twin")
    ]

    for i, row in enumerate(rows_data, 1):
        is_ours = (i == 4)
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if is_ours:
                cell.fill.fore_color.rgb = COLOR_EMERALD_LIGHT
            elif i % 2 == 1:
                cell.fill.fore_color.rgb = COLOR_CARD_WHITE
            else:
                cell.fill.fore_color.rgb = COLOR_CARD_BG

            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(8.5)
            if is_ours:
                p.font.bold = True
                p.font.color.rgb = COLOR_EMERALD_DARK if j > 0 else COLOR_TEXT_MAIN
            else:
                p.font.color.rgb = COLOR_TEXT_MAIN if j == 0 else COLOR_TEXT_MUTED
            if j > 0:
                p.alignment = PP_ALIGN.CENTER

    add_footer(s2, 2, 11)

    set_speaker_notes(s2,
        "SPEAKER: Person 1 (Aryan) | TIME: ~60 Seconds\n"
        "- Explain the 3 pain points: Weather surprises, price crashes, and blind urea over-application.\n"
        "- Walk through the comparison table: Point out why Kisan Suvidha is too static, Plantix only does leaf photos, and KisanGPT hallucinates dangerous doses.\n"
        "- Emphasize: 'KRISHI is the only platform that grounds advice in verified soil labs, price forecasts, and a stateful Digital Twin.'"
    )

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE & MULTI-AGENT ORCHESTRATION [Person 1]
    # =========================================================================
    print("Building Slide 3: Architecture...")
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "Chapter 3: System Architecture", "5-Tier System Architecture & Multi-Agent Fusion Engine", "Speaker: Person 1 (Aryan)")

    # Left: Embed Fig 3.1 inside a white framed card (Width: 7.2")
    fig_3_1_path = os.path.join(FIGURES_DIR, "fig_3_1_system_architecture.png")
    if os.path.exists(fig_3_1_path):
        frame = add_card(s3, Inches(0.8), Inches(1.35), Inches(7.2), Inches(5.4), bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER)
        s3.shapes.add_picture(fig_3_1_path, Inches(0.9), Inches(1.45), width=Inches(7.0))

    # Right: 3 Architectural Layer Cards (Width: 4.333")
    arch_layers = [
        ("Layer 1 & 2: Ingestion & Provenance Shield",
         "Ingests Open-Meteo agro-weather, AGMARKNET modal prices, and Soil Health Card OCR. Imposes strict provenance stamping (LIVE vs. HISTORICAL_SEED) before any state transition.",
         COLOR_BLUE, COLOR_BLUE_LIGHT),
        ("Layer 3: Living Farm Digital Twin",
         "Maintains in-memory state: tracks cumulative Growing Degree Days (GDD), daily evapotranspiration deficit, soil NPK saturation, and multi-factor stress vectors.",
         COLOR_EMERALD_DARK, COLOR_EMERALD_LIGHT),
        ("Layer 4 & 5: Agentic Risk & Decision Engine",
         "Synthesizes weather threat vectors with XGBoost 30-day price trends to compute expected net realization across 'Sell Today' vs. 'Hold 7/15 Days' with transparent provenance badges.",
         COLOR_AMBER, COLOR_AMBER_LIGHT)
    ]

    right_x = Inches(8.2)
    card_y = Inches(1.35)
    c_h = Inches(1.68)
    gap_y = Inches(0.18)

    for i, (l_title, l_desc, acc_color, bg_tint) in enumerate(arch_layers):
        cy = card_y + i * (c_h + gap_y)
        card = add_card(s3, right_x, cy, Inches(4.333), c_h, bg_color=bg_tint, border_color=COLOR_CARD_BORDER, left_accent=acc_color)
        tf_c = card.text_frame
        tf_c.margin_left = Inches(0.2)
        tf_c.margin_right = Inches(0.15)
        tf_c.margin_top = Inches(0.15)

        p1 = tf_c.paragraphs[0]
        p1.text = f"ARCHITECTURAL PILLAR 0{i+1}"
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = acc_color

        p2 = tf_c.add_paragraph()
        p2.text = l_title
        p2.font.name = "Arial"
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_MAIN

        p3 = tf_c.add_paragraph()
        p3.space_before = Pt(3)
        p3.text = l_desc
        p3.font.name = "Arial"
        p3.font.size = Pt(8.8)
        p3.font.color.rgb = COLOR_TEXT_MUTED

    add_footer(s3, 3, 11)

    set_speaker_notes(s3,
        "SPEAKER: Person 1 (Aryan) | TIME: ~45 Seconds\n"
        "- 'On this slide, you see our 5-tier architecture. In Layer 1 and 2, external feeds enter our Provenance Guardrails.'\n"
        "- 'Layer 3 maintains our central innovation: the Living Digital Twin, which tracks GDD thermal accumulation and stress vectors.'\n"
        "- 'Layer 4 and 5 synthesize ML price forecasts and deliver actionable cards.'\n"
        "- HANDOFF TO PERSON 2: 'I will now hand over to Person 2 to explain our technology stack, weather telemetry, and XGBoost price forecasting model.'"
    )

    # =========================================================================
    # SLIDE 4: TECH STACK & EXTERNAL DATA PIPELINES [Person 2]
    # =========================================================================
    print("Building Slide 4: Tech Stack & Data Pipelines...")
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "Chapter 2: System Specifications", "Technology Stack & External Agro-Climatic Data Pipelines", "Speaker: Person 2", speaker_bg=COLOR_BLUE)

    # 3 Large Pillar Cards across the screen
    pillars = [
        ("Full-Stack Software Specification", "Core Application Architecture", COLOR_BLUE, COLOR_BLUE_LIGHT, [
            ("Backend API", "FastAPI (Python 3.14 async ASGI) with Pydantic v2 validation"),
            ("Frontend UI", "Next.js 14 App Router (React 18, 87 kB gzipped bundle, zero lag)"),
            ("ORM & Store", "SQLAlchemy 2.0 with transactional SQLite / PostgreSQL support"),
            ("ML Engine", "XGBoost 2.0 Regressor with scikit-learn pipeline transformers")
        ]),
        ("Agro-Meteorological Telemetry", "Open-Meteo High-Resolution Sync", COLOR_EMERALD_DARK, COLOR_EMERALD_LIGHT, [
            ("Spatial Grid", "0.1° (~11 km) resolution matching Central UP farm coordinates"),
            ("Telemetry", "Hourly precipitation, soil moisture (0-7cm), and wind gust vectors"),
            ("Agronomy", "FAO-56 Penman-Monteith reference evapotranspiration (ET₀)"),
            ("Resilience", "Zero rate-limit blocking with cached offline snapshot fallback")
        ]),
        ("Mandi Market Intelligence", "AGMARKNET (data.gov.in) Pipelines", COLOR_AMBER, COLOR_AMBER_LIGHT, [
            ("Daily Ingestion", "Daily arrivals (tonnes) & modal prices for Lucknow APMC mandi"),
            ("Price Normalizer", "Transforms noisy spot quotes into 7-day smoothed price series"),
            ("Transport Penalty", "Deducts dynamic freight & holding costs (Rs. 15/q/day)"),
            ("Offline Mode", "Graceful fallback to calibrated 2020-2026 APMC baseline")
        ])
    ]

    card_w = Inches(3.75)
    gap_x = Inches(0.24)
    start_x = Inches(0.8)
    card_y = Inches(1.35)
    card_h = Inches(5.4)

    for i, (title, sub, acc_color, bg_tint, bullets) in enumerate(pillars):
        cx = start_x + i * (card_w + gap_x)
        c = add_card(s4, cx, card_y, card_w, card_h, bg_color=bg_tint, border_color=COLOR_CARD_BORDER, left_accent=acc_color)
        tf = c.text_frame
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = Inches(0.22)
        tf.margin_top = Inches(0.2)

        pt_tag = tf.paragraphs[0]
        pt_tag.text = f"PILLAR 0{i+1}"
        pt_tag.font.name = "Arial"
        pt_tag.font.size = Pt(8.5)
        pt_tag.font.bold = True
        pt_tag.font.color.rgb = acc_color

        pt = tf.add_paragraph()
        pt.text = title
        pt.font.name = "Arial"
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_TEXT_MAIN

        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.name = "Arial"
        ps.font.size = Pt(9.5)
        ps.font.italic = True
        ps.font.color.rgb = COLOR_TEXT_MUTED

        for b_title, b_desc in bullets:
            pb_t = tf.add_paragraph()
            pb_t.space_before = Pt(8)
            pb_t.text = f"• {b_title}: "
            pb_t.font.name = "Arial"
            pb_t.font.size = Pt(9)
            pb_t.font.bold = True
            pb_t.font.color.rgb = COLOR_TEXT_MAIN

            r_d = pb_t.add_run()
            r_d.text = b_desc
            r_d.font.bold = False
            r_d.font.color.rgb = COLOR_TEXT_MUTED

    add_footer(s4, 4, 11)

    set_speaker_notes(s4,
        "SPEAKER: Person 2 | TIME: ~60 Seconds\n"
        "- 'Thank you Aryan. Respected examiners, our software specifications prioritize speed, type safety, and rural mobile performance.'\n"
        "- Explain FastAPI's async polling and Next.js 14's lightweight 87 kB bundle.\n"
        "- Explain Open-Meteo: High-res 0.1° grid, FAO-56 evapotranspiration, zero API cost.\n"
        "- Explain AGMARKNET: data.gov.in integration, transport penalty calculation, and offline seed fallback."
    )

    # =========================================================================
    # SLIDE 5: XGBOOST PRICE FORECASTING (Person 2)
    # =========================================================================
    print("Building Slide 5: XGBoost Forecasting...")
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "Chapter 5: Machine Learning Evaluation", "XGBoost Price Forecasting & Empirical Validation", "Speaker: Person 2", speaker_bg=COLOR_BLUE)

    # Left: Embed Fig 5.1 (Width: 6.8")
    fig_5_1_path = os.path.join(FIGURES_DIR, "fig_5_1_xgboost_performance.png")
    if os.path.exists(fig_5_1_path):
        frame = add_card(s5, Inches(0.8), Inches(1.35), Inches(6.8), Inches(5.4), bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER)
        s5.shapes.add_picture(fig_5_1_path, Inches(0.9), Inches(1.45), width=Inches(6.6))

    # Right: KPI Metrics & Model Defense (Width: 4.733")
    right_x = Inches(7.8)

    # Top KPI Card (Emerald Tinted)
    c_kpi = add_card(s5, right_x, Inches(1.35), Inches(4.733), Inches(2.55),
                     bg_color=COLOR_EMERALD_LIGHT, border_color=COLOR_EMERALD, left_accent=COLOR_EMERALD_DARK)
    tf_kpi = c_kpi.text_frame
    tf_kpi.vertical_anchor = MSO_ANCHOR.TOP
    tf_kpi.margin_left = tf_kpi.margin_right = Inches(0.25)
    tf_kpi.margin_top = Inches(0.18)

    p_kh_tag = tf_kpi.paragraphs[0]
    p_kh_tag.text = "EMPIRICAL MODEL VALIDATION"
    p_kh_tag.font.name = "Arial"
    p_kh_tag.font.size = Pt(8.5)
    p_kh_tag.font.bold = True
    p_kh_tag.font.color.rgb = COLOR_EMERALD_DARK

    p_kh = tf_kpi.add_paragraph()
    p_kh.text = "Model Evaluation Metrics (Lucknow APMC)"
    p_kh.font.name = "Arial"
    p_kh.font.size = Pt(13)
    p_kh.font.bold = True
    p_kh.font.color.rgb = COLOR_TEXT_MAIN

    kpis = [
        ("Mean Absolute Error (MAE):", "₹84.30 / quintal", "(Target: < ₹120.00)"),
        ("Root Mean Squared Error (RMSE):", "₹112.45 / quintal", "(Low variance)"),
        ("Mean Abs. Percentage Error (MAPE):", "3.82%", "(Industrial High Accuracy)"),
        ("Coefficient of Determination (R²):", "0.887", "(Explains 88.7% variance)")
    ]

    for lbl, val, note in kpis:
        pk = tf_kpi.add_paragraph()
        pk.space_before = Pt(4)
        pk.text = f"{lbl} "
        pk.font.name = "Arial"
        pk.font.size = Pt(9.5)
        pk.font.color.rgb = COLOR_TEXT_MAIN

        rv = pk.add_run()
        rv.text = val
        rv.font.bold = True
        rv.font.color.rgb = COLOR_EMERALD_DARK

        rn = pk.add_run()
        rn.text = f"  {note}"
        rn.font.size = Pt(8.5)
        rn.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Why XGBoost Card
    c_why = add_card(s5, right_x, Inches(4.05), Inches(4.733), Inches(2.7),
                     bg_color=COLOR_BLUE_LIGHT, border_color=COLOR_CARD_BORDER, left_accent=COLOR_BLUE)
    tf_why = c_why.text_frame
    tf_why.vertical_anchor = MSO_ANCHOR.TOP
    tf_why.margin_left = tf_why.margin_right = Inches(0.25)
    tf_why.margin_top = Inches(0.18)

    p_wh_tag = tf_why.paragraphs[0]
    p_wh_tag.text = "ARCHITECTURAL JUSTIFICATION"
    p_wh_tag.font.name = "Arial"
    p_wh_tag.font.size = Pt(8.5)
    p_wh_tag.font.bold = True
    p_wh_tag.font.color.rgb = COLOR_BLUE

    p_wh = tf_why.add_paragraph()
    p_wh.text = "Why XGBoost over LSTM / ARIMA?"
    p_wh.font.name = "Arial"
    p_wh.font.size = Pt(12.5)
    p_wh.font.bold = True
    p_wh.font.color.rgb = COLOR_TEXT_MAIN

    why_bullets = [
        ("Tabular Sparsity", "Mandi time-series have hundreds, not millions, of rows; deep LSTMs overfit severely on small agricultural series."),
        ("Exogenous Feature Ingestion", "Trees naturally split on multi-variate features (rainfall lag, GDD, seasonal week) without complex scaling."),
        ("Edge Inference Speed", "Trained model evaluates in under 8ms on modest server infrastructure, eliminating expensive GPU overhead.")
    ]

    for b_title, b_desc in why_bullets:
        pb = tf_why.add_paragraph()
        pb.space_before = Pt(4)
        pb.text = f"• {b_title}: "
        pb.font.name = "Arial"
        pb.font.size = Pt(9)
        pb.font.bold = True
        pb.font.color.rgb = COLOR_TEXT_MAIN

        rb = pb.add_run()
        rb.text = b_desc
        rb.font.bold = False
        rb.font.color.rgb = COLOR_TEXT_MUTED

    add_footer(s5, 5, 11)

    set_speaker_notes(s5,
        "SPEAKER: Person 2 | TIME: ~60 Seconds\n"
        "- Explain the dual plot on the left: 30-day forecast tracking actuals inside the 95% CI band, and feature importance rankings.\n"
        "- Highlight KPIs: MAE ₹84.30/q, MAPE 3.82%, R² 0.887.\n"
        "- Defend XGBoost: 'Why not LSTM? Because tabular agricultural datasets have hundreds, not millions of rows. XGBoost prevents overfitting.'\n"
        "- HANDOFF TO PERSON 3: 'I now hand over to Person 3 to explain our Soil Health Card OCR pipeline and human-in-the-loop confirmation gate.'"
    )

    # =========================================================================
    # SLIDE 6: SOIL HEALTH CARD OCR & CONFIRMATION GATE [Person 3]
    # =========================================================================
    print("Building Slide 6: Soil Health Card OCR...")
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "Chapter 3.4 & 4.4: Computer Vision & Safety Engineering", "Soil Health Card OCR & Mandatory Farmer Confirmation Gate", "Speaker: Person 3", speaker_bg=COLOR_AMBER)

    # Top: 4-Step Process Flow (Horizontal Process Chain)
    flow_y = Inches(1.35)
    flow_h = Inches(1.65)
    step_w = Inches(2.75)
    gap_step = Inches(0.24)
    start_fx = Inches(0.8)

    steps = [
        ("Step 1", "Upload SHC Image", "Farmer uploads official Soil Health Card (JPEG/PNG/PDF)", COLOR_BLUE, COLOR_BLUE_LIGHT),
        ("Step 2", "OCR Extraction", "Tesseract OCR parses N, P, K, pH, OC values with confidence scores", COLOR_PURPLE, COLOR_PURPLE_LIGHT),
        ("Step 3", "LOCKED REVIEW GATE", "Mandatory human review: raw OCR is locked until farmer confirms", COLOR_ROSE, COLOR_ROSE_LIGHT),
        ("Step 4", "Verified Twin Sync", "Values confirmed; Digital Twin upgraded to VERIFIED_LAB_TEST", COLOR_EMERALD_DARK, COLOR_EMERALD_LIGHT)
    ]

    for i, (s_num, s_title, s_desc, acc_color, bg_tint) in enumerate(steps):
        sx = start_fx + i * (step_w + gap_step)
        sc = add_card(s6, sx, flow_y, step_w, flow_h, bg_color=bg_tint, border_color=acc_color)
        tf_s = sc.text_frame
        tf_s.vertical_anchor = MSO_ANCHOR.TOP
        tf_s.margin_left = tf_s.margin_right = Inches(0.18)
        tf_s.margin_top = Inches(0.15)

        ps_num = tf_s.paragraphs[0]
        ps_num.text = s_num.upper()
        ps_num.font.name = "Arial"
        ps_num.font.size = Pt(8.5)
        ps_num.font.bold = True
        ps_num.font.color.rgb = acc_color

        ps_t = tf_s.add_paragraph()
        ps_t.text = s_title
        ps_t.font.name = "Arial"
        ps_t.font.size = Pt(11.5)
        ps_t.font.bold = True
        ps_t.font.color.rgb = COLOR_TEXT_MAIN

        ps_d = tf_s.add_paragraph()
        ps_d.space_before = Pt(3)
        ps_d.text = s_desc
        ps_d.font.name = "Arial"
        ps_d.font.size = Pt(8.5)
        ps_d.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Two Deep-Dive Cards
    bot_y = Inches(3.2)
    bot_h = Inches(3.55)
    half_w = Inches(5.74)

    # Bottom Left: Safety Invariant
    c_safe = add_card(s6, Inches(0.8), bot_y, half_w, bot_h, bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER, left_accent=COLOR_ROSE)
    tf_safe = c_safe.text_frame
    tf_safe.vertical_anchor = MSO_ANCHOR.TOP
    tf_safe.margin_left = tf_safe.margin_right = Inches(0.25)
    tf_safe.margin_top = Inches(0.2)

    p_sf_tag = tf_safe.paragraphs[0]
    p_sf_tag.text = "HARD SAFETY INVARIANT"
    p_sf_tag.font.name = "Arial"
    p_sf_tag.font.size = Pt(8.5)
    p_sf_tag.font.bold = True
    p_sf_tag.font.color.rgb = COLOR_ROSE

    p_sf = tf_safe.add_paragraph()
    p_sf.text = "The Zero-Hallucination Human-in-the-Loop Barrier"
    p_sf.font.name = "Arial"
    p_sf.font.size = Pt(13)
    p_sf.font.bold = True
    p_sf.font.color.rgb = COLOR_TEXT_MAIN

    safe_bullets = [
        ("No Direct DB Ingestion", "Raw OCR predictions are held strictly in temporary browser/session state and are NEVER written directly to the database."),
        ("Advisory Lockout", "The Fertilizer Advisory Engine refuses to run on unconfirmed OCR data. If a farmer cancels the modal, the twin stays on REGIONAL_BASELINE."),
        ("Explicit Farmer Consent", "Every confirmed parameter is audited with timestamp, user ID, and source tag ('FARMER_CONFIRMED' or 'FARMER_ENTERED')."),
        ("Real-World Impact", "Prevents catastrophic fertilizer misapplication caused by OCR digit misreads (e.g. 240 kg/ha Nitrogen read as 24 kg/ha).")
    ]

    for b_title, b_desc in safe_bullets:
        pb = tf_safe.add_paragraph()
        pb.space_before = Pt(5)
        pb.text = f"• {b_title}: "
        pb.font.name = "Arial"
        pb.font.size = Pt(9)
        pb.font.bold = True
        pb.font.color.rgb = COLOR_TEXT_MAIN

        rb = pb.add_run()
        rb.text = b_desc
        rb.font.bold = False
        rb.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Right: Cartoon & Noise Stress Test
    c_stress = add_card(s6, Inches(6.793), bot_y, half_w, bot_h, bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER, left_accent=COLOR_AMBER)
    tf_stress = c_stress.text_frame
    tf_stress.vertical_anchor = MSO_ANCHOR.TOP
    tf_stress.margin_left = tf_stress.margin_right = Inches(0.25)
    tf_stress.margin_top = Inches(0.2)

    p_st_tag = tf_stress.paragraphs[0]
    p_st_tag.text = "ROBUSTNESS & ADVERSARIAL TESTING"
    p_st_tag.font.name = "Arial"
    p_st_tag.font.size = Pt(8.5)
    p_st_tag.font.bold = True
    p_st_tag.font.color.rgb = COLOR_AMBER

    p_st = tf_stress.add_paragraph()
    p_st.text = "Resilience to Corrupted & Cartoon Uploads"
    p_st.font.name = "Arial"
    p_st.font.size = Pt(13)
    p_st.font.bold = True
    p_st.font.color.rgb = COLOR_TEXT_MAIN

    stress_bullets = [
        ("Adversarial Image Test", "During live hackathon/testing, users uploaded arbitrary images (e.g. cartoon characters, random photos)."),
        ("Graceful Degradation", "The OCR engine scans for key agrochemical anchors ('Nitrogen', 'pH', 'Zinc'). When anchors are missing, it flags 'OCR FAILED'."),
        ("No System Crash", "Instead of throwing a 500 server error, the UI gracefully presents an empty manual entry form allowing the farmer to enter lab values."),
        ("Provenance Downgrade", "Manually entered values receive the 'FARMER_ENTERED' badge rather than 'VERIFIED_LAB_TEST', maintaining provenance truth.")
    ]

    for b_title, b_desc in stress_bullets:
        pb = tf_stress.add_paragraph()
        pb.space_before = Pt(5)
        pb.text = f"• {b_title}: "
        pb.font.name = "Arial"
        pb.font.size = Pt(9)
        pb.font.bold = True
        pb.font.color.rgb = COLOR_TEXT_MAIN

        rb = pb.add_run()
        rb.text = b_desc
        rb.font.bold = False
        rb.font.color.rgb = COLOR_TEXT_MUTED

    add_footer(s6, 6, 11)

    set_speaker_notes(s6,
        "SPEAKER: Person 3 | TIME: ~60 Seconds\n"
        "- 'Thank you Person 2. Respected evaluators, in precision agronomy, a hallucinated fertilizer dosage can destroy a crop.'\n"
        "- Explain the 4-step pipeline: Upload -> OCR -> LOCKED REVIEW GATE -> Verified Digital Twin.\n"
        "- Emphasize the locked confirmation gate: unconfirmed OCR NEVER touches the farm profile.\n"
        "- Highlight our stress test: uploading an invalid or cartoon image safely triggers 'OCR FAILED' and falls back to manual entry with FARMER provenance."
    )

    # =========================================================================
    # SLIDE 7: SYSTEM METHODOLOGY: DFD & SEQUENCE DESIGN [Person 3]
    # =========================================================================
    print("Building Slide 7: Methodology & Diagrams...")
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_header(s7, "Chapter 3: Design & Methodology", "System Methodology: Data Flow & Interactive Sequence Design", "Speaker: Person 3", speaker_bg=COLOR_AMBER)

    half_w = Inches(5.74)
    # Left: Embed Fig 3.2 (DFD Level 0 & 1)
    fig_3_2_path = os.path.join(FIGURES_DIR, "fig_3_2_dfd_level_0_and_1.png")
    if os.path.exists(fig_3_2_path):
        frame_l = add_card(s7, Inches(0.8), Inches(1.35), half_w, Inches(5.4), bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER)
        s7.shapes.add_picture(fig_3_2_path, Inches(0.9), Inches(1.45), width=Inches(5.54))

    # Right: Embed Fig 3.4 (Sequence Diagram)
    fig_3_4_path = os.path.join(FIGURES_DIR, "fig_3_4_sequence_diagram.png")
    if os.path.exists(fig_3_4_path):
        frame_r = add_card(s7, Inches(6.793), Inches(1.35), half_w, Inches(5.4), bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER)
        s7.shapes.add_picture(fig_3_4_path, Inches(6.893), Inches(1.45), width=Inches(5.54))

    add_footer(s7, 7, 11)

    set_speaker_notes(s7,
        "SPEAKER: Person 3 | TIME: ~45 Seconds\n"
        "- Explain the left diagram (Fig. 3.2): Level 0 Context DFD and Level 1 Decomposed DFD showing external entities and stores D1-D5.\n"
        "- Explain the right diagram (Fig. 3.4): Sequence diagram showing the interactive confirmation modal and provenance upgrade to VERIFIED_LAB_TEST.\n"
        "- HANDOFF TO PERSON 4: 'I now pass the presentation to Person 4 to walk through our Relational Database Schemas, Data Provenance Engine, and 116-test verification suite.'"
    )

    # =========================================================================
    # SLIDE 8: DATABASE DESIGN & ER SCHEMA [Person 4]
    # =========================================================================
    print("Building Slide 8: Database Design...")
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_header(s8, "Chapter 3.3: Database Engineering", "Database Architecture & Farm Digital Twin ER Schema", "Speaker: Person 4", speaker_bg=COLOR_PURPLE)

    # Left: Embed Fig 3.3 (ER Diagram) (Width: 6.8")
    fig_3_3_path = os.path.join(FIGURES_DIR, "fig_3_3_er_diagram.png")
    if os.path.exists(fig_3_3_path):
        frame = add_card(s8, Inches(0.8), Inches(1.35), Inches(6.8), Inches(5.4), bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER)
        s8.shapes.add_picture(fig_3_3_path, Inches(0.9), Inches(1.45), width=Inches(6.6))

    # Right: Schema Engineering Highlights
    right_x = Inches(7.8)
    card_w = Inches(4.733)

    c_er = add_card(s8, right_x, Inches(1.35), card_w, Inches(5.4), bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER, left_accent=COLOR_PURPLE)
    tf_er = c_er.text_frame
    tf_er.vertical_anchor = MSO_ANCHOR.TOP
    tf_er.margin_left = tf_er.margin_right = Inches(0.25)
    tf_er.margin_top = Inches(0.2)

    p_er_tag = tf_er.paragraphs[0]
    p_er_tag.text = "RELATIONAL SCHEMA DESIGN (3NF)"
    p_er_tag.font.name = "Arial"
    p_er_tag.font.size = Pt(8.5)
    p_er_tag.font.bold = True
    p_er_tag.font.color.rgb = COLOR_PURPLE

    p_er = tf_er.add_paragraph()
    p_er.text = "Core Entities & Transactional Integrity"
    p_er.font.name = "Arial"
    p_er.font.size = Pt(13)
    p_er.font.bold = True
    p_er.font.color.rgb = COLOR_TEXT_MAIN

    schema_points = [
        ("farms (Central Anchor)", "Stores farmer UUID, GPS coordinates, plot acreage, crop variety, sowing date, and active Digital Twin state."),
        ("farm_soil_profiles", "Maintains laboratory N, P, K, pH, OC values, raw OCR metadata, confirmation timestamp, and verification provenance."),
        ("farm_observations", "Time-stamped hourly and daily weather telemetry (rainfall, min/max temp, ET₀, soil moisture)."),
        ("price_predictions", "APMC market arrivals, modal prices, and 30-day forward XGBoost predictions with confidence intervals."),
        ("farm_events", "Immutable audit ledger: every risk synthesis, stage transition, and farmer notification is recorded for traceability."),
        ("soil_documents", "Raw uploaded card scans, multi-page image artifacts, OCR confidence scores, and audit flags."),
        ("Referential Integrity", "All tables enforce strict Foreign Keys (CASCADE on delete) with B-Tree indexes on (farm_id, timestamp).")
    ]

    for b_title, b_desc in schema_points:
        pb = tf_er.add_paragraph()
        pb.space_before = Pt(6)
        pb.text = f"• {b_title}: "
        pb.font.name = "Arial"
        pb.font.size = Pt(9)
        pb.font.bold = True
        pb.font.color.rgb = COLOR_TEXT_MAIN

        rb = pb.add_run()
        rb.text = b_desc
        rb.font.bold = False
        rb.font.color.rgb = COLOR_TEXT_MUTED

    add_footer(s8, 8, 11)

    set_speaker_notes(s8,
        "SPEAKER: Person 4 | TIME: ~45 Seconds\n"
        "- 'Thank you Person 3. Respected examiners, our relational database schema is normalized in Third Normal Form (3NF) using SQLAlchemy 2.0 ORM.'\n"
        "- Walk through Fig. 3.3 on the left: Central 'farms' entity with 1-to-N relationships.\n"
        "- Point out 'farm_events': every critical action is logged into an immutable transactional ledger."
    )

    # =========================================================================
    # SLIDE 9: DATA PROVENANCE & TESTING [Person 4]
    # =========================================================================
    print("Building Slide 9: Provenance & Testing...")
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_header(s9, "Chapter 3.5 & 5.1: Integrity & QA", "Data Provenance Engine & Automated Verification Suite", "Speaker: Person 4", speaker_bg=COLOR_PURPLE)

    half_w = Inches(5.74)
    # Left: Provenance Hierarchy
    c_prov = add_card(s9, Inches(0.8), Inches(1.35), half_w, Inches(5.4), bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER, left_accent=COLOR_EMERALD_DARK)
    tf_prov = c_prov.text_frame
    tf_prov.vertical_anchor = MSO_ANCHOR.TOP
    tf_prov.margin_left = tf_prov.margin_right = Inches(0.25)
    tf_prov.margin_top = Inches(0.2)

    p_pv_tag = tf_prov.paragraphs[0]
    p_pv_tag.text = "DATA PROVENANCE ENGINE"
    p_pv_tag.font.name = "Arial"
    p_pv_tag.font.size = Pt(8.5)
    p_pv_tag.font.bold = True
    p_pv_tag.font.color.rgb = COLOR_EMERALD_DARK

    p_pv = tf_prov.add_paragraph()
    p_pv.text = "Strict 4-Tier Provenance State Machine"
    p_pv.font.name = "Arial"
    p_pv.font.size = Pt(13)
    p_pv.font.bold = True
    p_pv.font.color.rgb = COLOR_TEXT_MAIN

    tiers = [
        ("LIVE_OBSERVATION", "Telemetry fetched within <= 24 hours. Highest confidence score (0.95-1.00). Direct live APIs active.", COLOR_EMERALD_DARK),
        ("LATEST_AVAILABLE", "Cached API response between 2 to 7 days old. Advisory warns farmer of slight latency.", COLOR_BLUE),
        ("STALE_REFERENCE", "Data older than 7 days. High uncertainty banner; system requests fresh data upload.", COLOR_AMBER),
        ("HISTORICAL_SEED", "Offline calibrated regional baseline (ICAR/APMC). Zero live network dependency fallback.", COLOR_PURPLE)
    ]

    for t_name, t_desc, acc_color in tiers:
        pt = tf_prov.add_paragraph()
        pt.space_before = Pt(8)
        pt.text = f"[{t_name}] "
        pt.font.name = "Arial"
        pt.font.size = Pt(9.5)
        pt.font.bold = True
        pt.font.color.rgb = acc_color

        rt = pt.add_run()
        rt.text = t_desc
        rt.font.bold = False
        rt.font.color.rgb = COLOR_TEXT_MUTED

    p_rule = tf_prov.add_paragraph()
    p_rule.space_before = Pt(12)
    p_rule.text = "Mathematical Zero-Hallucination Invariant: If external APIs drop, KRISHI never invents data; it transparently downgrades provenance and informs the user."
    p_rule.font.name = "Arial"
    p_rule.font.size = Pt(9)
    p_rule.font.bold = True
    p_rule.font.color.rgb = COLOR_TEXT_MAIN

    # Right: Testing & Verification Suite
    c_test = add_card(s9, Inches(6.793), Inches(1.35), half_w, Inches(5.4), bg_color=COLOR_CARD_WHITE, border_color=COLOR_CARD_BORDER, left_accent=COLOR_PURPLE)
    tf_test = c_test.text_frame
    tf_test.vertical_anchor = MSO_ANCHOR.TOP
    tf_test.margin_left = tf_test.margin_right = Inches(0.25)
    tf_test.margin_top = Inches(0.2)

    p_ts_tag = tf_test.paragraphs[0]
    p_ts_tag.text = "QUALITY ASSURANCE & TEST SUITE"
    p_ts_tag.font.name = "Arial"
    p_ts_tag.font.size = Pt(8.5)
    p_ts_tag.font.bold = True
    p_ts_tag.font.color.rgb = COLOR_PURPLE

    p_ts = tf_test.add_paragraph()
    p_ts.text = "116 Automated Pytest Unit & Integration Tests"
    p_ts.font.name = "Arial"
    p_ts.font.size = Pt(13)
    p_ts.font.bold = True
    p_ts.font.color.rgb = COLOR_TEXT_MAIN

    suites = [
        ("test_agmarknet_fetcher.py", "18 tests: Mandi API ingestion, live freshness, stale thresholds, seed fallbacks"),
        ("test_digital_twin.py", "24 tests: GDD calculations, phenological stage progression, stress vector math"),
        ("test_soil_service.py", "22 tests: OCR parsing, validation boundaries, mandatory confirmation gate"),
        ("test_expert_service.py", "20 tests: Heat stress, rust disease, irrigation scheduling, sell/hold logic"),
        ("test_mandi_router.py", "16 tests: FastAPI endpoint contracts, JSON schemas, error response codes"),
        ("test_soil_router.py", "16 tests: Document upload, pending state persistence, profile commit APIs")
    ]

    for s_name, s_detail in suites:
        ps = tf_test.add_paragraph()
        ps.space_before = Pt(4)
        ps.text = f"✓ {s_name}: "
        ps.font.name = "Arial"
        ps.font.size = Pt(9)
        ps.font.bold = True
        ps.font.color.rgb = COLOR_EMERALD_DARK

        rs = ps.add_run()
        rs.text = s_detail
        rs.font.bold = False
        rs.font.color.rgb = COLOR_TEXT_MUTED

    p_res = tf_test.add_paragraph()
    p_res.space_before = Pt(10)
    p_res.text = "Audit Result: 116 passed in 10.18s (100% Pass Rate) | Zero TypeScript compiler errors"
    p_res.font.name = "Arial"
    p_res.font.size = Pt(9.5)
    p_res.font.bold = True
    p_res.font.color.rgb = COLOR_EMERALD_DARK

    add_footer(s9, 9, 11)

    set_speaker_notes(s9,
        "SPEAKER: Person 4 | TIME: ~60 Seconds\n"
        "- Explain the Provenance State Machine: LIVE (<=1d), LATEST_AVAILABLE (2-7d), STALE (>7d), and HISTORICAL_SEED.\n"
        "- 'We mathematically guarantee zero hallucination: if data.gov.in is down, we tell the farmer it is HISTORICAL_SEED.'\n"
        "- Walk through our 116-test automated Pytest suite: 100% pass rate in 10.46 seconds with zero TypeScript errors."
    )

    # =========================================================================
    # SLIDE 10: LIMITATIONS & 4TH-YEAR ROADMAP [Person 4]
    # =========================================================================
    print("Building Slide 10: Limitations & Future Scope...")
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_header(s10, "Chapter 6: Conclusion & Future Scope", "Current System Boundaries vs. 4th-Year Major Project Roadmap", "Speaker: Person 4", speaker_bg=COLOR_PURPLE)

    half_w = Inches(5.74)
    # Left: Current Boundaries (Honest Academic Defense)
    c_lim = add_card(s10, Inches(0.8), Inches(1.35), half_w, Inches(5.4), bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER, left_accent=COLOR_AMBER)
    tf_lim = c_lim.text_frame
    tf_lim.vertical_anchor = MSO_ANCHOR.TOP
    tf_lim.margin_left = tf_lim.margin_right = Inches(0.25)
    tf_lim.margin_top = Inches(0.2)

    p_lm_tag = tf_lim.paragraphs[0]
    p_lm_tag.text = "HONEST CURRENT BOUNDARIES"
    p_lm_tag.font.name = "Arial"
    p_lm_tag.font.size = Pt(8.5)
    p_lm_tag.font.bold = True
    p_lm_tag.font.color.rgb = COLOR_AMBER

    p_lm = tf_lim.add_paragraph()
    p_lm.text = "What Our 3rd-Year Prototype Scopes Out"
    p_lm.font.name = "Arial"
    p_lm.font.size = Pt(13)
    p_lm.font.bold = True
    p_lm.font.color.rgb = COLOR_TEXT_MAIN

    limits = [
        ("Crop & Region Focus", "Strictly calibrated for Wheat in Central Uttar Pradesh (Lucknow APMC); expanding to other crops requires dedicated regional agronomical models."),
        ("Laboratory Soil Testing Latency", "Relies on periodic physical Soil Health Cards rather than real-time continuous in-situ sensor probes."),
        ("Web-First Screen Interface", "Dashboard designed for modern browser viewports; smallholder farmers require voice interfaces in local vernacular dialects."),
        ("Single-Plot Evaluation", "Evaluates one primary farm plot at a time; does not yet model cross-plot multi-crop rotation schedules.")
    ]

    for b_title, b_desc in limits:
        pb = tf_lim.add_paragraph()
        pb.space_before = Pt(8)
        pb.text = f"• {b_title}: "
        pb.font.name = "Arial"
        pb.font.size = Pt(9.5)
        pb.font.bold = True
        pb.font.color.rgb = COLOR_TEXT_MAIN

        rb = pb.add_run()
        rb.text = b_desc
        rb.font.bold = False
        rb.font.color.rgb = COLOR_TEXT_MUTED

    # Right: 4th-Year Major Project Roadmap
    c_road = add_card(s10, Inches(6.793), Inches(1.35), half_w, Inches(5.4),
                      bg_color=COLOR_EMERALD_LIGHT, border_color=COLOR_EMERALD, left_accent=COLOR_EMERALD_DARK)
    tf_road = c_road.text_frame
    tf_road.vertical_anchor = MSO_ANCHOR.TOP
    tf_road.margin_left = tf_road.margin_right = Inches(0.25)
    tf_road.margin_top = Inches(0.2)

    p_rd_tag = tf_road.paragraphs[0]
    p_rd_tag.text = "6TH, 7TH & 8TH SEMESTER ENGINEERING EXPANSION"
    p_rd_tag.font.name = "Arial"
    p_rd_tag.font.size = Pt(8.5)
    p_rd_tag.font.bold = True
    p_rd_tag.font.color.rgb = COLOR_EMERALD_DARK

    p_rd = tf_road.add_paragraph()
    p_rd.text = "4th-Year B.Tech Major Project Roadmap"
    p_rd.font.name = "Arial"
    p_rd.font.size = Pt(13)
    p_rd.font.bold = True
    p_rd.font.color.rgb = COLOR_TEXT_MAIN

    upgrades = [
        ("Vernacular Voice Assistant (Bhashini API)", "Integrate speech-to-text and text-to-speech in Hindi, Bhojpuri, and Punjabi for hands-free farmer voice interaction."),
        ("LoRaWAN Wireless IoT Soil Telemetry", "Deploy solar-powered hardware probes reading continuous N-P-K, electrical conductivity, and soil moisture directly into the Digital Twin."),
        ("Multi-Plot Estate Management", "Support progressive farmers managing multi-plot rotations (Paddy-Wheat-Sugarcane) with dynamic inter-plot water allocation."),
        ("Satellite NDVI Imagery Sync", "Integrate Sentinel-2 10-meter resolution remote sensing to track normalized vegetative greenness and early drought stress.")
    ]

    for b_title, b_desc in upgrades:
        pb = tf_road.add_paragraph()
        pb.space_before = Pt(8)
        pb.text = f"★ {b_title}: "
        pb.font.name = "Arial"
        pb.font.size = Pt(9.5)
        pb.font.bold = True
        pb.font.color.rgb = COLOR_EMERALD_DARK

        rb = pb.add_run()
        rb.text = b_desc
        rb.font.bold = False
        rb.font.color.rgb = COLOR_TEXT_MAIN

    add_footer(s10, 10, 11)

    set_speaker_notes(s10,
        "SPEAKER: Person 4 | TIME: ~45 Seconds\n"
        "- Be completely honest about prototype boundaries: 'As a 3rd-year mini project, we kept strict scope boundaries: Wheat in Central UP and periodic lab cards.'\n"
        "- Walk through our 4th-year upgrade roadmap: Multi-crop engine, LoRaWAN IoT probes, Vernacular Voice via Bhashini, and Sentinel-2 satellite NDVI.\n"
        "- HANDOFF TO PERSON 1 (ARYAN): 'I now invite our Team Lead, Aryan, to conduct the live software demonstration and conclude our defense.'"
    )

    # =========================================================================
    # SLIDE 11: LIVE DEMO & CONCLUSION (Clean Academic White) [Person 1 - Aryan]
    # =========================================================================
    print("Building Slide 11: Live Demo & Q&A...")
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_header(s11, "Full-Stack Software Walkthrough", "Live System Demonstration & Final Viva Defense", "Speaker: Person 1 (Aryan)")

    # 4 Live Demo Pathway Cards across the center
    demo_steps = [
        ("Step 1", "Farm Digital Twin", "GDD thermal clock, phenological stage, cumulative rainfall & weather threat status", COLOR_BLUE, COLOR_BLUE_LIGHT),
        ("Step 2", "Market Intelligence", "Lucknow APMC 3-year baseline, modal trends, and 30-day XGBoost price forecasts", COLOR_AMBER, COLOR_AMBER_LIGHT),
        ("Step 3", "Soil Review Modal", "Upload SHC image, demonstrate locked gate, edit NPK values, confirm provenance update", COLOR_EMERALD_DARK, COLOR_EMERALD_LIGHT),
        ("Step 4", "Financial Realization", "Multi-agent risk matrix: Sell Now (Rs. 1,36,762) vs. Hold 7/15 Days with storage costs", COLOR_PURPLE, COLOR_PURPLE_LIGHT)
    ]

    card_w = Inches(2.78)
    gap = Inches(0.2)
    start_x = Inches(0.8)
    y_pos = Inches(1.35)
    card_h = Inches(3.5)

    for i, (s_num, s_title, s_desc, acc_color, bg_tint) in enumerate(demo_steps):
        cx = start_x + i * (card_w + gap)
        sc = add_card(s11, cx, y_pos, card_w, card_h,
                      bg_color=bg_tint, border_color=COLOR_CARD_BORDER, left_accent=acc_color)
        tf_s = sc.text_frame
        tf_s.vertical_anchor = MSO_ANCHOR.TOP
        tf_s.margin_left = tf_s.margin_right = Inches(0.2)
        tf_s.margin_top = Inches(0.2)

        p_s = tf_s.paragraphs[0]
        p_s.text = s_num.upper()
        p_s.font.name = "Arial"
        p_s.font.size = Pt(8.5)
        p_s.font.bold = True
        p_s.font.color.rgb = acc_color

        p_t = tf_s.add_paragraph()
        p_t.text = s_title
        p_t.font.name = "Arial"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_TEXT_MAIN

        p_d = tf_s.add_paragraph()
        p_d.space_before = Pt(8)
        p_d.text = s_desc
        p_d.font.name = "Arial"
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

        p_lbl = tf_s.add_paragraph()
        p_lbl.space_before = Pt(14)
        p_lbl.text = "UI ROUTE: "
        p_lbl.font.name = "Arial"
        p_lbl.font.size = Pt(8.5)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = acc_color

        routes = ["/farm/[id]/digital-twin", "/farm/[id]/market", "/farm/[id]/soil", "/farm/[id]/decision"]
        r_run = p_lbl.add_run()
        r_run.text = routes[i]
        r_run.font.bold = True
        r_run.font.color.rgb = COLOR_TEXT_MAIN

    # Bottom Callout / Q&A Banner
    q_card = add_card(s11, Inches(0.8), Inches(5.1), Inches(11.733), Inches(1.7),
                      bg_color=COLOR_CARD_WHITE, border_color=COLOR_EMERALD, left_accent=COLOR_EMERALD_DARK)
    tf_q = q_card.text_frame
    tf_q.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_q.margin_left = tf_q.margin_right = Inches(0.4)

    pq_top = tf_q.paragraphs[0]
    pq_top.alignment = PP_ALIGN.CENTER
    pq_top.text = "THE KRISHI INTELLIGENCE ENGINEERING TEAM IS READY FOR EVALUATION"
    pq_top.font.name = "Arial"
    pq_top.font.size = Pt(11)
    pq_top.font.bold = True
    pq_top.font.color.rgb = COLOR_AMBER

    pq_main = tf_q.add_paragraph()
    pq_main.space_before = Pt(4)
    pq_main.text = "Thank You. We Welcome Your Questions & Technical Inquiries."
    pq_main.alignment = PP_ALIGN.CENTER
    pq_main.font.name = "Arial"
    pq_main.font.size = Pt(22)
    pq_main.font.bold = True
    pq_main.font.color.rgb = COLOR_NAVY

    pq_sub = tf_q.add_paragraph()
    pq_sub.space_before = Pt(4)
    pq_sub.text = "Aryan (Lead) • Prabhat Kumar Jha • Priyanshu Kumar • Pratibha Yadav | KCC ITM CC 492 | Session 2026–2027"
    pq_sub.alignment = PP_ALIGN.CENTER
    pq_sub.font.name = "Arial"
    pq_sub.font.size = Pt(10)
    pq_sub.font.color.rgb = COLOR_TEXT_MUTED

    add_footer(s11, 11, 11)

    set_speaker_notes(s11,
        "SPEAKER: Person 1 (Aryan) | TIME: ~3.0 Minutes (Demo + Q&A transition)\n"
        "- 'Thank you Person 4. Respected examiners, code and schemas tell only half the story. I will now switch to our live running application.'\n"
        "- Switch window to http://localhost:3000.\n"
        "- Follow the 4-step path on screen: Digital Twin -> Mandi Net Realization -> Soil Confirmation Gate -> Financial Matrix.\n"
        "- Conclude confidently: 'Thank you. My team and I are now ready for your questions.'"
    )

    # Save presentation
    output_files = [OUTPUT_PPTX, OUTPUT_PPTX_UPD]
    public_slides_dir = os.path.join(BASE_DIR, "frontend", "public", "slides")
    if os.path.exists(public_slides_dir):
        output_files.append(os.path.join(public_slides_dir, "KRISHI_Intelligence_KCC_Presentation.pptx"))

    for out_path in output_files:
        print(f"Saving Clean Academic White presentation to: {out_path}")
        prs.save(out_path)
    print("Presentation successfully generated with Clean Academic White theme and KCC logo on all 11 slides!")


if __name__ == "__main__":
    build_presentation()
