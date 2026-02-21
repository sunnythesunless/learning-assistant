import json
from models.database import get_supabase
from core.config import settings
from core.error_handlers import ProcessingError, RetrievalError
import logging

logger = logging.getLogger(__name__)


def create_session(title: str, source_type: str, source_url: str = None) -> str:
    """Create a new learning session. Returns session_id."""
    logger.info(f"[VectorStore] Creating session: title={title}, type={source_type}")
    supabase = get_supabase()

    data = {
        "title": title,
        "source_type": source_type,
    }
    if source_url:
        data["source_url"] = source_url

    try:
        result = supabase.table("sessions").insert(data).execute()
    except Exception as e:
        logger.error(f"[VectorStore] ❌ Supabase insert sessions failed: {type(e).__name__}: {e}")
        raise ProcessingError(f"Database error creating session: {str(e)}")

    if not result.data:
        logger.error(f"[VectorStore] ❌ No data returned from sessions insert")
        raise ProcessingError("Failed to create session.")

    session_id = result.data[0]["id"]
    logger.info(f"[VectorStore] ✅ Created session: {session_id}")
    return session_id


def store_chunks(session_id: str, chunks: list[dict], embeddings: list[list[float]]):
    """Store document chunks with their embeddings."""
    logger.info(f"[VectorStore] Storing {len(chunks)} chunks for session {session_id}")
    supabase = get_supabase()

    rows = []
    for chunk, embedding in zip(chunks, embeddings):
        rows.append(
            {
                "session_id": session_id,
                "content": chunk["content"],
                "metadata": json.dumps(chunk["metadata"]),
                "embedding": embedding,
            }
        )

    # Insert in batches of 50
    batch_size = 50
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        batch_num = i // batch_size + 1
        try:
            supabase.table("documents").insert(batch).execute()
            logger.info(f"[VectorStore] ✅ Inserted batch {batch_num} ({len(batch)} rows)")
        except Exception as e:
            logger.error(f"[VectorStore] ❌ Batch {batch_num} insert failed: {type(e).__name__}: {e}")
            raise ProcessingError(f"Database error storing chunks: {str(e)}")

    logger.info(f"[VectorStore] ✅ All {len(rows)} chunks stored successfully")


def similarity_search(
    query_embedding: list[float],
    session_id: str,
    top_k: int = None,
    threshold: float = None,
) -> list[dict]:
    """
    Find similar documents using cosine similarity.
    Filters by similarity threshold for quality RAG.
    """
    supabase = get_supabase()
    top_k = top_k or settings.TOP_K_RESULTS
    threshold = threshold or settings.SIMILARITY_THRESHOLD

    result = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_session_id": session_id,
            "match_count": top_k,
        },
    ).execute()

    if not result.data:
        raise RetrievalError(
            "No relevant content found for your question. "
            "Try rephrasing or ask about the processed content."
        )

    # Apply similarity threshold filtering
    filtered = [doc for doc in result.data if doc.get("similarity", 0) > threshold]

    if not filtered:
        # Fall back to top results even below threshold, but warn
        logger.warning(
            f"No results above threshold {threshold}. "
            f"Best similarity: {result.data[0].get('similarity', 0):.3f}"
        )
        filtered = result.data[:3]  # Return top 3 anyway

    logger.info(
        f"Similarity search: {len(filtered)} results "
        f"(threshold={threshold}, session={session_id})"
    )
    return filtered


def get_all_chunks(session_id: str) -> list[dict]:
    """Get all document chunks for a session (for flashcard/quiz generation)."""
    supabase = get_supabase()

    result = (
        supabase.table("documents")
        .select("content, metadata")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )

    if not result.data:
        raise RetrievalError(f"No content found for session {session_id}")

    return result.data


def get_session(session_id: str) -> dict:
    """Get session details."""
    supabase = get_supabase()

    result = (
        supabase.table("sessions")
        .select("*")
        .eq("id", session_id)
        .single()
        .execute()
    )

    if not result.data:
        raise RetrievalError(f"Session not found: {session_id}")

    return result.data


def save_chat_message(session_id: str, role: str, content: str):
    """Save a chat message to history."""
    supabase = get_supabase()
    supabase.table("chat_messages").insert(
        {"session_id": session_id, "role": role, "content": content}
    ).execute()


def get_chat_history(session_id: str, limit: int = None) -> list[dict]:
    """Get recent chat history for a session."""
    supabase = get_supabase()
    limit = limit or settings.MAX_CHAT_HISTORY

    result = (
        supabase.table("chat_messages")
        .select("role, content")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    # Reverse to get chronological order
    messages = list(reversed(result.data)) if result.data else []
    return messages


def save_generated_content(session_id: str, content_type: str, content: dict):
    """Cache generated flashcards/quiz."""
    supabase = get_supabase()
    supabase.table("generated_content").insert(
        {
            "session_id": session_id,
            "content_type": content_type,
            "content": json.dumps(content),
        }
    ).execute()


def get_generated_content(session_id: str, content_type: str) -> dict | None:
    """Get cached generated content."""
    supabase = get_supabase()

    result = (
        supabase.table("generated_content")
        .select("content")
        .eq("session_id", session_id)
        .eq("content_type", content_type)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if result.data:
        content = result.data[0]["content"]
        return json.loads(content) if isinstance(content, str) else content
    return None
