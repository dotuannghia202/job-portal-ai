import pdfplumber
import requests
import io

def extract_text_from_pdf_url(pdf_url: str) -> str:
    try:
        # 1. Tải file PDF từ Link Cloudinary về
        response = requests.get(pdf_url)
        response.raise_for_status() # Báo lỗi nếu link hỏng (404, 403)

        # 2. Đưa file vào bộ nhớ RAM thay vì lưu xuống ổ cứng
        pdf_bytes = io.BytesIO(response.content)

        full_text = ""

        # 3. Mở và đọc PDF bằng pdfplumber
        with pdfplumber.open(pdf_bytes) as pdf:
            # Lặp qua từng trang của CV
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        # 4. Trả về chuỗi văn bản đã được làm sạch khoảng trắng
        return full_text.strip()

    except Exception as e:
        raise Exception(f"Error when extracting PDF: {str(e)}")