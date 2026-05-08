from docxtpl import DocxTemplate
doc = DocxTemplate("../templates/MASTER_TEMPLATE_VFINAL.docx")

# Check what variables docxtpl finds
vars = doc.get_undeclared_template_variables()
print("Variables recognized by docxtpl:")
for v in sorted(vars):
    print(f"  {v}")
