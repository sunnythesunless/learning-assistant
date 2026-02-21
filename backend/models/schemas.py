from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


# ── Request Models ──────────────────────────────────────────────

class ProcessVideoRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL")


class GenerateRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from content processing")


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    message: str = Field(..., min_length=1, description="User message")


# ── Response Models ─────────────────────────────────────────────

class ProcessResponse(BaseModel):
    session_id: str
    title: str
    chunk_count: int
    source_type: str


class Flashcard(BaseModel):
    front: str
    back: str
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")


class FlashcardResponse(BaseModel):
    session_id: str
    flashcards: list[Flashcard]
    count: int


class QuizOption(BaseModel):
    label: str
    text: str


class QuizQuestion(BaseModel):
    question: str
    options: list[QuizOption]
    correct_answer: str
    explanation: str


class QuizResponse(BaseModel):
    session_id: str
    questions: list[QuizQuestion]
    count: int


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ErrorResponse(BaseModel):
    error: str
    message: str
