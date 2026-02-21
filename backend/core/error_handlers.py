from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class ProcessingError(Exception):
    """Raised when content processing fails (transcript unavailable, PDF unreadable)."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class GenerationError(Exception):
    """Raised when AI generation fails (malformed JSON, empty output)."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RetrievalError(Exception):
    """Raised when RAG retrieval fails (no matching documents, embedding failure)."""

    def __init__(self, message: str, status_code: int = 404):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def processing_error_handler(request: Request, exc: ProcessingError):
    logger.warning(f"Processing error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "processing_error", "message": exc.message},
    )


async def generation_error_handler(request: Request, exc: GenerationError):
    logger.error(f"Generation error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "generation_error", "message": exc.message},
    )


async def retrieval_error_handler(request: Request, exc: RetrievalError):
    logger.warning(f"Retrieval error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "retrieval_error", "message": exc.message},
    )


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred. Please try again.",
        },
    )
