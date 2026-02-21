"use client";

import { useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import FlashcardViewer from "@/components/FlashcardViewer";
import QuizInterface from "@/components/QuizInterface";
import ChatWindow from "@/components/ChatWindow";
import Link from "next/link";

type Tab = "flashcards" | "quiz" | "chat";

export default function LearnPage() {
    const params = useParams();
    const searchParams = useSearchParams();
    const sessionId = params.sessionId as string;
    const title = searchParams.get("title") || "Learning Session";
    const [activeTab, setActiveTab] = useState<Tab>("flashcards");

    const tabs: { id: Tab; label: string; icon: string }[] = [
        { id: "flashcards", label: "Flashcards", icon: "🃏" },
        { id: "quiz", label: "Quiz", icon: "🧠" },
        { id: "chat", label: "AI Chat", icon: "💬" },
    ];

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header
                className="sticky top-0 z-50 px-6 py-4 flex items-center justify-between"
                style={{
                    background: "rgba(10, 14, 26, 0.8)",
                    backdropFilter: "blur(12px)",
                    borderBottom: "1px solid var(--border-glass)",
                }}
            >
                <div className="flex items-center gap-4">
                    <Link
                        href="/"
                        className="text-sm font-medium px-3 py-1.5 rounded-lg transition-all"
                        style={{
                            color: "var(--text-secondary)",
                            background: "rgba(99, 102, 241, 0.08)",
                        }}
                    >
                        ← Back
                    </Link>
                    <div>
                        <h1 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
                            {decodeURIComponent(title)}
                        </h1>
                        <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                            Session: {sessionId.slice(0, 8)}...
                        </p>
                    </div>
                </div>

                {/* Tabs */}
                <nav className="flex gap-2">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
                        >
                            {tab.icon} {tab.label}
                        </button>
                    ))}
                </nav>
            </header>

            {/* Content */}
            <main className="flex-1 p-6 max-w-6xl mx-auto w-full">
                {activeTab === "flashcards" && <FlashcardViewer sessionId={sessionId} />}
                {activeTab === "quiz" && <QuizInterface sessionId={sessionId} />}
                {activeTab === "chat" && <ChatWindow sessionId={sessionId} />}
            </main>
        </div>
    );
}
