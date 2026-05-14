import docx
import os

def patch_file(filepath):
    doc = docx.Document(filepath)
    changed = False
    for p in doc.paragraphs:
        if "thanh lý ký lại" in p.text.lower():
            # Perform case-insensitive replacement
            import re
            p.text = re.sub(r'(?i)thanh lý ký lại', 'đàm phán giảm giá', p.text)
            changed = True
    
    if changed:
        doc.save(filepath)
        print(f"Patched {filepath}")
    else:
        print(f"No changes needed for {filepath}")

patch_file("templates/PHU_LUC_GIAM_GIA_MAT_BANG.docx")
patch_file("templates/PHU_LUC_GIAM_GIA_CSHT.docx")
