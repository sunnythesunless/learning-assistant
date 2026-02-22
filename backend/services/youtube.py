import re
import httpx
from youtube_transcript_api import YouTubeTranscriptApi
from core.config import settings
from core.error_handlers import ProcessingError
import logging

logger = logging.getLogger(__name__)

# Create a single instance (v1.2.x is class-based)
_ytt_api = YouTubeTranscriptApi()


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            logger.info(f"[YouTube] Extracted video ID: {video_id} from URL: {url}")
            return video_id

    logger.error(f"[YouTube] Could not extract video ID from URL: {url}")
    raise ProcessingError(f"Invalid YouTube URL: {url}")


def _fetch_via_supadata(video_id: str) -> str:
    """
    Fetch transcript using the Supadata API (works from cloud IPs).
    Returns the full transcript text.
    """
    logger.info(f"[YouTube] Trying Supadata API for video: {video_id}")
    try:
        response = httpx.get(
            "https://api.supadata.ai/v1/youtube/transcript",
            params={"videoId": video_id, "text": "true"},
            headers={"x-api-key": settings.SUPADATA_API_KEY},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        # The API returns { "content": "..." } when text=true
        text = data.get("content") or data.get("text") or data.get("transcript", "")
        if not text or len(text.strip()) < 50:
            raise ValueError(f"Supadata returned insufficient text ({len(text.strip())} chars)")

        logger.info(f"[YouTube] ✅ Supadata API returned {len(text)} chars")
        return text

    except httpx.HTTPStatusError as e:
        logger.warning(f"[YouTube] Supadata API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        raise
    except Exception as e:
        logger.warning(f"[YouTube] Supadata API failed: {type(e).__name__}: {e}")
        raise


def _fetch_via_library(video_id: str) -> tuple[str, str]:
    """
    Fetch transcript using youtube-transcript-api library (works from non-cloud IPs).
    Returns (full_text, language_used).
    """
    logger.info(f"[YouTube] Trying youtube-transcript-api library for video: {video_id}")

    # Try English first
    try:
        result = _ytt_api.fetch(video_id, languages=["en", "en-US", "en-GB"])
        lang_used = "en"
        logger.info("[YouTube] Found English transcript")
    except Exception:
        # Fall back: list all available transcripts and pick the first one
        logger.info("[YouTube] No English transcript, checking other languages...")
        transcript_list = _ytt_api.list(video_id)
        available = list(transcript_list)

        if not available:
            raise ProcessingError(
                "No transcripts available for this video."
            )

        # Pick the first available transcript
        chosen = available[0]
        lang_used = chosen.language
        logger.info(
            f"[YouTube] Using transcript: {chosen.language} "
            f"({chosen.language_code}, auto-generated={chosen.is_generated})"
        )
        result = chosen.fetch()

    snippets = result.snippets

    if not snippets:
        raise ProcessingError(
            "Transcript is empty. The video may not have captions."
        )

    full_text = " ".join([s.text for s in snippets])
    logger.info(f"[YouTube] ✅ Library returned {len(full_text)} chars, language: {lang_used}")
    return full_text, lang_used


def fetch_transcript(url: str) -> dict:
    """
    Fetch transcript from a YouTube video URL.
    Strategy:
      1. If SUPADATA_API_KEY is set → try Supadata API first (works from cloud IPs)
      2. Fall back to youtube-transcript-api library (works from local/residential IPs)
    Returns: { text: str, title: str, video_id: str, source_url: str }
    """
    video_id = extract_video_id(url)
    logger.info(f"[YouTube] Fetching transcript for video: {video_id}")

    full_text = None
    lang_used = "unknown"

    # ── Strategy 1: Supadata API (cloud-friendly) ──
    if settings.SUPADATA_API_KEY:
        try:
            full_text = _fetch_via_supadata(video_id)
            lang_used = "auto (Supadata)"
        except Exception as e:
            logger.warning(f"[YouTube] Supadata failed, falling back to library: {e}")
    else:
        logger.info("[YouTube] No SUPADATA_API_KEY configured, using library directly")

    # ── Strategy 2: Direct library (fallback) ──
    if full_text is None:
        try:
            full_text, lang_used = _fetch_via_library(video_id)
        except ProcessingError:
            raise
        except Exception as e:
            logger.error(f"[YouTube] ❌ Library also failed: {type(e).__name__}: {e}")
            raise ProcessingError(f"Failed to fetch transcript: {str(e)}")

    if len(full_text.strip()) < 50:
        raise ProcessingError(
            "Transcript too short to generate meaningful content."
        )

    title = f"YouTube Video ({video_id})"

    logger.info(
        f"[YouTube] ✅ Successfully fetched transcript: "
        f"{len(full_text)} chars, language: {lang_used}"
    )

    return {
        "text": full_text,
        "title": title,
        "video_id": video_id,
        "source_url": url,
    }
