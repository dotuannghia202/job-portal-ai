from fastapi import APIRouter, HTTPException
from schemas.ai_schemas import MatchRequest, MatchData, RestResponse
from services.ai_service import calculate_match_score

router = APIRouter(prefix="/api/v1/ai", tags=["AI Matching"])

@router.post("/match", response_model=RestResponse[MatchData])
async def match_cv_job(request: MatchRequest):
    try:
        # Gọi Service tính điểm
        score = calculate_match_score(request.job_text, request.cv_text)
        
        # Đóng gói kết quả
        data_obj = MatchData(match_score=score)
        
        return RestResponse(
            status_code=200,
            message="Chấm điểm CV thành công!",
            data=data_obj,
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))