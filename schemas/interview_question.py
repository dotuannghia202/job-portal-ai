import json
from enum import Enum
from google.genai import types
from pydantic import BaseModel, Field


# ⚠️ NOTE: The values here MUST MATCH 100% with QuestionCategory.kt in Java/Kotlin
class QuestionCategoryEnum(str, Enum):
    PROJECT_DEEP_DIVE = "PROJECT_DEEP_DIVE"  # Xoáy sâu dự án trong CV
    TECHNICAL_CORE = (
        "TECHNICAL_CORE"  # Kiến thức kỹ thuật cốt lõi theo JD
    )
    SITUATIONAL = "SITUATIONAL"  # Tình huống thực tế / Kỹ năng mềm
    PROBLEM_SOLVING = "PROBLEM_SOLVING"  # Tư duy giải quyết vấn đề


class InterviewQuestionItem(BaseModel):
    order_index: int = Field(
        ..., description="Thứ tự câu hỏi từ 1 đến 5", ge=1, le=5
    )
    category: QuestionCategoryEnum = Field(
        ...,
        description=(
            "Loại câu hỏi (chỉ nhận: PROJECT_DEEP_DIVE, TECHNICAL_CORE,"
            " SITUATIONAL, PROBLEM_SOLVING)"
        ),
    )
    question_text: str = Field(..., description="Nội dung câu hỏi phỏng vấn")
    time_limit_seconds: int = Field(
        ...,
        description="Thời gian trả lời (ví dụ: 60, 90, 120 giây)",
        ge=30,
        le=300,
    )
    rubric: str = Field(
        ...,
        description=(
            "Tiêu chí chấm điểm câu trả lời chi tiết theo thang điểm/yếu tố cần"
            " đạt"
        ),
    )
