from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

from routers import cv_router, jd_router, match_router

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Job Portal AI Microservice",
    description="Hệ thống AI xử lý CV và JD",
    version="1.0.0"
)

# GLOBAL EXCEPTION HANDLERS (Giống hệt @RestControllerAdvice)
# ================================================================

# 1. Bắt lỗi HTTP do mình chủ động ném ra (VD: raise HTTPException)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": "Xử lý thất bại!",
            "data": None,
            "error": exc.detail # Bỏ lỗi vào trường error
        }
    )

# 2. Bắt lỗi Validation (Khi gửi sai định dạng JSON)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "status_code": 400,
            "message": "Dữ liệu đầu vào không hợp lệ",
            "data": None,
            "error": str(exc.errors())
        }
    )

# 3. Bắt mọi lỗi Exception chung chung (Lỗi 500 sập Server)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status_code": 500,
            "message": "Lỗi hệ thống nội bộ Server",
            "data": None,
            "error": str(exc)
        }
    )

# Tạo một DTO đơn giản (Trong Python dùng Pydantic)
class HelloResponse(BaseModel):
    message: str
    status: int

# GẮN ROUTER
# ================================================================
app.include_router(cv_router.router)
app.include_router(match_router.router)
app.include_router(jd_router.router)

# Viết API GET cơ bản (Giống @GetMapping)
@app.get("/", response_model=HelloResponse)
async def root():
    return {"status_code": 200, 
        "message": "Python AI Server đang chạy!", 
        "data": None, 
        "error": None}