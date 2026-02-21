-- =============================================
-- AI Learning Assistant - Supabase Schema Setup
-- Run this in your Supabase SQL Editor
-- =============================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ── Sessions ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('youtube', 'pdf')),
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Document Chunks with Embeddings ─────────────────────────────
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(3072),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for filtering by session (vector search uses sequential scan, fine for our data size)
CREATE INDEX IF NOT EXISTS idx_documents_session
    ON documents (session_id);

-- ── Similarity Search Function ──────────────────────────────────
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(3072),
    match_session_id UUID,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        d.id,
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM documents d
    WHERE d.session_id = match_session_id
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- ── Chat Messages ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_session
    ON chat_messages (session_id, created_at);

-- ── Generated Content Cache ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    content_type TEXT NOT NULL CHECK (content_type IN ('flashcards', 'quiz')),
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_generated_session
    ON generated_content (session_id, content_type);
