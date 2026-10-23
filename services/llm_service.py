import json
import os
import tempfile
import time
import requests
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

from schemas.interview_question import (
    InterviewQuestionItem,
    SessionEvaluationRequest,
    SessionEvaluationResponse,
)
from services.vector_service import search_custom_questions

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in .env file")

client = genai.Client(api_key=GEMINI_API_KEY)


# Generate Job Description
def generate_job_description(
    title: str,
    skills: str,
    levels: str
) -> str:
    try:
        prompt = f"""
        You are a professional Recruitment Specialist / HR Expert. Write a compelling and professional job description.
        Input information:
        - Job Title: {title}
        - Level: {levels}
        - Required Skills: {skills}

        YOU MUST RETURN EXACTLY THE FOLLOWING JSON FORMAT (No markdown formatting, no code blocks, no extra text):
        {{
            "description": "Write a 3-4 sentence engaging introduction about the job role and its impact...",
            "requirements": [
                "Requirement 1...",
                "Requirement 2..."
            ],
            "benefits": [
                "Benefit 1...",
                "Benefit 2..."
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


# Calculate match score between JD and CV
def calculate_match_score_by_gemini(job_text: str, cv_text: str) -> dict:
    try:
        if not job_text or not cv_text:
            return {"match_score": 0.0, "matched_skills": [], "missing_skills": []}

        prompt = f"""
        You are a strict HR Director and a data analysis expert.
        Your task is to compare a candidate's CV with a Job Description (JD).

        Analysis Rules:
        1. match_score: Score the overall match from 0 to 100.
        2. matched_skills: Extract a list of core skills that ARE REQUIRED IN THE JD AND FOUND IN THE CV.
        3. missing_skills: Extract a list of core skills that ARE REQUIRED IN THE JD BUT MISSING FROM THE CV.
        4. Multilingual support: Support both Vietnamese and English. Capitalize skill names properly (e.g., Java, Spring Boot, ReactJS).

        YOU MUST RETURN EXACTLY THE FOLLOWING JSON FORMAT (No markdown, no extra text):
        {{
            "match_score": 85.5,
            "matched_skills": ["Java", "Spring Boot", "PostgreSQL"],
            "missing_skills": ["AWS", "Kubernetes"]
        }}

        --- JOB DESCRIPTION (JD) ---
        {job_text}

        --- CV CONTENT ---
        {cv_text}
        """

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )

        if not response.text:
            return {"match_score": 0.0, "matched_skills": [], "missing_skills": []}

        parsed_json = json.loads(response.text.strip())
        parsed_json["match_score"] = max(0.0, min(100.0, float(parsed_json.get("match_score", 0.0))))
        return parsed_json

    except Exception as e:
        print(f">>> [Error] Scoring with Gemini: {str(e)}")
        return {"match_score": 0.0, "matched_skills": [], "missing_skills": []}


# Generate interview questions (Bilingual VI + EN)
def generate_interview_questions(job_text: str, cv_text: str) -> list:
    try:
        search_query = f"{job_text[:500]} {cv_text[:500]}"
        custom_bank = search_custom_questions(search_query, n_results=2)

        custom_context = ""
        if custom_bank:
            custom_context = (
                "--- PROPRIETARY SAMPLE QUESTIONS (PRIORITIZE ADAPTING BASED ON THESE) ---\n"
            )
            for item in custom_bank:
                custom_context += (
                    f"+ Sample question: {item['question']}\n  Evaluation rubric: {item['rubric']}\n"
                )

        prompt = f"""
        You are an Engineering Manager. Based on the JD, CV, and Sample Questions, generate exactly 5 interview questions.
        For EACH question, generate both 'question_text_vi' (Vietnamese) and 'question_text_en' (English with accurate IT terminology).

        {custom_context}

        --- QUESTION CATEGORIES & DISTRIBUTION GUIDELINES:
        1. PROJECT_DEEP_DIVE (1-2 questions): Deep dive into specific projects/architecture mentioned in CV.
        2. TECHNICAL_CORE (1-2 questions): Core technical knowledge required strictly by the JD.
        3. PROBLEM_SOLVING (1 question): System design, troubleshooting a bug, or resolving a performance bottleneck.
        4. SITUATIONAL (1 question): Real-world workplace scenarios, handling deadlines, or teamwork.

        --- RULES:
        - If 'PROPRIETARY SAMPLE QUESTIONS' are provided, adapt and contextualize them into the candidate's CV experience.
        - Questions must be concrete, practical, and directly address the candidate's tech stack.

        --- JD:
        {job_text}

        --- CV:
        {cv_text}
        """

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[InterviewQuestionItem],
                temperature=0.2,
            ),
        )

        return json.loads(response.text.strip())

    except Exception as e:
        raise Exception(f"Error generating interview questions: {str(e)}")


# Evaluate interview session (Gemini Multimodal + Rubric + Zero-Hallucination)
def evaluate_interview_session(req: SessionEvaluationRequest) -> dict:
    """
    Workflow:
    1. Tải video từ Cloudinary xuống file tạm trên máy chủ.
    2. Upload lên Gemini File API (hỗ trợ an toàn file lớn).
    3. Chờ trạng thái File chuyển sang ACTIVE.
    4. Yêu cầu Gemini:
       - Bóc băng tiếng Việt nguyên văn (transcribed_text_vi) và dịch sang tiếng Anh (transcribed_text_en).
       - Chấm điểm chuẩn xác theo Rubric (accuracy_score).
       - BẮT BUỘC trích dẫn câu nói thực tế của ứng viên vào 'evidence_quote' để chống ảo giác.
       - Tính final_score dựa trên accuracy_score và speed_factor.
       - Cung cấp nhận xét song ngữ (feedback_vi, feedback_en, ai_overall_feedback_vi, ai_overall_feedback_en).
    5. Xóa file tạm và xóa file trên Gemini để giải phóng bộ nhớ.
    """
    temp_file_path = None
    uploaded_gemini_file = None

    try:
        # BƯỚC 1: Tải video từ Cloudinary về file tạm
        print(f">>> [AI Evaluation] Đang tải video từ Cloudinary: {req.video_url}")
        res = requests.get(req.video_url, stream=True, timeout=120)
        res.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file_path = temp_file.name
            for chunk in res.iter_content(chunk_size=8192):
                temp_file.write(chunk)

        # BƯỚC 2: Upload lên Gemini Files API
        print(">>> [AI Evaluation] Đang upload video lên Gemini File API...")
        uploaded_gemini_file = client.files.upload(
            file=temp_file_path,
            config=types.UploadFileConfig(
                display_name=f"interview_session_{req.session_id}",
                mime_type="video/webm"
            )
        )

        # BƯỚC 3: Chờ video xử lý xong trên server Google
        print(f">>> [AI Evaluation] File state hiện tại: {uploaded_gemini_file.state.name}")
        while uploaded_gemini_file.state.name == "PROCESSING":
            time.sleep(3)
            uploaded_gemini_file = client.files.get(name=uploaded_gemini_file.name)

        if uploaded_gemini_file.state.name == "FAILED":
            raise Exception("Gemini không thể giải mã định dạng video này.")

        # BƯỚC 4: Chuẩn bị payload danh sách câu hỏi và tiêu chí
        questions_payload = [
            {
                "question_id": q.question_id,
                "question_text": q.question_text,
                "rubric": q.rubric,
                "duration_seconds": q.duration_seconds,
                "time_limit_seconds": q.time_limit_seconds,
                "start_time_seconds": q.start_time_seconds
            }
            for q in req.questions
        ]

        # BƯỚC 5: Prompt triệt tiêu ảo giác (Zero-Hallucination Framework)
        prompt = f"""
        Bạn là Hội đồng Giám khảo kỹ thuật phần mềm cấp cao.
        Nhiệm vụ:
        1. Lắng nghe video phỏng vấn và bóc băng lời thoại ứng viên cho từng câu hỏi (chuyển thành tiếng Việt nguyên văn và dịch sang tiếng Anh).
        2. Chấm điểm từng câu hỏi dựa TUYỆT ĐỐI vào Rubric đề ra.

        DANH SÁCH CÂU HỎI VÀ TIÊU CHÍ (RUBRIC):
        {json.dumps(questions_payload, ensure_ascii=False, indent=2)}

        --- NGUYÊN TẮC CHỐNG ẢO GIÁC (ZERO-HALLUCINATION RULES):
        1. CHỈ chấm điểm dựa trên những gì ứng viên THỰC SỰ ĐÃ NÓI trong video. TUYỆT ĐỐI KHÔNG tự suy đoán kiến thức ngầm của ứng viên.
        2. BẮT BUỘC phải trích dẫn câu nói thực tế của ứng viên vào trường 'evidence_quote' để làm bằng chứng cho số điểm đã chấm. Nếu ứng viên không nói ý đó trong video, tiêu chí đó tính là 0 điểm.
        3. Công thức tính final_score cho mỗi câu:
           - speed_factor = min(1.0, max(0.0, 1.0 - (duration_seconds / time_limit_seconds) * 0.3)) nếu trả lời đúng.
           - Nếu accuracy_score < 50: speed_factor = 0.0.
           - final_score = accuracy_score * (0.7 + 0.3 * speed_factor).
        4. Cung cấp nhận xét song ngữ đầy đủ cả 'feedback_vi' và 'feedback_en'.
        """

        print(">>> [AI Evaluation] Đang tiến hành phân tích & chấm điểm bằng Gemini...")
        eval_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                uploaded_gemini_file,
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SessionEvaluationResponse,
                temperature=0.0 # BẮT BUỘC = 0.0 để loại bỏ hoàn toàn tính ngẫu nhiên
            )
        )

        return json.loads(eval_response.text.strip())

    except Exception as e:
        raise Exception(f"Error evaluating interview video: {str(e)}")

    finally:
        # BƯỚC 6: Dọn dẹp file tạm ở cả server local và Gemini
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

        if uploaded_gemini_file:
            try:
                client.files.delete(name=uploaded_gemini_file.name)
                print(">>> [AI Evaluation] Đã xóa file trên Gemini File API thành công.")
            except Exception:
                pass