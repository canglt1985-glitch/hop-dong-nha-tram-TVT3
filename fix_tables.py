import docx

def remove_row(table, row):
    tbl = table._tbl
    tr = row._tr
    tbl.remove(tr)

def fix():
    files = {
        "templates/PHU_LUC_GIAM_GIA_CSHT.docx": "{{VHKT_1245}}",
        "templates/THANH_LY_KY_LAI_CSHT.docx": "{{VHKT_1245}}",
        "templates/PHU_LUC_GIAM_GIA_MAT_BANG.docx": "{{MFĐ_1245}}",
        "templates/THANH_LY_KY_LAI_MAT_BANG.docx": "{{MFĐ_1245}}"
    }
    
    for f, tag in files.items():
        doc = docx.Document(f)
        tbl = doc.tables[1]
        
        rows_to_remove = []
        for row in tbl.rows:
            # We check if the tag is in the row.
            # Wait, the original CSHT might not have {{VHKT_1245}}.
            # My patch added {{VHKT_1245}} to CSHT.
            # My patch added {{MFĐ_1245}} to MAT_BANG.
            found_tag = any(tag in cell.text for cell in row.cells)
            if found_tag:
                rows_to_remove.append(row)
                
        for row in rows_to_remove:
            remove_row(tbl, row)
            
        doc.save(f)
        print(f"Fixed {f}")

fix()
