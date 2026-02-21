from fastapi import APIRouter
from models.schemas import GenerateRequest, FlashcardResponse, QuizResponse
from services.flashcard_gen import generate_flashcards
from services.quiz_gen import generate_quiz
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-flashcards", response_model=FlashcardResponse)
async def create_flashcards(request: GenerateRequest):
    """Generate flashcards from processed content."""
    logger.info(f"━━━ /generate-flashcards ━━━ session: {request.session_id}")

    flashcards = generate_flashcards(request.session_id)

    logger.info(f"━━━ /generate-flashcards COMPLETE ━━━ count={len(flashcards)}")

    return FlashcardResponse(
        session_id=request.session_id,
        flashcards=flashcards,
        count=len(flashcards),
    )


@router.post("/generate-quiz", response_model=QuizResponse)
async def create_quiz(request: GenerateRequest):
    """Generate quiz questions from processed content."""
    logger.info(f"━━━ /generate-quiz ━━━ session: {request.session_id}")

    questions = generate_quiz(request.session_id)

    logger.info(f"━━━ /generate-quiz COMPLETE ━━━ count={len(questions)}")

    return QuizResponse(
        session_id=request.session_id,
        questions=questions,
        count=len(questions),
    )
