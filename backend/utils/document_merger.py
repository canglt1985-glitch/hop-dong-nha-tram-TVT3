import os
import copy
import docx

def merge_docx_files(base_path, append_paths, output_path):
    """
    Sáp nhập nội dung của các tệp append_paths vào cuối tệp base_path, phân cách bằng ngắt trang.
    Lưu kết quả ra tệp output_path.
    """
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Không tìm thấy tệp gốc: {base_path}")
        
    doc_base = docx.Document(base_path)
    
    for path in append_paths:
        if not path or not os.path.exists(path):
            continue
            
        # Thêm ngắt trang trước khi nối tài liệu tiếp theo
        doc_base.add_page_break()
        doc_src = docx.Document(path)
        
        # Sao chép các phần tử XML chính từ body nguồn sang body đích
        for element in doc_src.element.body:
            if element.tag.endswith('sectPr'):
                # Bỏ qua sectPr (Section properties) để tránh làm hỏng thiết lập lề/page layout của file base
                continue
            elem_copy = copy.deepcopy(element)
            doc_base.element.body.append(elem_copy)
            
    doc_base.save(output_path)
