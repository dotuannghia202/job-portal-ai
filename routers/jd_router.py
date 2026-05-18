import json

from fastapi import APIRouter, HTTPException
from schemas.ai_schemas import GenerateJdRequest, GenerateJdData, RestResponse
from services.llm_service import generate_job_description

router = APIRouter(prefix="/api/v1/ai", tags=["JD Generation"])

@router.post("/generate-jd", response_model=RestResponse[GenerateJdData])
async def generate_jd(request: GenerateJdRequest):
    try:
        # 1. Lấy chuỗi văn bản từ Gemini (Đang chứa \n và \")
        raw_text = generate_job_description(
            request.title, 
            request.skills, 
            request.company_culture, 
            request.levels
        )
        
        # 2. 🚨 ÉP CHUỖI ĐÓ THÀNH ĐỐI TƯỢNG JSON THẬT
        try:
            parsed_json = json.loads(raw_text)
        except json.JSONDecodeError:
            # Đề phòng AI dở chứng trả về văn bản linh tinh không phải JSON
            raise Exception("AI không trả về đúng định dạng JSON!")

        # 3. Gắn vào DTO (Bây giờ nó là 1 object xịn sò)
        data_obj = GenerateJdData(generated_jd=parsed_json)
        
        return RestResponse(
            status_code=200,
            message="Sinh mô tả công việc bằng AI thành công!",
            data=data_obj,
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))