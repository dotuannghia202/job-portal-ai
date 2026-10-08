from fastapi import APIRouter, HTTPException
import logging

from schemas.ai_schemas import GenerateInterviewQuestionRequest, RestResponse
from services.llm_service import generate_interview_questions

router = APIRouter(prefix="/api/v1/ai", tags=["Interview Generation"])

logger = logging.getLogger(__name__)

@router.post("/generation/interview-questions", response_model=RestResponse[list])
async def generate_interview_question_api(request: GenerateInterviewQuestionRequest):
    try:
        questions = generate_interview_questions(
            job_text=request.job_text,
            cv_text=request.cv_text
        )
        return RestResponse(
            status_code=200,
            message="Successfully generate interview questions using AI!",
            data=questions,
            error=None
        )
    except Exception as e:
        logger.exception(f"Error generating interview questions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(e)}"
        )
