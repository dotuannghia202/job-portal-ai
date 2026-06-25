import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in .env file")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_job_description(
    title: str,
    skills: str,
    levels: str
    
) -> str:
    try:
        prompt = f"""
        Bạn là một Chuyên gia Tuyển dụng. Hãy viết nội dung tin tuyển dụng thật chuyên nghiệp và thu hút.
        Thông tin đầu vào:
        - Vị trí: {title}
        - Cấp bậc: {levels}
        - Kỹ năng yêu cầu: {skills}
        BẮT BUỘC TRẢ VỀ CHÍNH XÁC ĐỊNH DẠNG JSON SAU (Không thêm markdown, không thêm text thừa):
        {{
            "description": "Viết 1 đoạn văn 3-4 câu giới thiệu về công việc và sự thú vị của nó...",
            "requirements": [
                "Yêu cầu 1...",
                "Yêu cầu 2..."
            ],
            "benefits": [
                "Quyền lợi 1...",
                "Quyền lợi 2..."
            ]
        }}
        """

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )

        if not response.text:
            raise Exception("Gemini returned empty response")

        return response.text.strip()

    except Exception as e:
        raise Exception(f"Error when calling Google Gemini API: {str(e)}")


def calculate_match_score_by_gemini(job_text: str, cv_text: str) -> float:
    try:
        # 1. Kiểm tra dữ liệu rỗng (Tiết kiệm tiền gọi API)
        if not job_text or not cv_text:
            return 0.0

        # 2. Xây dựng Prompt (Lời nhắc)
        prompt = f"""
        Bạn là một Giám đốc nhân sự (HR) khắt khe. Hãy chấm điểm mức độ phù hợp của CV ứng viên với Yêu cầu công việc (JD) dưới thang điểm 100.

        Quy tắc chấm điểm (QUAN TRỌNG):
        1. Đánh giá kỹ năng: Nếu CV có chứa ĐỦ các kỹ năng cốt lõi mà JD yêu cầu -> Điểm cao.
        2. Dư thừa không trừ điểm: Việc CV có thêm nhiều kỹ năng khác hoặc dài dòng KHÔNG được làm giảm điểm số.
        3. Đa ngôn ngữ: Chấp nhận JD Tiếng Việt và CV Tiếng Anh (hoặc ngược lại). Hãy hiểu ngữ nghĩa của chúng.
        4. BẮT BUỘC CHỈ TRẢ VỀ DUY NHẤT 1 CON SỐ (từ 0 đến 100). Không giải thích, không thêm dấu chấm câu, không viết thêm bất kỳ chữ nào khác.

        --- MÔ TẢ CÔNG VIỆC (JD) ---
        {job_text}

        --- NỘI DUNG CV ---
        {cv_text}
        """

        # 3. Gọi Google Gemini
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        raw_text = response.text.strip()

        # 4. Dùng Regex để an toàn lấy ra con số (Đề phòng AI trả lời: "Điểm: 85")
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", raw_text)

        if numbers:
            score = float(numbers[0])
            # Ép điểm nằm trong khoảng an toàn 0 -> 100
            return max(0.0, min(100.0, score))
        else:
            print(f">>> [Cảnh báo] Gemini không trả về số: {raw_text}")
            return 0.0

    except Exception as e:
        print(f">>> [Lỗi] Khi chấm điểm bằng Gemini: {str(e)}")
        return 0.0