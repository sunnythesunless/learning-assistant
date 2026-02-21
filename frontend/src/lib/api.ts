const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ProcessResponse {
    session_id: string;
    title: string;
    chunk_count: number;
    source_type: string;
}

export interface Flashcard {
    front: string;
    back: string;
    difficulty: "easy" | "medium" | "hard";
}

export interface FlashcardResponse {
    session_id: string;
    flashcards: Flashcard[];
    count: number;
}

export interface QuizOption {
    label: string;
    text: string;
}

export interface QuizQuestion {
    question: string;
    options: QuizOption[];
    correct_answer: string;
    explanation: string;
}

export interface QuizResponse {
    session_id: string;
    questions: QuizQuestion[];
    count: number;
}

export interface ChatMessage {
    role: "user" | "assistant";
    content: string;
}

class ApiClient {
    private baseUrl: string;

    constructor() {
        this.baseUrl = API_BASE;
    }

    async processVideo(url: string): Promise<ProcessResponse> {
        const res = await fetch(`${this.baseUrl}/process-video`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });
        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: "Failed to process video" }));
            throw new Error(error.message || "Failed to process video");
        }
        return res.json();
    }

    async processPdf(file: File): Promise<ProcessResponse> {
        const formData = new FormData();
        formData.append("file", file);
        const res = await fetch(`${this.baseUrl}/process-pdf`, {
            method: "POST",
            body: formData,
        });
        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: "Failed to process PDF" }));
            throw new Error(error.message || "Failed to process PDF");
        }
        return res.json();
    }

    async generateFlashcards(sessionId: string): Promise<FlashcardResponse> {
        const res = await fetch(`${this.baseUrl}/generate-flashcards`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId }),
        });
        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: "Failed to generate flashcards" }));
            throw new Error(error.message || "Failed to generate flashcards");
        }
        return res.json();
    }

    async generateQuiz(sessionId: string): Promise<QuizResponse> {
        const res = await fetch(`${this.baseUrl}/generate-quiz`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId }),
        });
        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: "Failed to generate quiz" }));
            throw new Error(error.message || "Failed to generate quiz");
        }
        return res.json();
    }

    async *streamChat(sessionId: string, message: string): AsyncGenerator<string> {
        const res = await fetch(`${this.baseUrl}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, message }),
        });

        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: "Chat failed" }));
            throw new Error(error.message || "Chat failed");
        }

        const reader = res.body?.getReader();
        if (!reader) throw new Error("No response body");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const data = line.slice(6).trim();
                    if (data === "[DONE]") return;
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.content) yield parsed.content;
                    } catch {
                        // Skip malformed SSE lines
                    }
                }
            }
        }
    }
}

export const api = new ApiClient();
