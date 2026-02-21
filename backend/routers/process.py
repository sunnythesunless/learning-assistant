from fastapi import APIRouter, UploadFile, File
from models.schemas import ProcessVideoRequest, ProcessResponse
from services.youtube import fetch_transcript
from services.pdf import extract_text_from_pdf
from services.chunker import chunk_text
from services.embeddings import generate_embeddings
from services.vector_store import create_session, store_chunks
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process-video", response_model=ProcessResponse)
async def process_video(request: ProcessVideoRequest):
    """Process a YouTube video: extract transcript, chunk, embed, and store."""
    logger.info(f"━━━ /process-video ━━━ URL: {request.url}")

    # 1. Extract transcript
    logger.info("[Step 1/5] Extracting transcript...")
    result = fetch_transcript(request.url)
    logger.info(f"[Step 1/5] ✅ Transcript extracted: {len(result['text'])} chars")

    # 2. Create session
    logger.info("[Step 2/5] Creating session in Supabase...")
    session_id = create_session(
        title=result["title"],
        source_type="youtube",
        source_url=request.url,
    )
    logger.info(f"[Step 2/5] ✅ Session created: {session_id}")

    # 3. Chunk the text
    logger.info("[Step 3/5] Chunking text...")
    chunks = chunk_text(
        result["text"],
        source_metadata={
            "source_type": "youtube",
            "video_id": result["video_id"],
            "source_url": request.url,
        },
    )
    logger.info(f"[Step 3/5] ✅ Created {len(chunks)} chunks")

    # 4. Generate embeddings
    logger.info("[Step 4/5] Generating embeddings via Gemini...")
    texts = [c["content"] for c in chunks]
    embeddings = generate_embeddings(texts)
    logger.info(f"[Step 4/5] ✅ Generated {len(embeddings)} embeddings")

    # 5. Store in vector database
    logger.info("[Step 5/5] Storing chunks + embeddings in Supabase...")
    store_chunks(session_id, chunks, embeddings)
    logger.info(f"[Step 5/5] ✅ Stored successfully!")

    logger.info(f"━━━ /process-video COMPLETE ━━━ session_id={session_id}, chunks={len(chunks)}")

    return ProcessResponse(
        session_id=session_id,
        title=result["title"],
        chunk_count=len(chunks),
        source_type="youtube",
    )


@router.post("/process-pdf", response_model=ProcessResponse)
async def process_pdf(file: UploadFile = File(...)):
    """Process a PDF file: extract text, chunk, embed, and store."""
    logger.info(f"━━━ /process-pdf ━━━ filename: {file.filename}")

    # 1. Read the file
    logger.info("[Step 1/6] Reading uploaded file...")
    file_bytes = await file.read()
    logger.info(f"[Step 1/6] ✅ Read {len(file_bytes)} bytes ({len(file_bytes)/1024/1024:.1f} MB)")

    # 2. Extract text
    logger.info("[Step 2/6] Extracting text from PDF...")
    result = extract_text_from_pdf(file_bytes, file.filename)
    logger.info(f"[Step 2/6] ✅ Extracted {len(result['text'])} chars from {result['page_count']} pages")

    # 3. Create session
    logger.info("[Step 3/6] Creating session in Supabase...")
    session_id = create_session(
        title=result["title"],
        source_type="pdf",
    )
    logger.info(f"[Step 3/6] ✅ Session created: {session_id}")

    # 4. Chunk the text
    logger.info("[Step 4/6] Chunking text...")
    chunks = chunk_text(
        result["text"],
        source_metadata={
            "source_type": "pdf",
            "filename": file.filename,
            "page_count": result["page_count"],
        },
    )
    logger.info(f"[Step 4/6] ✅ Created {len(chunks)} chunks")

    # 5. Generate embeddings
    logger.info("[Step 5/6] Generating embeddings via Gemini...")
    texts = [c["content"] for c in chunks]
    embeddings = generate_embeddings(texts)
    logger.info(f"[Step 5/6] ✅ Generated {len(embeddings)} embeddings")

    # 6. Store in vector database
    logger.info("[Step 6/6] Storing chunks + embeddings in Supabase...")
    store_chunks(session_id, chunks, embeddings)
    logger.info(f"[Step 6/6] ✅ Stored successfully!")

    logger.info(f"━━━ /process-pdf COMPLETE ━━━ session_id={session_id}, chunks={len(chunks)}")

    return ProcessResponse(
        session_id=session_id,
        title=result["title"],
        chunk_count=len(chunks),
        source_type="pdf",
    )
