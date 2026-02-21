# 🧠 AI Learning Assistant

**Transform any YouTube video or PDF into interactive flashcards, quizzes, and an AI-powered study companion — in seconds.**

Built with a **RAG (Retrieval-Augmented Generation)** pipeline: content is chunked, embedded, stored in a vector database, and retrieved contextually for accurate AI responses.

![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat-square&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129-009688?style=flat-square&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-pgvector-3ECF8E?style=flat-square&logo=supabase)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-Embeddings-4285F4?style=flat-square&logo=google)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📺 **YouTube Processing** | Extracts transcripts (multi-language support with auto-fallback) and processes into study material |
| 📄 **PDF Upload** | Drag-and-drop PDF text extraction (up to 20MB) |
| 🃏 **Smart Flashcards** | AI-generated flashcards with difficulty grading (easy / medium / hard) |
| 🧠 **Interactive Quizzes** | Multiple-choice questions with instant feedback, explanations, and scoring |
| 💬 **RAG Chat** | Context-aware AI chat with SSE streaming and source-grounded responses |
| 🎨 **Premium UI** | Dark glassmorphism design with smooth animations and full responsiveness |

---

## 🏗️ Architecture

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
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   Supabase   │ │   Groq   │ │Google Gemini │
│  (Postgres + │ │(LLM:Chat,│ │ (Embeddings  │
│   pgvector)  │ │Cards,Quiz│ │  3072-dim)   │
└──────────────┘ └──────────┘ └──────────────┘
```

### Data Flow (RAG Pipeline)

```
User Input → Transcript/PDF Extraction → Recursive Text Chunking
    → Gemini Embedding (3072-dim) → Supabase pgvector Storage
        → Similarity Search (cosine, threshold 0.75)
            → Context Injection → Groq LLM Generation → Response
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 (App Router), TailwindCSS | Responsive SPA with client-side routing |
| **Backend** | Python 3.11+, FastAPI | REST API with async handlers |
| **Database** | Supabase (Postgres + pgvector) | Vector storage, sessions, chat history |
| **LLM** | Groq (Llama 3.3 70B Versatile) | Flashcard, quiz, and chat generation |
| **Embeddings** | Google Gemini (embedding-001, 3072d) | Semantic vector representations |
| **Streaming** | Server-Sent Events (SSE) | Real-time chat token streaming |

---

## 🚀 Setup Instructions

### Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- [Supabase](https://supabase.com/) account (free tier works)
- [Google AI API key](https://aistudio.google.com/apikey) — for embeddings
- [Groq API key](https://console.groq.com/keys) — for LLM generation

### 1. Clone the Repository

```bash
git clone https://github.com/sunnythesunless/learning-assistant.git
cd learning-assistant
```

### 2. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the contents of [`backend/schema.sql`](backend/schema.sql)
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
# Edit .env with your API keys:
#   GOOGLE_API_KEY=...     (embeddings)
#   GROQ_API_KEY=...       (LLM generation)
#   SUPABASE_URL=...       (database)
#   SUPABASE_SERVICE_KEY=...(database auth)

# Start server
python main.py
```

Backend runs at `http://localhost:8000` — Swagger docs at `/docs`.

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at `http://localhost:3000`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/process-video` | Process YouTube video URL → chunks + embeddings |
| `POST` | `/process-pdf` | Upload PDF → chunks + embeddings |
| `POST` | `/generate-flashcards` | Generate flashcards for a session |
| `POST` | `/generate-quiz` | Generate quiz questions for a session |
| `POST` | `/chat` | RAG chat with SSE streaming response |

Interactive API documentation available at `http://localhost:8000/docs`

---

## 🧩 Key Design Decisions

### AI Integration
- **Dual-provider architecture**: Groq handles LLM generation (speed), Gemini handles embeddings (quality)
- **Deterministic output**: `temperature=0.2` with structured JSON prompts + 3-attempt retry with validation
- **Content caching**: Generated flashcards/quizzes are cached in DB to avoid redundant API calls
- **Token management**: Content truncation to stay within Groq TPM limits; chat history trimmed to last 6 messages

### RAG Implementation
- **Recursive text chunking**: Splits by paragraph → sentence → word boundaries with configurable overlap
- **3072-dimensional embeddings**: Using Gemini `embedding-001` for high-quality semantic representations
- **Threshold-based retrieval**: Cosine similarity with 0.75 threshold, graceful fallback to top-3 results
- **Context injection**: Retrieved chunks are injected into LLM prompts for grounded, source-aware responses

### Architecture
- **Monorepo structure**: Frontend and backend in a single repository for easy deployment
- **Service layer pattern**: Each feature (YouTube, PDF, chunker, embeddings, RAG, flashcards, quiz) is an isolated service
- **Configurable settings**: All thresholds, model names, and limits are configurable via environment variables
- **Performance safeguards**: Max 20MB PDF, max 500 chunks/session, batched embedding generation

---

## 🛡️ Error Handling

| Layer | Strategy |
|-------|----------|
| **Custom Exceptions** | `ProcessingError`, `GenerationError`, `RetrievalError` with specific error codes |
| **Global Handler** | FastAPI exception handler catches unhandled errors with structured JSON responses |
| **Retry Logic** | LLM calls retry up to 3 times with exponential backoff for rate limits |
| **Input Validation** | Pydantic models validate all request/response data |
| **Frontend** | Error states with retry buttons, loading spinners, and user-friendly messages |
| **Graceful Degradation** | Missing transcripts fall back to available languages; low-similarity results use top-3 |

---

## 📁 Project Structure

```
learning-assistant/
├── frontend/                    # Next.js 14 application
│   ├── src/
│   │   ├── app/                 # Pages (landing, learn/[sessionId])
│   │   ├── components/          # FlashcardViewer, QuizInterface, ChatWindow
│   │   └── lib/                 # API client, utilities
│   └── package.json
├── backend/                     # FastAPI application
│   ├── main.py                  # App entry point, CORS, startup
│   ├── core/                    # Config, error handlers
│   ├── models/                  # Pydantic schemas, DB client
│   ├── routers/                 # API route handlers
│   ├── services/                # Business logic (YouTube, PDF, RAG, etc.)
│   ├── prompts/                 # LLM prompt templates
│   ├── schema.sql               # Supabase database schema
│   └── requirements.txt
├── .gitignore
└── README.md
```

---

## 📜 License

MIT
