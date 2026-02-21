# AI Learning Assistant 🧠

An AI-powered learning platform that transforms YouTube videos and PDFs into interactive flashcards, quizzes, and contextual AI chat using RAG (Retrieval-Augmented Generation).

![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat-square&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-pgvector-3ECF8E?style=flat-square&logo=supabase)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3-F55036?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-Embeddings-4285F4?style=flat-square&logo=google)

## Features

- **📺 YouTube Processing** — Extracts transcripts and processes them into study material
- **📄 PDF Upload** — Extracts text from PDFs with drag-and-drop support
- **🃏 Smart Flashcards** — AI-generated flashcards with difficulty levels (easy/medium/hard)
- **🧠 Interactive Quizzes** — MCQs with instant feedback, explanations, and scoring
- **💬 RAG Chat** — Context-aware AI chat with streaming responses and source citations
- **🎨 Premium UI** — Dark glassmorphism design with smooth animations

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ Landing   │  │Flashcard │  │  Quiz    │  │  Chat   ││
│  │  Page     │  │ Viewer   │  │Interface │  │ Window  ││
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬─────┘│
└───────┼──────────────┼────────────┼─────────────┼──────┘
        │              │            │             │
        ▼              ▼            ▼             ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Routers: /process-video, /process-pdf,             │ │
│  │          /generate-flashcards, /generate-quiz,     │ │
│  │          /chat (SSE streaming)                     │ │
│  └──────────────────┬─────────────────────────────────┘ │
│  ┌──────────────────┴─────────────────────────────────┐ │
│  │ Services: YouTube, PDF, Chunker, Embeddings, RAG,  │ │
│  │           Flashcard Gen, Quiz Gen, Vector Store     │ │
│  └──────────────────┬─────────────────────────────────┘ │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               Supabase (Postgres + pgvector)            │
│  sessions │ documents (embeddings) │ chat_messages │    │
│  generated_content │ match_documents() RPC             │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
        ┌───────────────┐   ┌───────────────┐
        │     Groq      │   │ Google Gemini  │
        │  (LLM - Chat, │   │ (Embeddings)  │
        │  Cards, Quiz) │   │               │
        └───────────────┘   └───────────────┘
```

## Tech Stack

| Layer       | Technology                            |
| ----------- | ------------------------------------- |
| Frontend    | Next.js 14 (App Router), TailwindCSS  |
| Backend     | Python, FastAPI                       |
| Database    | Supabase (Postgres + pgvector)        |
| LLM         | Groq (Llama 3.3 70B Versatile)        |
| Embeddings  | Google Gemini embedding-001 (3072d)   |
| Streaming   | Server-Sent Events (SSE)              |

## Setup Instructions

### Prerequisites

- Node.js 18+
- Python 3.11+
- [Supabase](https://supabase.com/) account (free tier)
- [Google AI API key](https://aistudio.google.com/apikey) (for embeddings)
- [Groq API key](https://console.groq.com/keys) (for LLM generation)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-learn-assistant.git
cd ai-learn-assistant
```

### 2. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the contents of `backend/schema.sql`
3. Copy your **Project URL** and **Service Role Key** from Settings → API

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys:
# GOOGLE_API_KEY=your_key     (for embeddings)
# GROQ_API_KEY=your_key       (for LLM generation)
# SUPABASE_URL=your_url
# SUPABASE_SERVICE_KEY=your_key

# Start server
python main.py
```

Backend runs at `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at `http://localhost:3000`

## API Endpoints

| Method | Endpoint              | Description                    |
| ------ | --------------------- | ------------------------------ |
| POST   | `/process-video`      | Process YouTube video URL      |
| POST   | `/process-pdf`        | Upload and process PDF file    |
| POST   | `/generate-flashcards`| Generate flashcards for session|
| POST   | `/generate-quiz`      | Generate quiz for session      |
| POST   | `/chat`               | RAG chat with SSE streaming    |
| GET    | `/`                   | Health check                   |

## Key Design Decisions

- **RAG with threshold filtering**: Similarity search uses a `0.75` threshold to filter low-quality context, with graceful fallback to top-3 results
- **Deterministic AI output**: Flashcard/quiz generation uses `temperature=0.2` + 2-attempt retry with JSON validation
- **Content caching**: Generated flashcards and quizzes are cached in the database to avoid redundant API calls
- **Chat history trimming**: Only the last 6 messages are sent to the LLM to stay within token limits
- **Performance safeguards**: Max 20MB PDF, max 500 chunks/session, batched embedding generation

## Error Handling

- Custom exception classes (`ProcessingError`, `GenerationError`, `RetrievalError`)
- Global exception handler for unhandled errors
- Per-service input validation (invalid URLs, empty PDFs, malformed LLM output)
- Frontend error states with retry buttons

## License

MIT
