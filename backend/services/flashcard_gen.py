import json
import time
import re
from openai import OpenAI
from core.config import settings
from core.error_handlers import GenerationError
from services.vector_store import get_all_chunks, save_generated_content, get_generated_content
from prompts.flashcard import FLASHCARD_SYSTEM_PROMPT, FLASHCARD_USER_PROMPT
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


def generate_flashcards(session_id: str, count: int = 12) -> list[dict]:
    """
    Generate flashcards for a session using Groq.
    Uses caching to avoid re-generating.
    """
    # Check cache first
    cached = get_generated_content(session_id, "flashcards")
    if cached:
        logger.info(f"[Flashcard] Returning cached flashcards for session {session_id}")
        return cached

    # Get all chunks for the session
    chunks = get_all_chunks(session_id)
    content_text = "\n\n".join([c["content"] for c in chunks])

    # Truncate to stay within Groq free-tier token limits (12K TPM)
    max_content_len = 12000
    if len(content_text) > max_content_len:
        content_text = content_text[:max_content_len]

    client = _get_client()
    system_prompt = FLASHCARD_SYSTEM_PROMPT.format(count=count)
    user_prompt = FLASHCARD_USER_PROMPT.format(count=count, content=content_text)

    # Retry logic
    last_error = None
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            logger.info(f"[Flashcard] Generating via Groq (attempt {attempt + 1}/{max_attempts})...")

            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=settings.TEMPERATURE,
            )

            raw_text = response.choices[0].message.content.strip()

            # Clean markdown code fences if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3].strip()

            flashcards = json.loads(raw_text)

            # Validate structure
            if not isinstance(flashcards, list) or len(flashcards) == 0:
                raise ValueError("Expected non-empty list of flashcards")

            for fc in flashcards:
                if not all(k in fc for k in ("front", "back", "difficulty")):
                    raise ValueError(f"Flashcard missing required fields: {fc}")
                if fc["difficulty"] not in ("easy", "medium", "hard"):
                    fc["difficulty"] = "medium"

            # Cache the result
            save_generated_content(session_id, "flashcards", flashcards)
            logger.info(f"[Flashcard] ✅ Generated {len(flashcards)} flashcards via Groq")
            return flashcards

        except json.JSONDecodeError as e:
            last_error = e
            logger.warning(f"[Flashcard] JSON parsing failed (attempt {attempt + 1}): {e}")
        except ValueError as e:
            last_error = e
            logger.warning(f"[Flashcard] Validation failed (attempt {attempt + 1}): {e}")
        except Exception as e:
            last_error = e
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                delay = 10
                logger.warning(f"[Flashcard] ⏳ Rate limited. Waiting {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"[Flashcard] ❌ Generation failed (attempt {attempt + 1}): {e}")
                time.sleep(5)  # Brief pause before retry

    raise GenerationError(
        f"Failed to generate flashcards after {max_attempts} attempts: {str(last_error)}"
    )
