import docx
import os

files = [
    "PHU_LUC_GIAM_GIA_CSHT.docx",
    "PHU_LUC_GIAM_GIA_MAT_BANG.docx",
    "THANH_LY_KY_LAI_CSHT.docx",
    "THANH_LY_KY_LAI_MAT_BANG.docx"
]

for f in files:
    try:
        doc = docx.Document(f"templates/{f}")
        print(f"=== {f} ===")
        for i, t in enumerate(doc.tables):
            try:
                text = t.rows[0].cells[0].text[:50].replace("\n", " ")
                print(f"Table {i}: {text}")
            except:
                pass
        print()
    except Exception as e:
        print(f"Error {f}: {e}")
