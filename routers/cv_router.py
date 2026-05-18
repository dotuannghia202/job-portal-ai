from fastapi import APIRouter, HTTPException
from schemas.ai_schemas import ExtractCvRequest, ExtractCvResponse, RestResponse
from services.pdf_service import extract_text_from_pdf_url

router = APIRouter(prefix="/api/v1/ai", tags=["CV Processing"])

# Chú ý: response_model bây giờ là RestResponse bọc lấy ExtractCvResponse
@router.post("/extract-cv", response_model=RestResponse[ExtractCvResponse])
async def extract_cv(request: ExtractCvRequest):
    try:
        # Gọi Service xử lý
        text = extract_text_from_pdf_url(request.file_url)
        
        # Đóng gói data
        data_obj = ExtractCvResponse(parsed_text=text)
        
        # Trả về thành công
        return RestResponse(
            status_code=200,
            message="Text extracted from CV successfully!",
            data=data_obj,
            error=None
        )
        
    except Exception as e:
        # Ném lỗi ra, file main.py sẽ tự chộp lấy và bọc thành JSON lỗi
        raise HTTPException(status_code=400, detail=str(e))