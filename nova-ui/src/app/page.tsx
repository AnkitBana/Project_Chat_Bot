"use client";
import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import MessageList, { Message } from "@/components/MessageList";
import InputBox from "@/components/InputBox";
import Toast, { useToast } from "@/components/Toast";
import { streamChat, apiFetch, BASE } from "@/lib/api";

const SUGGESTIONS = [
  { icon: "🔍", text: "Search latest AI news", sub: "Web search tool" },
  { icon: "🧮", text: "What is 123 × 456?", sub: "Calculator tool" },
  { icon: "💻", text: "Write a C# Hello World program", sub: "Code generation" },
  { icon: "📅", text: "What's today's date and time?", sub: "System tool" },
];

export default function ChatPage() {
  const router = useRouter();
  const { msg: toastMsg, visible: toastVisible, showToast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState("");
  const [loading, setLoading] = useState(false);

  // Auth guard
  useEffect(() => {
    if (!localStorage.getItem("nova_token")) router.replace("/login");
  }, [router]);

  const send = useCallback(async (text: string) => {
    if (loading) return;
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);
    setStreaming(true);
    setStreamContent("");

    let raw = "";
    const tools: string[] = [];

    streamChat(
      text,
      (token) => { raw += token; setStreamContent(raw); },
      (tool)  => { tools.push(tool); },
      (turns) => {
        setStreaming(false);
        setLoading(false);
        setMessages((prev) => [...prev, { role: "assistant", content: raw, tools: [...tools] }]);
        setStreamContent("");
        void turns;
      },
      (err) => {
        setStreaming(false);
        setLoading(false);
        setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${err}` }]);
        setStreamContent("");
      },
    );
  }, [loading]);

  async function newChat() {
    try { await apiFetch("/api/clear", { method: "POST" }); } catch {}
    setMessages([]);
    setStreamContent("");
    showToast("New conversation started");
  }

  async function saveWord() {
    try {
      const res = await fetch(`${BASE}/api/export/docx`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("nova_token")}` },
        body: JSON.stringify({ title: "Nova AI Chat", messages }),
      });
      if (!res.ok) throw new Error("Export failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a"); a.href = url; a.download = "nova-chat.docx"; a.click();
      URL.revokeObjectURL(url);
    } catch (e: unknown) { showToast("Export failed: " + (e as Error).message); }
  }

  const showWelcome = messages.length === 0 && !streaming;

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
      <Sidebar
        onModelSwitch={(p, m) => showToast(`Switched to ${m} (${p}). Memory preserved.`)}
        onNewChat={newChat}
        onSaveWord={saveWord}
        showToast={showToast}
      />

      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", position: "relative" }}>
        {showWelcome ? (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px 24px", textAlign: "center", gap: 16 }}>
            <div style={{
              width: 56, height: 56, borderRadius: 16,
              background: "linear-gradient(135deg, var(--accent2), #3b82d4)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 26, fontWeight: 800, color: "#fff",
            }}>N</div>
            <h1 style={{ fontSize: 26, fontWeight: 700 }}>What can I help with?</h1>
            <p style={{ color: "var(--muted)", fontSize: 15, maxWidth: 420 }}>
              Nova is your AI agent — it can search the web, read files, run calculations, call APIs, and more.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 8, width: "100%", maxWidth: 520 }}>
              {SUGGESTIONS.map((s) => (
                <div key={s.text} onClick={() => send(s.text)} style={{
                  background: "var(--surface)", border: "1px solid var(--border)",
                  borderRadius: 12, padding: "14px 16px", cursor: "pointer", textAlign: "left", fontSize: 13,
                  color: "var(--text)", lineHeight: 1.4, transition: "border-color 0.15s",
                }}
                  onMouseEnter={(e) => (e.currentTarget as HTMLDivElement).style.borderColor = "var(--accent2)"}
                  onMouseLeave={(e) => (e.currentTarget as HTMLDivElement).style.borderColor = "var(--border)"}
                >
                  <span style={{ fontSize: 18, marginBottom: 6, display: "block" }}>{s.icon}</span>
                  <div style={{ fontWeight: 500 }}>{s.text}</div>
                  <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 2 }}>{s.sub}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <MessageList
            messages={messages}
            streaming={streaming}
            streamContent={streamContent}
            onCopy={(t) => { navigator.clipboard.writeText(t); showToast("Copied!"); }}
          />
        )}

        {/* Progress bar */}
        <div className="progress-bar">
          {loading && <div className="progress-fill" />}
        </div>

        <InputBox onSend={send} disabled={loading} />
      </main>

      <Toast message={toastMsg} visible={toastVisible} />
    </div>
  );
}
