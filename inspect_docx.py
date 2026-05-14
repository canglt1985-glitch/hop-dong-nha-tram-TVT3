import docx
doc = docx.Document("templates/PHU_LUC_GIAM_GIA_MAT_BANG.docx")
for p in doc.paragraphs:
    if "ngày" in p.text:
        print(p.text)
