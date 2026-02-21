"use client";

import { useState, useRef, DragEvent } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [mode, setMode] = useState<"youtube" | "pdf">("youtube");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async () => {
    setError("");
    setLoading(true);

    try {
      let result;
      if (mode === "youtube") {
        if (!url.trim()) {
          setError("Please enter a YouTube URL");
          setLoading(false);
          return;
        }
        result = await api.processVideo(url);
      } else {
        if (!file) {
          setError("Please select a PDF file");
          setLoading(false);
          return;
        }
        result = await api.processPdf(file);
      }
      router.push(`/learn/${result.session_id}?title=${encodeURIComponent(result.title)}`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Something went wrong";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.type === "application/pdf") {
      setFile(dropped);
    } else {
      setError("Please drop a PDF file");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Background glow effects */}
      <div
        className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full opacity-20 blur-3xl pointer-events-none"
        style={{ background: "var(--accent-blue)" }}
      />
      <div
        className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full opacity-15 blur-3xl pointer-events-none"
        style={{ background: "var(--accent-purple)" }}
      />

      {/* Hero */}
      <div className="text-center mb-12 animate-fade-in relative z-10">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6" style={{ background: "rgba(99, 102, 241, 0.1)", border: "1px solid rgba(99, 102, 241, 0.2)" }}>
          <span style={{ fontSize: "0.85rem", color: "var(--accent-blue)" }}>✨ AI-Powered Learning</span>
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold mb-4 tracking-tight">
          <span className="gradient-text">Learn Smarter</span>
          <br />
          <span style={{ color: "var(--text-primary)" }}>Not Harder</span>
        </h1>
        <p className="text-lg md:text-xl max-w-2xl mx-auto" style={{ color: "var(--text-secondary)" }}>
          Transform any YouTube video or PDF into interactive flashcards,
          quizzes, and an AI study companion — in seconds.
        </p>
      </div>

      {/* Input Card */}
      <div className="glass-card w-full max-w-2xl p-8 relative z-10 animate-fade-in" style={{ animationDelay: "0.2s" }}>
        {/* Mode Toggle */}
        <div className="flex gap-2 mb-6 p-1 rounded-xl" style={{ background: "var(--bg-secondary)" }}>
          <button
            onClick={() => { setMode("youtube"); setError(""); }}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all text-sm ${mode === "youtube"
                ? "text-white shadow-lg"
                : ""
              }`}
            style={
              mode === "youtube"
                ? { background: "var(--gradient-primary)" }
                : { color: "var(--text-secondary)" }
            }
          >
            🎬 YouTube Video
          </button>
          <button
            onClick={() => { setMode("pdf"); setError(""); }}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all text-sm ${mode === "pdf"
                ? "text-white shadow-lg"
                : ""
              }`}
            style={
              mode === "pdf"
                ? { background: "var(--gradient-primary)" }
                : { color: "var(--text-secondary)" }
            }
          >
            📄 PDF Upload
          </button>
        </div>

        {/* Input Area */}
        {mode === "youtube" ? (
          <div className="mb-6">
            <input
              type="text"
              placeholder="Paste a YouTube URL (e.g. https://youtube.com/watch?v=...)"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-5 py-4 rounded-xl text-base outline-none transition-all"
              style={{
                background: "var(--bg-secondary)",
                border: "1px solid var(--border-glass)",
                color: "var(--text-primary)",
              }}
              onFocus={(e) => (e.target.style.borderColor = "var(--accent-blue)")}
              onBlur={(e) => (e.target.style.borderColor = "var(--border-glass)")}
            />
          </div>
        ) : (
          <div
            className={`drop-zone mb-6 ${dragging ? "dragging" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) setFile(f);
              }}
            />
            {file ? (
              <div>
                <div className="text-3xl mb-2">📄</div>
                <p className="font-medium" style={{ color: "var(--text-primary)" }}>
                  {file.name}
                </p>
                <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
                  {(file.size / 1024 / 1024).toFixed(1)} MB
                </p>
              </div>
            ) : (
              <div>
                <div className="text-4xl mb-3">📁</div>
                <p style={{ color: "var(--text-secondary)" }}>
                  Drag & drop a PDF here, or click to browse
                </p>
                <p className="text-sm mt-2" style={{ color: "var(--text-muted)" }}>
                  Max 20MB
                </p>
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            className="mb-4 px-4 py-3 rounded-xl text-sm"
            style={{
              background: "rgba(244, 63, 94, 0.1)",
              border: "1px solid rgba(244, 63, 94, 0.2)",
              color: "var(--accent-rose)",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn-glow w-full flex items-center justify-center gap-3"
        >
          {loading ? (
            <>
              <div className="spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
              Processing...
            </>
          ) : (
            <>🚀 Start Learning</>
          )}
        </button>
      </div>

      {/* Feature cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mt-16 relative z-10">
        {[
          { icon: "🃏", title: "Smart Flashcards", desc: "AI-generated cards with difficulty levels" },
          { icon: "🧠", title: "Interactive Quizzes", desc: "MCQs with instant feedback & explanations" },
          { icon: "💬", title: "AI Study Chat", desc: "Ask questions about your content with RAG" },
        ].map((f, i) => (
          <div
            key={i}
            className="glass-card p-6 text-center animate-fade-in"
            style={{ animationDelay: `${0.3 + i * 0.1}s` }}
          >
            <div className="text-4xl mb-4">{f.icon}</div>
            <h3 className="font-semibold text-lg mb-2" style={{ color: "var(--text-primary)" }}>
              {f.title}
            </h3>
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              {f.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
