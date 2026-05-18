from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

# Khai báo chữ T (Generic Type) giống hệt Java
T = TypeVar("T")

# 1. CLASS BỌC RESPONSE CHUẨN MỰC
class RestResponse(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

# DTO Nhận dữ liệu từ Spring Boot gửi sang
class ExtractCvRequest(BaseModel):
    file_url: str

# DTO Trả dữ liệu về cho Spring Boot
class ExtractCvResponse(BaseModel):
    parsed_text: str

# --- DTO CHO CHỨC NĂNG MATCHING ---
class MatchRequest(BaseModel):
    job_text: str
    cv_text: str

class MatchData(BaseModel):
    match_score: float

# --- DTO CHO CHỨC NĂNG GEN JD ---
class GenerateJdRequest(BaseModel):
    title: str        # Tên công việc (VD: Senior Backend Java)
    skills: str       # Kỹ năng (VD: Spring Boot, PostgreSQL)
    location: str     # Địa điểm (VD: Hà Nội)
    experience: str   # Yêu cầu kinh nghiệm (VD: 2 năm)

class GenerateJdData(BaseModel):
    generated_jd: str # Bài văn JD do AI sinh ra