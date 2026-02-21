"use client";

import { useState, useRef, useEffect } from "react";
import { api } from "@/lib/api";

interface Message {
    role: "user" | "assistant";
    content: string;
}

// Strip markdown formatting symbols from text
function cleanText(text: string): string {
    return text
        .replace(/\*{2,3}(.*?)\*{2,3}/g, "$1") // **bold** or ***bold***
        .replace(/\*(.*?)\*/g, "$1")             // *italic*
        .replace(/^#{1,6}\s+/gm, "")            // ## headings
        .replace(/^[-*]\s+/gm, "• ")            // bullet points → clean dots
        .replace(/`([^`]+)`/g, "$1");            // `code`
}

interface Props {
    sessionId: string;
}

export default function ChatWindow({ sessionId }: Props) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [streaming, setStreaming] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async () => {
        const message = input.trim();
        if (!message || streaming) return;

        setInput("");
        setMessages((prev) => [...prev, { role: "user", content: message }]);
        setStreaming(true);

        // Add empty assistant message for streaming
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        try {
            let fullResponse = "";
            for await (const chunk of api.streamChat(sessionId, message)) {
                fullResponse += chunk;
                setMessages((prev) => {
                    const updated = [...prev];
                    updated[updated.length - 1] = {
                        role: "assistant",
                        content: fullResponse,
                    };
                    return updated;
                });
            }
        } catch (err: unknown) {
            const errMsg = err instanceof Error ? err.message : "Chat failed";
            setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                    role: "assistant",
                    content: `⚠️ ${errMsg}`,
                };
                return updated;
            });
        } finally {
            setStreaming(false);
            inputRef.current?.focus();
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div
            className="flex flex-col animate-fade-in"
            style={{ height: "calc(100vh - 160px)" }}
        >
            {/* Messages area */}
            <div className="flex-1 overflow-y-auto pr-2 space-y-4 mb-4">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <div className="text-5xl mb-4 animate-float">💬</div>
                        <h3
                            className="text-xl font-semibold mb-2"
                            style={{ color: "var(--text-primary)" }}
                        >
                            AI Study Chat
                        </h3>
                        <p
                            className="max-w-md text-sm"
                            style={{ color: "var(--text-secondary)" }}
                        >
                            Ask anything about the content you've processed. I'll use
                            RAG to find relevant context and give you accurate answers.
                        </p>
                        <div className="flex flex-wrap gap-2 mt-6 justify-center">
                            {[
                                "Summarize the main points",
                                "Explain the key concepts",
                                "What are the practical applications?",
                            ].map((suggestion) => (
                                <button
                                    key={suggestion}
                                    onClick={() => {
                                        setInput(suggestion);
                                        inputRef.current?.focus();
                                    }}
                                    className="px-4 py-2 rounded-xl text-sm transition-all"
                                    style={{
                                        background: "rgba(99, 102, 241, 0.08)",
                                        border: "1px solid rgba(99, 102, 241, 0.15)",
                                        color: "var(--text-secondary)",
                                        cursor: "pointer",
                                    }}
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div
                        key={i}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                        <div className={`chat-bubble ${msg.role}`}>
                            {msg.role === "assistant" && msg.content === "" ? (
                                <div className="flex items-center gap-2">
                                    <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                                    <span className="text-sm" style={{ color: "var(--text-muted)" }}>
                                        Thinking...
                                    </span>
                                </div>
                            ) : (
                                <div style={{ whiteSpace: "pre-wrap" }}>
                                    {msg.role === "assistant" ? cleanText(msg.content) : msg.content}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input area */}
            <div
                className="flex gap-3 p-3 rounded-2xl"
                style={{
                    background: "var(--bg-card)",
                    border: "1px solid var(--border-glass)",
                }}
            >
                <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a question about the content..."
                    disabled={streaming}
                    className="flex-1 px-4 py-3 rounded-xl outline-none text-sm"
                    style={{
                        background: "var(--bg-secondary)",
                        color: "var(--text-primary)",
                        border: "none",
                    }}
                />
                <button
                    onClick={handleSend}
                    disabled={!input.trim() || streaming}
                    className="px-5 py-3 rounded-xl font-medium text-sm transition-all"
                    style={{
                        background: input.trim() && !streaming ? "var(--gradient-primary)" : "var(--bg-secondary)",
                        color: input.trim() && !streaming ? "white" : "var(--text-muted)",
                        cursor: input.trim() && !streaming ? "pointer" : "not-allowed",
                    }}
                >
                    {streaming ? "..." : "Send ↑"}
                </button>
            </div>
        </div>
    );
}
