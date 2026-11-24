import pptx

prs = pptx.Presentation(r'docs\KRISHI_Intelligence_KCC_Presentation.pptx')
print(f"Total slides: {len(prs.slides)}")
for idx, slide in enumerate(prs.slides):
    small_runs = 0
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                for run in p.runs:
                    if run.font.size and run.font.size.pt < 9:
                        small_runs += 1
                        # print first 2
                        if small_runs <= 2:
                            print(f"Slide {idx+1} small text ({run.font.size.pt}pt): {p.text[:40]}")
    if small_runs > 0:
        print(f"  Total small text runs on slide {idx+1}: {small_runs}")
