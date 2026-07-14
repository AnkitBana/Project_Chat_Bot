"use client";
import { useEffect, useRef, useCallback } from "react";
import { renderMarkdown } from "@/lib/markdown";

export interface Message {
  role: "user" | "assistant";
  content: string;
  tools?: string[];
}

interface Props {
  messages: Message[];
  streaming: boolean;
  streamContent: string;
  onCopy: (text: string) => void;
}

function UserBubble({ content }: { content: string }) {
  return (
    <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
      <div style={{
        background: "var(--user-bg)", borderRadius: "18px 18px 4px 18px",
        padding: "12px 16px", maxWidth: "80%", fontSize: 15, lineHeight: 1.6,
        whiteSpace: "pre-wrap", wordBreak: "break-word",
      }}>{content}</div>
    </div>
  );
}

function AssistantBubble({ content, tools, onCopy }: { content: string; tools?: string[]; onCopy: (t: string) => void }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    ref.current.querySelectorAll<HTMLButtonElement>(".copy-btn").forEach((btn) => {
      btn.onclick = () => {
        const pre = btn.closest(".code-block")?.querySelector("code");
        if (pre) { navigator.clipboard.writeText(pre.innerText); btn.textContent = "Copied!"; setTimeout(() => btn.textContent = "Copy", 2000); }
      };
    });
  }, [content]);

  return (
    <div style={{ display: "flex", gap: 14, alignItems: "flex-start", marginBottom: 8 }}>
      <div style={{
        width: 30, height: 30, borderRadius: "50%", flexShrink: 0,
        background: "linear-gradient(135deg, var(--accent2), #3b82d4)",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 13, fontWeight: 700, color: "#fff", marginTop: 2,
      }}>N</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        {tools?.map((t, i) => (
          <div key={i} className="tool-badge">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14" /></svg>
            {t}
          </div>
        ))}
        <div ref={ref} className="md" style={{ fontSize: 15, lineHeight: 1.75 }}
          dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }} />
        <div style={{ display: "flex", gap: 4, marginTop: 6, opacity: 0.6 }}>
          <button onClick={() => onCopy(content)} style={{
            background: "none", border: "none", color: "var(--muted)", cursor: "pointer",
            padding: "5px 8px", borderRadius: 6, fontSize: 12, display: "flex", alignItems: "center", gap: 5,
          }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
            Copy
          </button>
        </div>
      </div>
    </div>
  );
}

export default function MessageList({ messages, streaming, streamContent, onCopy }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const streamRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamContent]);

  const renderStream = useCallback(() => {
    if (!streamRef.current) return;
    streamRef.current.innerHTML = renderMarkdown(streamContent) + '<span class="cursor">▌</span>';
  }, [streamContent]);

  useEffect(() => { if (streaming) renderStream(); }, [streaming, renderStream]);

  if (messages.length === 0 && !streaming) return null;

  return (
    <div style={{ flex: 1, overflowY: "auto", padding: "24px 0 0" }}>
      {messages.map((m, i) => (
        <div key={i} style={{ width: "100%", maxWidth: 768, margin: "0 auto", padding: "4px 24px" }}>
          {m.role === "user"
            ? <UserBubble content={m.content} />
            : <AssistantBubble content={m.content} tools={m.tools} onCopy={onCopy} />}
        </div>
      ))}
      {streaming && (
        <div style={{ width: "100%", maxWidth: 768, margin: "0 auto", padding: "4px 24px" }}>
          <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
            <div style={{
              width: 30, height: 30, borderRadius: "50%", flexShrink: 0,
              background: "linear-gradient(135deg, var(--accent2), #3b82d4)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 13, fontWeight: 700, color: "#fff",
            }}>N</div>
            <div ref={streamRef} className="md" style={{ flex: 1, minWidth: 0, fontSize: 15, lineHeight: 1.75 }} />
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
