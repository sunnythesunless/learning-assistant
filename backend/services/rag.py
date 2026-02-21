from openai import OpenAI
from core.config import settings
from core.error_handlers import RetrievalError
from services.embeddings import generate_single_embedding
from services.vector_store import similarity_search, save_chat_message, get_chat_history
from prompts.chat import RAG_SYSTEM_PROMPT
import json
import logging

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
    return _client


def build_context(session_id: str, query: str) -> tuple[str, str]:
    """
    Retrieve relevant context for a query using RAG.
    Returns (context_text, sources_text).
    """
    # Generate embedding for the query (still uses Gemini)
    query_embedding = generate_single_embedding(query)

    # Similarity search with threshold filtering
    results = similarity_search(query_embedding, session_id)

    # Build context with source citations
    context_parts = []
    source_parts = []

    for i, doc in enumerate(results, 1):
        context_parts.append(f"[Source {i}]: {doc['content']}")

        metadata = doc.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}

        similarity = doc.get("similarity", 0)
        chunk_idx = metadata.get("chunk_index", "?")
        source_parts.append(
            f"- Source {i}: Chunk {chunk_idx} (relevance: {similarity:.0%})"
        )

    context_text = "\n\n".join(context_parts)
    sources_text = "\n".join(source_parts)

    return context_text, sources_text


async def stream_chat_response(session_id: str, message: str):
    """
    Stream a RAG-based chat response using Groq.
    Yields text chunks for SSE streaming.
    """
    # Get context via RAG
    context_text, sources_text = build_context(session_id, message)

    # Get chat history (last N messages)
    history = get_chat_history(session_id)

    # Build system prompt with RAG context
    system_prompt = RAG_SYSTEM_PROMPT.format(
        context=context_text, sources=sources_text
    )

    # Build messages list with history
    messages = [{"role": "system", "content": system_prompt}]

    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })

    # Add current user message
    messages.append({"role": "user", "content": message})

    # Save user message to history
    save_chat_message(session_id, "user", message)

    # Stream response from Groq
    client = _get_client()
    full_response = ""

    try:
        stream = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.7,  # Slightly higher for conversational
            stream=True,
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                yield text

    except Exception as e:
        logger.error(f"[Chat] ❌ Groq streaming error: {e}")
        error_msg = "I'm sorry, I encountered an error. Please try again."
        full_response = error_msg
        yield error_msg

    # Save assistant response to history
    if full_response:
        save_chat_message(session_id, "assistant", full_response)
