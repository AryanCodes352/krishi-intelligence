"""
Generate Authentic Sample Soil Health Cards for KRISHI Intelligence testing.
Creates high-contrast, official Government of India Soil Health Cards (PNG format).
"""
import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size: int, bold: bool = False):
    font_names = ["calibrib.ttf" if bold else "calibri.ttf",
                  "arialbd.ttf" if bold else "arial.ttf",
                  "segoeuib.ttf" if bold else "segoeui.ttf"]
    for fn in font_names:
        p = os.path.join(r"C:\Windows\Fonts", fn)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_soil_health_card(data: dict, output_path: str):
    width = 1200
    height = 1600
    
    # 1. Canvas
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer double border (Govt document styling)
    draw.rectangle([(16, 16), (width - 16, height - 16)], outline=(27, 67, 50), width=4)
    draw.rectangle([(22, 22), (width - 22, height - 22)], outline=(45, 106, 79), width=1)
    
    # 2. Header Banner
    banner_h = 135
    draw.rectangle([(23, 23), (width - 23, banner_h + 23)], fill=(27, 67, 50))
    
    font_h1 = get_font(23, bold=True)
    font_h2 = get_font(27, bold=True)
    font_h3 = get_font(16, bold=False)
    
    title_1 = "GOVERNMENT OF INDIA • DEPARTMENT OF AGRICULTURE & FARMERS WELFARE"
    title_2 = "SOIL HEALTH CARD (LABORATORY TEST REPORT)"
    title_3 = f"NATIONAL MISSION FOR SUSTAINABLE AGRICULTURE • {data['lab_name'].upper()}"
    
    draw.text((width // 2, 45), title_1, fill=(216, 243, 220), font=font_h1, anchor="mm")
    draw.text((width // 2, 85), title_2, fill=(255, 255, 255), font=font_h2, anchor="mm")
    draw.text((width // 2, 125), title_3, fill=(183, 228, 199), font=font_h3, anchor="mm")
    
    # Gold divider line
    draw.line([(24, banner_h + 23), (width - 24, banner_h + 23)], fill=(233, 196, 106), width=3)
    
    # 3. Farmer & Sample Metadata Box
    meta_top = 175
    meta_h = 195
    draw.rounded_rectangle([(45, meta_top), (width - 45, meta_top + meta_h)], radius=8, fill=(247, 252, 248), outline=(183, 228, 199), width=2)
    
    font_label = get_font(18, bold=True)
    font_val = get_font(18, bold=False)
    font_val_bold = get_font(19, bold=True)
    
    col1_x = 65
    col2_x = 630
    line_spacing = 35
    
    # Column 1
    y = meta_top + 18
    draw.text((col1_x, y), "Soil Health Card No:", fill=(27, 67, 50), font=font_label)
    draw.text((col1_x + 205, y), data["card_no"], fill=(0, 0, 0), font=font_val_bold)
    
    y += line_spacing
    draw.text((col1_x, y), "Farmer Name:", fill=(27, 67, 50), font=font_label)
    draw.text((col1_x + 205, y), data["farmer_name"], fill=(0, 0, 0), font=font_val_bold)
    
    y += line_spacing
    draw.text((col1_x, y), "Village / District / State:", fill=(27, 67, 50), font=font_label)
    draw.text((col1_x + 205, y), data["location"], fill=(40, 40, 40), font=font_val)
    
    y += line_spacing
    draw.text((col1_x, y), "Khasra / Survey No:", fill=(27, 67, 50), font=font_label)
    draw.text((col1_x + 205, y), f"{data['khasra_no']} (Area: {data['area']}, {data['texture']})", fill=(40, 40, 40), font=font_val)
    
    y += line_spacing
    draw.text((col1_x, y), "Soil Texture Class:", fill=(27, 67, 50), font=font_label)
    draw.text((col1_x + 205, y), data["texture"], fill=(0, 0, 0), font=font_val_bold)
    
    # Column 2
    y = meta_top + 18
    draw.text((col2_x, y), "Sample Collection Date:", fill=(27, 67, 50), font=font_label)
    draw.text((col2_x + 225, y), data["sample_date"], fill=(0, 0, 0), font=font_val_bold)
    
    y += line_spacing
    draw.text((col2_x, y), "Date of Testing:", fill=(27, 67, 50), font=font_label)
    draw.text((col2_x + 225, y), data["test_date"], fill=(40, 40, 40), font=font_val)
    
    y += line_spacing
    draw.text((col2_x, y), "Sample ID / Barcode:", fill=(27, 67, 50), font=font_label)
    draw.text((col2_x + 225, y), data["sample_id"], fill=(40, 40, 40), font=font_val)
    
    y += line_spacing
    draw.text((col2_x, y), "GPS Coordinates:", fill=(27, 67, 50), font=font_label)
    draw.text((col2_x + 225, y), data["gps"], fill=(40, 40, 40), font=font_val)
    
    y += line_spacing
    draw.text((col2_x, y), "Verification Status:", fill=(27, 67, 50), font=font_label)
    draw.text((col2_x + 225, y), "VERIFIED & VALIDATED", fill=(45, 106, 79), font=font_val_bold)
    
    # 4. Table Section Header
    table_top = meta_top + meta_h + 20
    draw.rectangle([(45, table_top), (width - 45, table_top + 36)], fill=(45, 106, 79))
    draw.text((width // 2, table_top + 18), "SOIL TEST RESULTS (MACRO & MICRO NUTRIENTS ANALYZED)", fill=(255, 255, 255), font=get_font(18, bold=True), anchor="mm")
    
    # 5. Table Header
    header_top = table_top + 36
    header_h = 42
    draw.rectangle([(45, header_top), (width - 45, header_top + header_h)], fill=(27, 67, 50))
    
    col_w = [80, 420, 180, 160, 270]
    col_x = [45]
    for w in col_w:
        col_x.append(col_x[-1] + w)
        
    font_th = get_font(17, bold=True)
    th_labels = ["S. No", "Parameter", "Test Value", "Unit", "Rating"]
    for i, lbl in enumerate(th_labels):
        cx = col_x[i] + col_w[i] // 2
        draw.text((cx, header_top + header_h // 2), lbl, fill=(255, 255, 255), font=font_th, anchor="mm")
    
    # 6. Table Rows
    font_row = get_font(18, bold=False)
    font_row_bold = get_font(18, bold=True)
    font_row_val = get_font(19, bold=True)
    
    curr_y = header_top + header_h
    row_h = 48
    
    for idx, row in enumerate(data["parameters"]):
        bg_color = (255, 255, 255) if idx % 2 == 0 else (244, 249, 245)
        draw.rectangle([(45, curr_y), (width - 45, curr_y + row_h)], fill=bg_color)
        draw.line([(45, curr_y + row_h), (width - 45, curr_y + row_h)], fill=(216, 224, 219), width=1)
        
        # S.No
        draw.text((col_x[0] + col_w[0] // 2, curr_y + row_h // 2), str(idx + 1), fill=(80, 80, 80), font=font_row, anchor="mm")
        
        # Parameter Name
        draw.text((col_x[1] + 25, curr_y + row_h // 2), row["name"], fill=(20, 20, 20), font=font_row_bold, anchor="lm")
        
        # Test Value
        draw.text((col_x[2] + col_w[2] // 2, curr_y + row_h // 2), str(row["value"]), fill=(0, 0, 0), font=font_row_val, anchor="mm")
        
        # Unit
        draw.text((col_x[3] + col_w[3] // 2, curr_y + row_h // 2), row["unit"], fill=(60, 60, 60), font=font_row, anchor="mm")
        
        # Rating badge
        rating = row["rating"]
        r_color = (45, 106, 79)
        if "Low" in rating or "Deficient" in rating:
            r_color = (180, 40, 40)
        elif "High" in rating or "Excess" in rating:
            r_color = (180, 100, 20)
        draw.text((col_x[4] + col_w[4] // 2, curr_y + row_h // 2), rating, fill=r_color, font=font_row_bold, anchor="mm")
        
        curr_y += row_h
        
    # Vertical grid lines
    for x in col_x:
        draw.line([(x, header_top), (x, curr_y)], fill=(200, 215, 205), width=1)
    draw.rectangle([(45, header_top), (width - 45, curr_y)], outline=(27, 67, 50), width=2)
    
    # 7. Laboratory & Authorization Footer
    footer_top = curr_y + 25
    footer_h = 160
    draw.rounded_rectangle([(45, footer_top), (width - 45, footer_top + footer_h)], radius=8, fill=(247, 252, 248), outline=(183, 228, 199), width=2)
    
    f_y = footer_top + 20
    draw.text((65, f_y), "Soil Testing Laboratory:", fill=(27, 67, 50), font=font_label)
    draw.text((290, f_y), data["lab_name"], fill=(0, 0, 0), font=font_val_bold)
    
    f_y += 35
    draw.text((65, f_y), "Laboratory Accreditation:", fill=(27, 67, 50), font=font_label)
    draw.text((290, f_y), "NABL Accredited & Certified Agricultural Soil Chemistry Division", fill=(40, 40, 40), font=font_val)
    
    f_y += 35
    draw.text((65, f_y), "Authorized Signatory:", fill=(27, 67, 50), font=font_label)
    draw.text((290, f_y), f"{data['signatory']} | Digitally Verified Lab Record", fill=(0, 0, 0), font=font_val_bold)
    
    f_y += 35
    draw.text((65, f_y), "QR / Digital Seal:", fill=(27, 67, 50), font=font_label)
    draw.text((290, f_y), f"SECURE-HASH-VAL-{data['card_no'].replace('-', '')}-GOV-APPROVED", fill=(80, 80, 80), font=font_val)
    
    # Bottom disclaimer
    draw.text((width // 2, height - 35), "This is an official computer-generated Soil Health Card issued by Department of Agriculture & Cooperation.", fill=(120, 120, 120), font=get_font(13), anchor="mm")
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Generated {output_path} successfully ({os.path.getsize(output_path)} bytes)")

# Card 2 Data: Suresh Patel, Kanpur Nagar (Clay Loam, High OC, High K, Medium N & P)
card_2_data = {
    "card_no": "SHC-UP-KNP-2026-09241",
    "farmer_name": "Suresh Patel",
    "location": "Bilhaur, Kanpur Nagar, Uttar Pradesh",
    "khasra_no": "88/14",
    "area": "4.5 Acres",
    "texture": "Clay Loam",
    "sample_date": "18-Nov-2026",
    "test_date": "20-Nov-2026",
    "sample_id": "SPL-KNP-2026-7819",
    "gps": "26.8467° N, 80.0528° E",
    "lab_name": "District Soil Testing Laboratory, Kanpur Nagar (Dept. of Agriculture, UP)",
    "signatory": "Dr. R. K. Verma, Senior Soil Chemist",
    "parameters": [
        {"name": "pH (Soil Reaction)", "value": "6.8", "unit": "-", "rating": "Normal (Optimal)"},
        {"name": "Electrical Conductivity (EC)", "value": "0.48", "unit": "dS/m", "rating": "Normal"},
        {"name": "Organic Carbon (OC)", "value": "0.85", "unit": "%", "rating": "High"},
        {"name": "Available Nitrogen (N)", "value": "315.0", "unit": "kg/ha", "rating": "Medium (Optimal)"},
        {"name": "Available Phosphorus (P)", "value": "34.2", "unit": "kg/ha", "rating": "Medium"},
        {"name": "Available Potassium (K)", "value": "240.0", "unit": "kg/ha", "rating": "High"},
        {"name": "Available Sulphur (S)", "value": "18.5", "unit": "ppm", "rating": "Sufficient"},
        {"name": "Available Zinc (Zn)", "value": "1.25", "unit": "ppm", "rating": "Sufficient"},
        {"name": "Available Iron (Fe)", "value": "6.80", "unit": "ppm", "rating": "Sufficient"},
        {"name": "Available Copper (Cu)", "value": "0.72", "unit": "ppm", "rating": "Sufficient"},
        {"name": "Available Manganese (Mn)", "value": "3.60", "unit": "ppm", "rating": "Sufficient"},
        {"name": "Available Boron (B)", "value": "0.72", "unit": "ppm", "rating": "Sufficient"},
    ]
}

# Card 3 Data: Gurpreet Singh, Ludhiana, Punjab (Silt Loam, Low OC, Low N & P)
card_3_data = {
    "card_no": "SHC-PB-LDH-2026-04192",
    "farmer_name": "Gurpreet Singh",
    "location": "Samrala, Ludhiana, Punjab",
    "khasra_no": "214/19",
    "area": "6.2 Acres",
    "texture": "Silt Loam",
    "sample_date": "16-Nov-2026",
    "test_date": "19-Nov-2026",
    "sample_id": "SPL-LDH-2026-3021",
    "gps": "30.9010° N, 75.8573° E",
    "lab_name": "Regional Soil Testing Laboratory, Ludhiana (Dept. of Agriculture, Punjab)",
    "signatory": "Dr. H. S. Dhillon, Chief Soil Analyst",
    "parameters": [
        {"name": "pH (Soil Reaction)", "value": "7.8", "unit": "-", "rating": "Slightly Alkaline"},
        {"name": "Electrical Conductivity (EC)", "value": "0.58", "unit": "dS/m", "rating": "Normal"},
        {"name": "Organic Carbon (OC)", "value": "0.42", "unit": "%", "rating": "Low"},
        {"name": "Available Nitrogen (N)", "value": "180.0", "unit": "kg/ha", "rating": "Low"},
        {"name": "Available Phosphorus (P)", "value": "16.5", "unit": "kg/ha", "rating": "Low"},
        {"name": "Available Potassium (K)", "value": "145.0", "unit": "kg/ha", "rating": "Low"},
        {"name": "Available Sulphur (S)", "value": "9.2", "unit": "ppm", "rating": "Deficient"},
        {"name": "Available Zinc (Zn)", "value": "0.48", "unit": "ppm", "rating": "Deficient"},
        {"name": "Available Iron (Fe)", "value": "4.10", "unit": "ppm", "rating": "Low"},
        {"name": "Available Copper (Cu)", "value": "0.38", "unit": "ppm", "rating": "Sufficient"},
        {"name": "Available Manganese (Mn)", "value": "2.40", "unit": "ppm", "rating": "Sufficient"},
        {"name": "Available Boron (B)", "value": "0.42", "unit": "ppm", "rating": "Deficient"},
    ]
}

if __name__ == "__main__":
    # Generate in data/ and docs/ and Desktop
    targets = [
        (card_2_data, r"data\sample_soil_health_card_2.png"),
        (card_2_data, r"docs\sample_soil_health_card_2.png"),
        (card_2_data, r"c:\Users\aryan\Desktop\sample_soil_health_card_2.png"),
        (card_3_data, r"data\sample_soil_health_card_3.png"),
        (card_3_data, r"docs\sample_soil_health_card_3.png"),
        (card_3_data, r"c:\Users\aryan\Desktop\sample_soil_health_card_3.png"),
    ]
    for data, path in targets:
        try:
            draw_soil_health_card(data, path)
        except Exception as e:
            print(f"Failed to generate {path}: {e}")
