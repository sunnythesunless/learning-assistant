from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest
from services.rag import stream_chat_response
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    """RAG-based chat with streaming SSE response."""
    logger.info(f"━━━ /chat ━━━ session: {request.session_id}, message: {request.message[:80]}...")

    async def event_generator():
        try:
            async for chunk in stream_chat_response(request.session_id, request.message):
                data = json.dumps({"content": chunk})
                yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"
            logger.info("━━━ /chat COMPLETE ━━━")
        except Exception as e:
            logger.error(f"━━━ /chat ERROR ━━━ {type(e).__name__}: {e}")
            error_data = json.dumps({"content": f"Error: {str(e)}"})
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
