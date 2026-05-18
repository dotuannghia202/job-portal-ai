from fastapi import APIRouter, HTTPException
from schemas.ai_schemas import GenerateJdRequest, GenerateJdData, RestResponse
from services.llm_service import generate_job_description

router = APIRouter(prefix="/api/v1/ai", tags=["JD Generation"])

@router.post("/generate-jd", response_model=RestResponse[GenerateJdData])
async def generate_jd(request: GenerateJdRequest):
    try:
        text = generate_job_description(
            request.title,
            request.skills,
            request.location,
            request.experience
        )
        
        data_obj = GenerateJdData(generated_jd=text)
        
        return RestResponse(
            status_code=200,
            message="Sinh mô tả công việc bằng AI thành công!",
            data=data_obj,
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))