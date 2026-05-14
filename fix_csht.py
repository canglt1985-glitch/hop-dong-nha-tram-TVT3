import docx

doc = docx.Document("templates/THANH_LY_KY_LAI_CSHT.docx")
for i, p in enumerate(doc.paragraphs):
    if 10 <= i <= 25:
        print(f"P{i}: '{p.text}'")
