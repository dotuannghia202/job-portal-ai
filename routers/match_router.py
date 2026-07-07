from fastapi import APIRouter, HTTPException
from schemas.ai_schemas import MatchRequest, MatchData, RestResponse
from services.llm_service import calculate_match_score_by_gemini

router = APIRouter(prefix="/api/v1/ai", tags=["AI Matching"])

@router.post("/match", response_model=RestResponse[MatchData])
async def match_cv_job(request: MatchRequest):
    try:
        result_dict = calculate_match_score_by_gemini(request.job_text, request.cv_text)
        data_obj = MatchData(**result_dict)
        return RestResponse(
            status_code=200,
            message="Phân tích CV bằng Gemini AI thành công!",
            data=data_obj,
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))