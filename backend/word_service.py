from docxtpl import DocxTemplate
import os

class WordService:
    def __init__(self, template_dir="templates", output_dir="output"):
        self.template_dir = template_dir
        self.output_dir = output_dir
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_document(self, template_name, data, output_filename=None):
        """
        template_name: Tên file mẫu (vd: DNCM02.docx)
        data: Dictionary chứa các tags (vd: {"SITE_ID": "DNLK01", ...})
        """
        template_path = os.path.join(self.template_dir, template_name)
        if not os.path.exists(template_path):
            return False, f"Không tìm thấy file mẫu tại {template_path}"

        try:
            doc = DocxTemplate(template_path)
            doc.render(data)
            
            if not output_filename:
                output_filename = f"PLHD_{data.get('SITE_ID', 'TEMP')}_{template_name}"
            
            output_path = os.path.join(self.output_dir, output_filename)
            doc.save(output_path)
            
            return True, output_path
        except Exception as e:
            return False, str(e)
