"use client";

import { useState, useEffect } from "react";
import { api, QuizQuestion } from "@/lib/api";

interface Props {
    sessionId: string;
}

export default function QuizInterface({ sessionId }: Props) {
    const [questions, setQuestions] = useState<QuizQuestion[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
    const [submitted, setSubmitted] = useState(false);
    const [score, setScore] = useState(0);
    const [finished, setFinished] = useState(false);
    const [answers, setAnswers] = useState<(string | null)[]>([]);

    useEffect(() => {
        loadQuiz();
    }, [sessionId]);

    const loadQuiz = async () => {
        try {
            setLoading(true);
            const res = await api.generateQuiz(sessionId);
            setQuestions(res.questions);
            setAnswers(new Array(res.questions.length).fill(null));
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Failed to load quiz");
        } finally {
            setLoading(false);
        }
    };

    const handleSelect = (label: string) => {
        if (submitted) return;
        setSelectedAnswer(label);
    };

    const handleSubmit = () => {
        if (!selectedAnswer) return;
        setSubmitted(true);
        const newAnswers = [...answers];
        newAnswers[currentIndex] = selectedAnswer;
        setAnswers(newAnswers);
        if (selectedAnswer === questions[currentIndex].correct_answer) {
            setScore((s) => s + 1);
        }
    };

    const handleNext = () => {
        if (currentIndex === questions.length - 1) {
            setFinished(true);
        } else {
            setCurrentIndex((i) => i + 1);
            setSelectedAnswer(null);
            setSubmitted(false);
        }
    };

    const handleRestart = () => {
        setCurrentIndex(0);
        setSelectedAnswer(null);
        setSubmitted(false);
        setScore(0);
        setFinished(false);
        setAnswers(new Array(questions.length).fill(null));
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <div className="spinner-lg mb-6" />
                <p className="text-lg font-medium" style={{ color: "var(--text-secondary)" }}>
                    Generating quiz questions...
                </p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-20">
                <p className="text-lg" style={{ color: "var(--accent-rose)" }}>⚠️ {error}</p>
                <button onClick={loadQuiz} className="btn-glow mt-4">Retry</button>
            </div>
        );
    }

    if (questions.length === 0) return null;

    // Score screen
    if (finished) {
        const pct = Math.round((score / questions.length) * 100);
        const emoji = pct >= 80 ? "🏆" : pct >= 60 ? "👍" : pct >= 40 ? "📚" : "💪";

        return (
            <div className="animate-fade-in text-center py-12">
                <div className="text-6xl mb-6">{emoji}</div>
                <h2 className="text-3xl font-bold mb-2" style={{ color: "var(--text-primary)" }}>
                    Quiz Complete!
                </h2>
                <p className="text-xl mb-8" style={{ color: "var(--text-secondary)" }}>
                    You scored{" "}
                    <span className="gradient-text font-bold">
                        {score}/{questions.length}
                    </span>{" "}
                    ({pct}%)
                </p>

                {/* Answer review */}
                <div className="glass-card p-6 max-w-2xl mx-auto text-left mb-8">
                    <h3 className="font-semibold mb-4" style={{ color: "var(--text-primary)" }}>
                        Review Answers
                    </h3>
                    {questions.map((q, i) => (
                        <div
                            key={i}
                            className="flex items-start gap-3 py-3"
                            style={{ borderBottom: i < questions.length - 1 ? "1px solid var(--border-glass)" : "none" }}
                        >
                            <span
                                className="text-lg mt-0.5"
                                style={{ minWidth: 24 }}
                            >
                                {answers[i] === q.correct_answer ? "✅" : "❌"}
                            </span>
                            <div>
                                <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                                    {q.question}
                                </p>
                                <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                                    Correct: {q.correct_answer} — {q.explanation}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                <button onClick={handleRestart} className="btn-glow">
                    🔄 Try Again
                </button>
            </div>
        );
    }

    const question = questions[currentIndex];

    return (
        <div className="animate-fade-in max-w-2xl mx-auto">
            {/* Progress bar */}
            <div className="mb-8">
                <div className="flex justify-between mb-2">
                    <span className="text-sm" style={{ color: "var(--text-secondary)" }}>
                        Question {currentIndex + 1} of {questions.length}
                    </span>
                    <span className="text-sm" style={{ color: "var(--accent-blue)" }}>
                        Score: {score}
                    </span>
                </div>
                <div
                    className="h-1.5 rounded-full overflow-hidden"
                    style={{ background: "var(--bg-secondary)" }}
                >
                    <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                            width: `${((currentIndex + 1) / questions.length) * 100}%`,
                            background: "var(--gradient-primary)",
                        }}
                    />
                </div>
            </div>

            {/* Question */}
            <div className="glass-card p-8 mb-6">
                <p className="text-xl font-medium leading-relaxed" style={{ color: "var(--text-primary)" }}>
                    {question.question}
                </p>
            </div>

            {/* Options */}
            <div className="space-y-3 mb-6">
                {question.options.map((opt) => {
                    let className = "quiz-option";
                    if (selectedAnswer === opt.label && !submitted) className += " selected";
                    if (submitted) {
                        if (opt.label === question.correct_answer) className += " correct";
                        else if (opt.label === selectedAnswer) className += " incorrect";
                    }

                    return (
                        <button
                            key={opt.label}
                            onClick={() => handleSelect(opt.label)}
                            className={className}
                            disabled={submitted}
                        >
                            <span
                                className="inline-flex items-center justify-center w-7 h-7 rounded-full text-sm font-bold mr-3"
                                style={{
                                    background: "rgba(99, 102, 241, 0.1)",
                                    color: "var(--accent-blue)",
                                }}
                            >
                                {opt.label}
                            </span>
                            {opt.text}
                        </button>
                    );
                })}
            </div>

            {/* Explanation */}
            {submitted && (
                <div
                    className="mb-6 p-4 rounded-xl animate-fade-in"
                    style={{
                        background:
                            selectedAnswer === question.correct_answer
                                ? "rgba(16, 185, 129, 0.08)"
                                : "rgba(244, 63, 94, 0.08)",
                        border: `1px solid ${selectedAnswer === question.correct_answer
                                ? "rgba(16, 185, 129, 0.2)"
                                : "rgba(244, 63, 94, 0.2)"
                            }`,
                    }}
                >
                    <p
                        className="font-medium mb-1"
                        style={{
                            color:
                                selectedAnswer === question.correct_answer
                                    ? "var(--accent-emerald)"
                                    : "var(--accent-rose)",
                        }}
                    >
                        {selectedAnswer === question.correct_answer ? "✅ Correct!" : "❌ Incorrect"}
                    </p>
                    <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                        {question.explanation}
                    </p>
                </div>
            )}

            {/* Action */}
            <div className="flex justify-end">
                {!submitted ? (
                    <button
                        onClick={handleSubmit}
                        disabled={!selectedAnswer}
                        className="btn-glow"
                    >
                        Submit Answer
                    </button>
                ) : (
                    <button onClick={handleNext} className="btn-glow">
                        {currentIndex === questions.length - 1 ? "See Results" : "Next Question →"}
                    </button>
                )}
            </div>
        </div>
    );
}
