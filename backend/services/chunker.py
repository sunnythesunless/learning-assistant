from core.config import settings
import logging

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
    source_metadata: dict = None,
) -> list[dict]:
    """
    Split text into overlapping chunks with metadata.
    Uses recursive character splitting on paragraph/sentence boundaries.

    Returns: [{ content: str, metadata: { source, chunk_index, ... } }]
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    if not text or not text.strip():
        return []

    # Split by paragraphs first, then recombine to fit chunk_size
    separators = ["\n\n", "\n", ". ", " "]
    chunks = _recursive_split(text, separators, chunk_size, chunk_overlap)

    # Apply max chunks limit
    if len(chunks) > settings.MAX_CHUNKS_PER_SESSION:
        logger.warning(
            f"Truncating chunks from {len(chunks)} to {settings.MAX_CHUNKS_PER_SESSION}"
        )
        chunks = chunks[: settings.MAX_CHUNKS_PER_SESSION]

    # Add metadata to each chunk
    result = []
    for i, chunk_text in enumerate(chunks):
        metadata = {
            "chunk_index": i,
            "total_chunks": len(chunks),
            **(source_metadata or {}),
        }
        result.append({"content": chunk_text, "metadata": metadata})

    logger.info(f"Created {len(result)} chunks from text ({len(text)} chars)")
    return result


def _recursive_split(
    text: str, separators: list[str], chunk_size: int, chunk_overlap: int
) -> list[str]:
    """Recursively split text using multiple separators."""
    chunks = []
    current_separator = separators[0] if separators else ""

    # Split by the current separator
    if current_separator:
        parts = text.split(current_separator)
    else:
        # Last resort: split by character count
        parts = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)]
        return [p for p in parts if p.strip()]

    current_chunk = ""

    for part in parts:
        test_chunk = (
            current_chunk + current_separator + part if current_chunk else part
        )

        if len(test_chunk) <= chunk_size:
            current_chunk = test_chunk
        else:
            if current_chunk:
                if len(current_chunk) > chunk_size and len(separators) > 1:
                    # Current chunk is still too big, split further
                    sub_chunks = _recursive_split(
                        current_chunk, separators[1:], chunk_size, chunk_overlap
                    )
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(current_chunk.strip())

            current_chunk = part

    # Don't forget the last chunk
    if current_chunk.strip():
        if len(current_chunk) > chunk_size and len(separators) > 1:
            sub_chunks = _recursive_split(
                current_chunk, separators[1:], chunk_size, chunk_overlap
            )
            chunks.extend(sub_chunks)
        else:
            chunks.append(current_chunk.strip())

    # Apply overlap by prepending part of the previous chunk
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            overlap_text = prev[-chunk_overlap:] if len(prev) > chunk_overlap else prev
            overlapped.append(overlap_text + " " + chunks[i])
        chunks = overlapped

    return [c for c in chunks if c.strip()]
