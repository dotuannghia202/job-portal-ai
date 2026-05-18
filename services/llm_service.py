import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in .env file")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_job_description(
    title: str,
    skills: str,
    location: str,
    experience: str
) -> str:
    try:
        prompt = f"""
Bạn là một Chuyên viên Nhân sự cấp cao.
Hãy viết một bản mô tả công việc chuyên nghiệp.

Thông tin đầu vào:
- Vị trí: {title}
- Kỹ năng yêu cầu: {skills}
- Địa điểm làm việc: {location}
- Yêu cầu kinh nghiệm: {experience}

Yêu cầu:
- Viết bằng tiếng Việt
- Giọng văn chuyên nghiệp
- Chỉ dùng gạch đầu dòng "-"
- Không dùng markdown phức tạp
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        if not response.text:
            raise Exception("Gemini returned empty response")

        return response.text.strip()

    except Exception as e:
        raise Exception(f"Error when calling Google Gemini API: {str(e)}")