# routers/knowledge_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from schemas.ai_schemas import RestResponse
from services.vector_service import add_custom_question

router = APIRouter(prefix="/api/v1/ai/knowledge", tags=["Custom Knowledge Base"])

class AddQuestionRequest(BaseModel):
    specialization: str  # For example: "Backend Java", "Digital Marketing", "Kế toán"
    question_text: str   # The question you came up with yourself
    rubric: str          # The criteria you want the AI to follow when answering

@router.post("/add-question", response_model=RestResponse[dict])
async def add_question(req: AddQuestionRequest):
    try:
        q_id = str(uuid.uuid4())
        add_custom_question(
            question_id=q_id,
            specialization=req.specialization,
            question_text=req.question_text,
            rubric=req.rubric
        )
        return RestResponse(
            status_code=200,
            message="Successfully added question to the knowledge base!",
            data={"id": q_id, "specialization": req.specialization},
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))