from google import genai
from core.config import settings
from core.error_handlers import ProcessingError
import logging

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    return _client


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts using Gemini.
    Processes in batches for efficiency.
    Returns: list of embedding vectors (3072 dims each)
    """
    if not texts:
        return []

    client = _get_client()
    all_embeddings = []
    batch_size = settings.EMBEDDING_BATCH_SIZE

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        logger.info(
            f"Generating embeddings for batch {i // batch_size + 1} "
            f"({len(batch)} texts)"
        )

        try:
            result = client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=batch,
            )
            all_embeddings.extend([e.values for e in result.embeddings])
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise ProcessingError(f"Failed to generate embeddings: {str(e)}")

    return all_embeddings


def generate_single_embedding(text: str) -> list[float]:
    """Generate embedding for a single text (used for search queries)."""
    results = generate_embeddings([text])
    if not results:
        raise ProcessingError("Failed to generate embedding for query.")
    return results[0]
