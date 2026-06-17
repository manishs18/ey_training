from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest
from app.services.rag_service import answer_question

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):

    answer = await answer_question(
        request.question
    )

    return {
        "answer": answer
    }