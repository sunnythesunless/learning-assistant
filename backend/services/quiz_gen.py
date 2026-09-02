import json
import time
from openai import OpenAI
from core.config import settings
from core.error_handlers import GenerationError
from services.vector_store import get_all_chunks, save_generated_content, get_generated_content
from prompts.quiz import QUIZ_SYSTEM_PROMPT, QUIZ_USER_PROMPT
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


def generate_quiz(session_id: str, count: int = 8) -> list[dict]:
    """
    Generate quiz questions for a session using Groq.
    Uses caching to avoid re-generating.
    """
    # Check cache first
    cached = get_generated_content(session_id, "quiz")
    if cached:
        logger.info(f"[Quiz] Returning cached quiz for session {session_id}")
        return cached

    # Get all chunks for the session
    chunks = get_all_chunks(session_id)
    content_text = "\n\n".join([c["content"] for c in chunks])

    # Truncate to stay within Groq free-tier token limits (12K TPM)
    max_content_len = 12000
    if len(content_text) > max_content_len:
        content_text = content_text[:max_content_len]

    client = _get_client()
    system_prompt = QUIZ_SYSTEM_PROMPT.format(count=count)
    user_prompt = QUIZ_USER_PROMPT.format(count=count, content=content_text)

    # Retry logic
    last_error = None
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            logger.info(f"[Quiz] Generating via Groq (attempt {attempt + 1}/{max_attempts})...")

            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=settings.TEMPERATURE,
                response_format={"type": "json_object"},
            )

            raw_text = response.choices[0].message.content.strip()

            # Clean markdown code fences
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3].strip()

            parsed = json.loads(raw_text)

            # Handle both {"questions": [...]} wrapper and direct [...] array
            if isinstance(parsed, dict):
                questions = None
                for v in parsed.values():
                    if isinstance(v, list):
                        questions = v
                        break
                if questions is None:
                    raise ValueError("JSON object does not contain a list of questions")
            else:
                questions = parsed

            # Validate structure
            if not isinstance(questions, list) or len(questions) == 0:
                raise ValueError("Expected non-empty list of questions")

            for q in questions:
                required = ("question", "options", "correct_answer", "explanation")
                if not all(k in q for k in required):
                    raise ValueError(f"Question missing required fields: {q}")
                if not isinstance(q["options"], list) or len(q["options"]) != 4:
                    raise ValueError(f"Expected exactly 4 options: {q}")
                if q["correct_answer"] not in ("A", "B", "C", "D"):
                    raise ValueError(f"Invalid correct_answer: {q['correct_answer']}")

            # Cache the result
            save_generated_content(session_id, "quiz", questions)
            logger.info(f"[Quiz] ✅ Generated {len(questions)} quiz questions via Groq")
            return questions

        except json.JSONDecodeError as e:
            last_error = e
            logger.warning(f"[Quiz] JSON parsing failed (attempt {attempt + 1}): {e}")
        except ValueError as e:
            last_error = e
            logger.warning(f"[Quiz] Validation failed (attempt {attempt + 1}): {e}")
        except Exception as e:
            last_error = e
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                delay = 10
                logger.warning(f"[Quiz] ⏳ Rate limited. Waiting {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"[Quiz] ❌ Generation failed (attempt {attempt + 1}): {e}")
                time.sleep(5)  # Brief pause before retry

    raise GenerationError(
        f"Failed to generate quiz after {max_attempts} attempts: {str(last_error)}"
    )
