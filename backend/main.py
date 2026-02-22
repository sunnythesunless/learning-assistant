from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.error_handlers import (
    ProcessingError,
    GenerationError,
    RetrievalError,
    processing_error_handler,
    generation_error_handler,
    retrieval_error_handler,
    global_exception_handler,
)
from routers import process, generate, chat
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("main")

# ── Startup Config Validation ────────────────────────────────────
logger.info("=" * 60)
logger.info("🚀 AI Learning Assistant - Starting Up")
logger.info("=" * 60)

if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your_google_api_key_here":
    logger.warning("⚠️  GOOGLE_API_KEY is not set! Embeddings will fail.")
else:
    logger.info("✅ GOOGLE_API_KEY configured")

if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
    logger.warning("⚠️  GROQ_API_KEY is not set! LLM generation will fail.")
else:
    logger.info("✅ GROQ_API_KEY configured")

if not settings.SUPABASE_URL or settings.SUPABASE_URL == "your_supabase_url_here":
    logger.warning("⚠️  SUPABASE_URL is not set! Database features will fail.")
else:
    logger.info("✅ SUPABASE_URL configured")

if not settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_SERVICE_KEY == "your_supabase_service_role_key_here":
    logger.warning("⚠️  SUPABASE_SERVICE_KEY is not set!")
else:
    logger.info("✅ SUPABASE_SERVICE_KEY configured")

if not settings.SUPADATA_API_KEY or settings.SUPADATA_API_KEY == "your_supadata_api_key_here":
    logger.warning("⚠️  SUPADATA_API_KEY is not set! YouTube transcripts may fail on cloud deployments.")
else:
    logger.info("✅ SUPADATA_API_KEY configured (YouTube transcripts will use Supadata)")

logger.info(f"📌 LLM model (Groq): {settings.GROQ_MODEL}")
logger.info(f"📌 Embedding model: {settings.EMBEDDING_MODEL}")
logger.info(f"📌 Frontend URL: {settings.FRONTEND_URL}")
logger.info(f"📌 Server: {settings.HOST}:{settings.PORT}")
logger.info("=" * 60)

app = FastAPI(
    title="AI Learning Assistant",
    description="Process YouTube videos & PDFs to generate flashcards, quizzes, and contextual chat",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception Handlers ──────────────────────────────────────────
app.add_exception_handler(ProcessingError, processing_error_handler)
app.add_exception_handler(GenerationError, generation_error_handler)
app.add_exception_handler(RetrievalError, retrieval_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

# ── Routers ──────────────────────────────────────────────────────
app.include_router(process.router, tags=["Content Processing"])
app.include_router(generate.router, tags=["AI Generation"])
app.include_router(chat.router, tags=["Chat"])


@app.get("/")
async def health():
    return {"status": "ok", "service": "AI Learning Assistant API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
