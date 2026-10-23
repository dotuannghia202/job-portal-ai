import logging
from fastapi import APIRouter, HTTPException

from schemas.ai_schemas import GenerateInterviewQuestionRequest, RestResponse
from schemas.interview_question import SessionEvaluationRequest
from services.llm_service import generate_interview_questions, evaluate_interview_session

router = APIRouter(prefix="/api/v1/ai", tags=["Interview Generation & Evaluation"])

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
            message="Successfully generated bilingual interview questions!",
            data=questions,
            error=None
        )
    except Exception as e:
        logger.exception(f"Error generating interview questions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(e)}"
        )


@router.post("/interview/evaluate", response_model=RestResponse[dict])
async def evaluate_interview_session_api(request: SessionEvaluationRequest):
    try:
        result = evaluate_interview_session(request)
        return RestResponse(
            status_code=200,
            message="Interview session evaluated successfully!",
            data=result,
            error=None
        )
    except Exception as e:
        logger.exception(f"Error evaluating interview session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Interview evaluation failed: {str(e)}"
        )
