from fastapi import FastAPI
from pydantic import BaseModel

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Job Portal AI Microservice",
    description="Hệ thống AI xử lý CV và JD",
    version="1.0.0"
)

# Tạo một DTO đơn giản (Trong Python dùng Pydantic)
class HelloResponse(BaseModel):
    message: str
    status: int

# Viết API GET cơ bản (Giống @GetMapping)
@app.get("/", response_model=HelloResponse)
async def root():
    return {"message": "Hello từ Python AI Backend!", "status": 200}