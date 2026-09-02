import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    SUPADATA_API_KEY: str = os.getenv("SUPADATA_API_KEY", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Processing limits
    MAX_PDF_SIZE_MB: int = 20
    MAX_CHUNKS_PER_SESSION: int = 500
    EMBEDDING_BATCH_SIZE: int = 100

    # RAG settings
    SIMILARITY_THRESHOLD: float = 0.75
    TOP_K_RESULTS: int = 5
    MAX_CHAT_HISTORY: int = 6

    # LLM settings (Groq for generation, Gemini for embeddings)
    GROQ_MODEL: str = "llama-3.1-8b-instant"   
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    TEMPERATURE: float = 0.2

    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200


settings = Settings()
