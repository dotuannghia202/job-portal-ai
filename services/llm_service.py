import os

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