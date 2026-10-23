import json
from enum import Enum
from pydantic import BaseModel, Field


# ⚠️ NOTE: The values here MUST MATCH 100% with QuestionCategory in Java
class QuestionCategoryEnum(str, Enum):
    PROJECT_DEEP_DIVE = "PROJECT_DEEP_DIVE"  # Xoáy sâu dự án trong CV
    TECHNICAL_CORE = "TECHNICAL_CORE"        # Kiến thức kỹ thuật cốt lõi theo JD
    SITUATIONAL = "SITUATIONAL"              # Tình huống thực tế / Kỹ năng mềm
    PROBLEM_SOLVING = "PROBLEM_SOLVING"      # Tư duy giải quyết vấn đề


# Schema câu hỏi sinh ra từ AI (Song ngữ từ đầu)
class InterviewQuestionItem(BaseModel):
    order_index: int = Field(..., ge=1, le=5, description="Thứ tự câu hỏi từ 1 đến 5")
    category: QuestionCategoryEnum = Field(..., description="Nhóm câu hỏi")
    time_limit_seconds: int = Field(..., ge=30, le=300, description="Thời gian tối đa trả lời")
    rubric: str = Field(..., description="Tiêu chí chấm điểm chi tiết (Tiếng Việt)")
    question_text_vi: str = Field(..., description="Nội dung câu hỏi bằng Tiếng Việt")
    question_text_en: str = Field(..., description="Question content in English with accurate tech terms")


# Input câu hỏi gửi sang để chấm điểm
class QuestionAnswerInput(BaseModel):
    question_id: str | int
    question_text: str
    rubric: str
    duration_seconds: int = 60
    time_limit_seconds: int = 90
    start_time_seconds: int = 0


# Request đánh giá toàn bộ buổi phỏng vấn
class SessionEvaluationRequest(BaseModel):
    session_id: str | int
    video_url: str
    questions: list[QuestionAnswerInput]


# Chi tiết đánh giá từng câu hỏi từ AI
class QuestionEvaluationResult(BaseModel):
    question_id: str | int
    transcribed_text_vi: str = Field(..., description="Lời thoại nguyên văn Tiếng Việt của ứng viên")
    transcribed_text_en: str = Field(..., description="Bản dịch tiếng Anh của lời thoại ứng viên")
    accuracy_score: float = Field(..., ge=0.0, le=100.0, description="Điểm nội dung theo rubric (0-100)")
    speed_factor: float = Field(..., ge=0.0, le=1.0, description="Hệ số tốc độ trả lời (0.0 - 1.0)")
    final_score: float = Field(..., ge=0.0, le=100.0, description="Điểm tổng kết câu")
    evidence_quote: str = Field(..., description="Trích dẫn NGUYÊN VĂN câu nói của ứng viên làm bằng chứng")
    feedback_vi: str = Field(..., description="Nhận xét chi tiết bằng Tiếng Việt")
    feedback_en: str = Field(..., description="Detailed feedback in English")


# Kết quả tổng kết phiên phỏng vấn
class SessionEvaluationResponse(BaseModel):
    session_id: str | int
    total_score: float = Field(..., ge=0.0, le=100.0, description="Điểm trung bình toàn buổi phỏng vấn")
    ai_overall_feedback_vi: str = Field(..., description="Nhận xét tổng quát toàn bộ buổi thi bằng Tiếng Việt")
    ai_overall_feedback_en: str = Field(..., description="Overall interview feedback in English")
    evaluations: list[QuestionEvaluationResult]
