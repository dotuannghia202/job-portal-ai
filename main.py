from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

from routers import cv_router, jd_router, match_router, knowledge_router, interview_router

# Initialize FastAPI application
app = FastAPI(
    title="Job Portal AI Microservice",
    description="AI system for CV and JD processing",
    version="1.0.0"
)

# GLOBAL EXCEPTION HANDLERS (Similar to @RestControllerAdvice)
# ================================================================

# 1. Handle HTTP exceptions explicitly raised (e.g., raise HTTPException)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": "Processing failed!",
            "data": None,
            "error": exc.detail # Store error details in the error field
        }
    )

# 2. Handle validation errors (e.g., invalid JSON format or schema mismatch)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "status_code": 400,
            "message": "Invalid input data",
            "data": None,
            "error": str(exc.errors())
        }
    )

# 3. Catch all general unhandled exceptions (500 Internal Server Error)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status_code": 500,
            "message": "Internal server error",
            "data": None,
            "error": str(exc)
        }
    )

# Create a simple DTO (using Pydantic in Python)
class HelloResponse(BaseModel):
    message: str
    status: int

# REGISTER ROUTERS
# ================================================================
app.include_router(cv_router.router)
app.include_router(match_router.router)
app.include_router(jd_router.router)
app.include_router(knowledge_router.router)
app.include_router(interview_router.router)

# Basic GET API endpoint (similar to @GetMapping)
@app.get("/", response_model=HelloResponse)
async def root():
    return {"status_code": 200, 
        "message": "Python AI Server is running!", 
        "data": None, 
        "error": None}