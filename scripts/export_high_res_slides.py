import os
import fitz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(BASE_DIR, "docs", "KRISHI_Intelligence_KCC_Presentation.pdf")
OUT_DIR = os.path.join(BASE_DIR, "docs", "slides_preview")
PUBLIC_DIR = os.path.join(BASE_DIR, "frontend", "public", "slides")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

print(f"Opening PDF: {PDF_PATH}")
doc = fitz.open(PDF_PATH)
print(f"Total pages: {len(doc)}")

for i, page in enumerate(doc):
    slide_num = i + 1
    # 200 DPI gives ~2667x1500 (Retina / Quad HD resolution)
    pix = page.get_pixmap(dpi=200)
    
    out_filename = f"Slide{slide_num}.PNG"
    out_path = os.path.join(OUT_DIR, out_filename)
    public_path = os.path.join(PUBLIC_DIR, out_filename)
    
    pix.save(out_path)
    pix.save(public_path)
    print(f"Saved {out_filename} ({pix.width}x{pix.height}) -> {os.path.getsize(out_path) // 1024} KB")

# Also copy PDF and PPTX to public folder
import shutil
shutil.copy2(PDF_PATH, os.path.join(PUBLIC_DIR, "KRISHI_Intelligence_KCC_Presentation.pdf"))
pptx_src = os.path.join(BASE_DIR, "docs", "KRISHI_Intelligence_KCC_Presentation.pptx")
shutil.copy2(pptx_src, os.path.join(PUBLIC_DIR, "KRISHI_Intelligence_KCC_Presentation.pptx"))
print("Copied PDF and PPTX to frontend public folder.")
