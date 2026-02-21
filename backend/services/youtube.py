import re
from youtube_transcript_api import YouTubeTranscriptApi
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


def fetch_transcript(url: str) -> dict:
    """
    Fetch transcript from a YouTube video URL.
    Tries English first, then falls back to any available language.
    Returns: { text: str, title: str, video_id: str, source_url: str }
    """
    video_id = extract_video_id(url)
    logger.info(f"[YouTube] Fetching transcript for video: {video_id}")

    try:
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

        logger.info(f"[YouTube] Got {len(snippets)} transcript snippets")

        if not snippets:
            logger.error("[YouTube] Transcript snippets list is empty")
            raise ProcessingError(
                "Transcript is empty. The video may not have captions."
            )

        # Combine all transcript snippets into full text
        full_text = " ".join([s.text for s in snippets])
        logger.info(f"[YouTube] Combined transcript length: {len(full_text)} chars")

        if len(full_text.strip()) < 50:
            logger.error(f"[YouTube] Transcript too short: {len(full_text.strip())} chars")
            raise ProcessingError(
                "Transcript too short to generate meaningful content."
            )

        title = f"YouTube Video ({video_id})"

        logger.info(f"[YouTube] ✅ Successfully fetched transcript: {len(full_text)} chars, language: {lang_used}")

        return {
            "text": full_text,
            "title": title,
            "video_id": video_id,
            "source_url": url,
        }

    except ProcessingError:
        raise
    except Exception as e:
        logger.error(f"[YouTube] ❌ Failed to fetch transcript: {type(e).__name__}: {e}")
        raise ProcessingError(f"Failed to fetch transcript: {str(e)}")

