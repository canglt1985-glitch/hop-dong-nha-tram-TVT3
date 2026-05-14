from backend.cloud_document_generator import generate_document_from_cloud

site_data = {
    "site_id": "TEST001",
    "owner": "Nguyen Van A",
    "end_date": "01/10/2026",
    "prices_breakdown": {
        "mb": 5000000,
        "pm": 0,
        "mfd": 0,
        "cot": 0,
        "giam_tru": 0,
        "vhkt": 0
    },
    "new_price": 5000000
}
generate_document_from_cloud(site_data, "templates/PHU_LUC_GIAM_GIA_CSHT.docx", "output", "PL", "phu_luc_giam_gia")
print("Done CSHT")

generate_document_from_cloud(site_data, "templates/THANH_LY_KY_LAI_MAT_BANG.docx", "output", "TL", "thanh_ly")
print("Done MAT BANG")
