"use client";

import { useState, useEffect } from "react";
import { api, Flashcard } from "@/lib/api";

interface Props {
    sessionId: string;
}

export default function FlashcardViewer({ sessionId }: Props) {
    const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [currentIndex, setCurrentIndex] = useState(0);
    const [flipped, setFlipped] = useState(false);
    const [loadingMsg, setLoadingMsg] = useState("Generating flashcards...");

    useEffect(() => {
        loadFlashcards();
    }, [sessionId]);

    useEffect(() => {
        if (!loading) return;
        const messages = [
            "Generating flashcards...",
            "Reading your content...",
            "Creating cards with AI...",
            "This can take up to 60s on free tier...",
            "Almost done...",
        ];
        let i = 0;
        const interval = setInterval(() => {
            i = (i + 1) % messages.length;
            setLoadingMsg(messages[i]);
        }, 8000);
        return () => clearInterval(interval);
    }, [loading]);

    const loadFlashcards = async () => {
        try {
            setLoading(true);
            const res = await api.generateFlashcards(sessionId);
            setFlashcards(res.flashcards);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Failed to load flashcards");
        } finally {
            setLoading(false);
        }
    };

    const goToCard = (index: number) => {
        setFlipped(false);
        setTimeout(() => setCurrentIndex(index), 100);
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <div className="spinner-lg mb-6" />
                <p className="text-lg font-medium" style={{ color: "var(--text-secondary)" }}>
                    {loadingMsg}
                </p>
                <p className="text-sm mt-2" style={{ color: "var(--text-muted)" }}>
                    AI is analyzing your content and crafting study material
                </p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-20">
                <p className="text-lg" style={{ color: "var(--accent-rose)" }}>
                    ⚠️ {error}
                </p>
                <button onClick={loadFlashcards} className="btn-glow mt-4">
                    Retry
                </button>
            </div>
        );
    }

    if (flashcards.length === 0) return null;

    const card = flashcards[currentIndex];
    const difficultyColors: Record<string, string> = {
        easy: "badge-easy",
        medium: "badge-medium",
        hard: "badge-hard",
    };

    return (
        <div className="animate-fade-in">
            {/* Progress */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <span className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
                        Card {currentIndex + 1} of {flashcards.length}
                    </span>
                    <span className={`badge ${difficultyColors[card.difficulty]}`}>
                        {card.difficulty}
                    </span>
                </div>
                <div className="flex gap-1">
                    {flashcards.map((_, i) => (
                        <button
                            key={i}
                            onClick={() => goToCard(i)}
                            className="w-2.5 h-2.5 rounded-full transition-all"
                            style={{
                                background:
                                    i === currentIndex
                                        ? "var(--accent-blue)"
                                        : "var(--text-muted)",
                                opacity: i === currentIndex ? 1 : 0.3,
                            }}
                        />
                    ))}
                </div>
            </div>

            {/* Flashcard */}
            <div
                className={`flip-card mx-auto ${flipped ? "flipped" : ""}`}
                style={{ width: "100%", maxWidth: 600, height: 350 }}
                onClick={() => setFlipped(!flipped)}
            >
                <div className="flip-card-inner">
                    {/* Front */}
                    <div
                        className="flip-card-front"
                        style={{
                            background: "var(--bg-card)",
                            border: "1px solid var(--border-glass)",
                        }}
                    >
                        <div className="text-center">
                            <p className="text-xs uppercase tracking-widest mb-4" style={{ color: "var(--text-muted)" }}>
                                Question
                            </p>
                            <p className="text-xl font-medium leading-relaxed" style={{ color: "var(--text-primary)" }}>
                                {card.front}
                            </p>
                            <p className="text-xs mt-6" style={{ color: "var(--text-muted)" }}>
                                Click to flip
                            </p>
                        </div>
                    </div>

                    {/* Back */}
                    <div
                        className="flip-card-back"
                        style={{
                            background: "linear-gradient(145deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.08))",
                            border: "1px solid rgba(99, 102, 241, 0.25)",
                        }}
                    >
                        <div className="text-center">
                            <p className="text-xs uppercase tracking-widest mb-4" style={{ color: "var(--accent-blue)" }}>
                                Answer
                            </p>
                            <p className="text-lg leading-relaxed" style={{ color: "var(--text-primary)" }}>
                                {card.back}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-center gap-4 mt-8">
                <button
                    onClick={() => goToCard(Math.max(0, currentIndex - 1))}
                    disabled={currentIndex === 0}
                    className="px-6 py-3 rounded-xl font-medium transition-all"
                    style={{
                        background: "var(--bg-card)",
                        border: "1px solid var(--border-glass)",
                        color: currentIndex === 0 ? "var(--text-muted)" : "var(--text-primary)",
                        opacity: currentIndex === 0 ? 0.5 : 1,
                        cursor: currentIndex === 0 ? "not-allowed" : "pointer",
                    }}
                >
                    ← Previous
                </button>
                <button
                    onClick={() => setFlipped(!flipped)}
                    className="px-6 py-3 rounded-xl font-medium transition-all"
                    style={{
                        background: "rgba(99, 102, 241, 0.1)",
                        border: "1px solid rgba(99, 102, 241, 0.25)",
                        color: "var(--accent-blue)",
                    }}
                >
                    {flipped ? "Show Question" : "Show Answer"}
                </button>
                <button
                    onClick={() => goToCard(Math.min(flashcards.length - 1, currentIndex + 1))}
                    disabled={currentIndex === flashcards.length - 1}
                    className="px-6 py-3 rounded-xl font-medium transition-all"
                    style={{
                        background: "var(--bg-card)",
                        border: "1px solid var(--border-glass)",
                        color: currentIndex === flashcards.length - 1 ? "var(--text-muted)" : "var(--text-primary)",
                        opacity: currentIndex === flashcards.length - 1 ? 0.5 : 1,
                        cursor: currentIndex === flashcards.length - 1 ? "not-allowed" : "pointer",
                    }}
                >
                    Next →
                </button>
            </div>
        </div>
    );
}
