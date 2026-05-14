import docx

doc = docx.Document("templates/THANH_LY_KY_LAI_CSHT.docx")
for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    if "Căn" in text or "cứ" in text or "_________________" in text:
        print(f"P{i}: {text}")
