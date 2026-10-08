from schemas.interview_question import InterviewQuestionItem
import json
import os

from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

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

        # Enable JSON response mode
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )

        if not response.text:
            return {"match_score": 0.0, "matched_skills": [], "missing_skills": []}

        # Parse JSON string returned by AI into a dictionary
        parsed_json = json.loads(response.text.strip())
        
        # Ensure match_score is constrained within [0.0, 100.0]
        parsed_json["match_score"] = max(0.0, min(100.0, float(parsed_json.get("match_score", 0.0))))
        
        return parsed_json

    except Exception as e:
        print(f">>> [Error] Scoring with Gemini: {str(e)}")
        return {"match_score": 0.0, "matched_skills": [], "missing_skills": []}


# Generate interview questions
def generate_interview_questions(job_text: str, cv_text: str) -> list:
    try:
        # Search proprietary questions trong Vector DB
        search_query = f"{job_text[:500]} {cv_text[:500]}"
        custom_bank = search_custom_questions(search_query, n_results=2)

        custom_context = ""
        if custom_bank:
            custom_context = (
                "--- PROPRIETARY SAMPLE QUESTIONS (PRIORITIZE ADAPTING BASED"
                " ON THESE) ---\n"
            )
            for item in custom_bank:
                custom_context += (
                    f"+ Sample question: {item['question']}\n  Evaluation"
                    f" rubric: {item['rubric']}\n"
                )

        # Prompt chỉ định rõ vai trò của từng loại category để AI phân loại chính xác
        prompt = f"""
        You are an Engineering Manager. Based on the Job Description (JD), Candidate CV, and Sample Questions, generate exactly 5 interview questions.

        {custom_context}

        --- QUESTION CATEGORIES & DISTRIBUTION GUIDELINES:
        Distribute the 5 questions across these exact categories:
        1. PROJECT_DEEP_DIVE (1-2 questions): Deep dive into specific projects/architecture mentioned in CV (ask about trade-offs, their actual role, challenges).
        2. TECHNICAL_CORE (1-2 questions): Core technical knowledge required strictly by the JD.
        3. PROBLEM_SOLVING (1 question): System design, troubleshooting a bug, or resolving a performance bottleneck.
        4. SITUATIONAL (1 question): Real-world workplace scenarios, tight deadlines, handling conflicts, or teamwork.

        --- RULES:
        - If "PROPRIETARY SAMPLE QUESTIONS" are provided, adapt and contextualize them into the candidate's CV experience.
        - Questions must be concrete, practical, and directly address the candidate's stack. Avoid generic textbook trivia.

        --- JD:
        {job_text}

        --- CV:
        {cv_text}
        """

        # Gọi Gemini với ràng buộc Schema
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[InterviewQuestionItem],
                temperature=0.3,
            ),
        )

        return json.loads(response.text.strip())

    except Exception as e:
        raise Exception(f"Error generating interview questions: {str(e)}")