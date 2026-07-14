"use client";
import { useRef, useState, useEffect } from "react";

interface Props {
  onSend: (msg: string) => void;
  disabled: boolean;
}

export default function InputBox({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const textRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textRef.current) {
      textRef.current.style.height = "auto";
      textRef.current.style.height = Math.min(textRef.current.scrollHeight, 180) + "px";
    }
  }, [value]);

  function send() {
    const msg = value.trim();
    if (!msg || disabled) return;
    setValue("");
    if (textRef.current) textRef.current.style.height = "auto";
    onSend(msg);
  }

  return (
    <div style={{ padding: "12px 24px 20px", background: "var(--bg)" }}>
      <div style={{ maxWidth: 768, margin: "0 auto" }}>
        <div style={{
          display: "flex", alignItems: "flex-end", gap: 8,
          background: "var(--surface)", border: "1px solid var(--border)",
          borderRadius: 16, padding: "10px 10px 10px 14px",
          transition: "border-color 0.2s",
        }}
          onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(124,92,216,0.6)")}
          onBlur={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
        >
          <textarea
            ref={textRef}
            value={value}
            rows={1}
            placeholder="Ask anything…"
            maxLength={8000}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
            style={{
              flex: 1, background: "transparent", border: "none", outline: "none",
              color: "var(--text)", fontSize: 15, resize: "none",
              maxHeight: 180, overflow: "auto", lineHeight: 1.6,
              fontFamily: "inherit", padding: "2px 0",
            }}
          />
          <button
            onClick={send}
            disabled={disabled || !value.trim()}
            style={{
              width: 34, height: 34, borderRadius: 8, flexShrink: 0,
              background: disabled || !value.trim() ? "var(--border)" : "var(--accent2)",
              border: "none", cursor: disabled || !value.trim() ? "not-allowed" : "pointer",
              color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
              opacity: disabled || !value.trim() ? 0.3 : 1, transition: "opacity 0.2s",
            }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="12" y1="19" x2="12" y2="5" /><polyline points="5 12 12 5 19 12" />
            </svg>
          </button>
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, color: "var(--muted)", gap: 6, marginTop: 6 }}>
          <span>Enter to send</span><span>·</span><span>Shift+Enter for new line</span>
        </div>
      </div>
    </div>
  );
}
