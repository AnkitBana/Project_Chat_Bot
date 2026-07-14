"use client";
import { useTheme } from "@/lib/theme";
import { apiFetch } from "@/lib/api";
import { useEffect, useState, useCallback } from "react";

interface ModelData {
  available: Record<string, string[]>;
  configured: Record<string, boolean>;
  current_model: string;
  current_provider: string;
}

const PROVIDER_LABELS: Record<string, string> = {
  google: "🟢 Google",
  openai: "🔵 OpenAI",
  anthropic: "🟠 Anthropic",
  ica: "🟣 ICA",
};

export default function Sidebar({
  onModelSwitch,
  onNewChat,
  onSaveWord,
  showToast,
}: {
  onModelSwitch: (provider: string, model: string) => void;
  onNewChat: () => void;
  onSaveWord: () => void;
  showToast: (msg: string) => void;
}) {
  const { theme, toggle } = useTheme();
  const [models, setModels] = useState<ModelData | null>(null);
  const [selModel, setSelModel] = useState("");
  const [tools, setTools] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"chat" | "settings">("chat");
  const [settings, setSettings] = useState({
    name: "Nova", temperature: 0.3, max_tokens: 2048,
    system_message: "", verbose: false,
  });
  const [username, setUsername] = useState("U");

  useEffect(() => {
    setUsername(localStorage.getItem("nova_username") ?? "User");
  }, []);

  const loadModels = useCallback(async () => {
    try {
      const data = await apiFetch<ModelData>("/api/models");
      setModels(data);
      setSelModel(data.current_model);
    } catch {}
  }, []);

  useEffect(() => {
    loadModels();
    apiFetch<{ tools: string[] }>("/api/status").then((d) => setTools(d.tools)).catch(() => {});
    apiFetch<typeof settings>("/api/agent/settings").then(setSettings).catch(() => {});
  }, [loadModels]);

  async function applyModel(provider: string, model: string) {
    const prev = selModel;
    setSelModel(model);
    try {
      await apiFetch("/api/models/switch", {
        method: "POST",
        body: JSON.stringify({ provider, model }),
      });
      showToast(`✓ Now using ${model}`);
      onModelSwitch(provider, model);
    } catch (e: unknown) {
      setSelModel(prev);
      showToast("⚠ " + (e as Error).message);
    }
  }

  async function applySettings() {
    try {
      await apiFetch("/api/agent/settings", { method: "POST", body: JSON.stringify(settings) });
      showToast("✓ Settings saved");
    } catch (e: unknown) { showToast("Error: " + (e as Error).message); }
  }

  function logout() {
    localStorage.removeItem("nova_token");
    localStorage.removeItem("nova_username");
    window.location.href = "/login";
  }

  return (
    <aside style={{
      width: 260, minWidth: 260, background: "var(--sidebar)",
      display: "flex", flexDirection: "column", borderRight: "1px solid var(--border)",
      height: "100vh", overflow: "hidden",
    }}>
      {/* Top */}
      <div style={{ padding: "16px 12px 8px", display: "flex", gap: 8 }}>
        <button onClick={onNewChat} style={{
          flex: 1, display: "flex", alignItems: "center", gap: 8,
          padding: "9px 12px", borderRadius: 8, background: "transparent",
          border: "1px solid var(--border)", color: "var(--text)",
          fontSize: 13, fontWeight: 500, cursor: "pointer", fontFamily: "inherit",
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          New chat
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 4, padding: "0 8px 8px" }}>
        {(["chat", "settings"] as const).map((t) => (
          <button key={t} onClick={() => setActiveTab(t)} style={{
            flex: 1, padding: "7px 6px", borderRadius: 8,
            border: `1px solid ${activeTab === t ? "var(--border)" : "transparent"}`,
            background: activeTab === t ? "var(--surface)" : "transparent",
            color: activeTab === t ? "var(--text)" : "var(--muted)",
            fontSize: 12, fontWeight: 500, cursor: "pointer", fontFamily: "inherit",
          }}>
            {t === "settings" ? "⚙ Settings" : "Chat"}
          </button>
        ))}
      </div>

      {/* Chat Tab */}
      {activeTab === "chat" && (
        <div style={{ display: "flex", flexDirection: "column", flex: 1, overflow: "hidden", minHeight: 0 }}>
          {/* Model list */}
          <div style={{ padding: "0 8px 4px", display: "flex", flexDirection: "column", flex: 1, overflow: "hidden", minHeight: 0 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.6px", padding: "8px 4px 6px" }}>
              Model
            </div>
            <div style={{ overflowY: "auto", flex: 1, minHeight: 0 }}>
              {models && Object.entries(PROVIDER_LABELS).map(([prov, label]) => {
                const provModels = models.available[prov] ?? [];
                if (!provModels.length) return null;
                const hasKey = models.configured[prov] !== false;
                return (
                  <div key={prov}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.5px", padding: "6px 8px 3px", display: "flex", justifyContent: "space-between" }}>
                      <span>{label}</span>
                      {!hasKey && <span style={{ opacity: 0.6, fontSize: 11 }}>🔒 no key</span>}
                    </div>
                    {provModels.map((m) => {
                      const isActive = m === selModel;
                      const locked = !hasKey;
                      return (
                        <div key={m} onClick={() => locked ? showToast(`Add ${prov.toUpperCase()}_API_KEY to .env`) : applyModel(prov, m)}
                          style={{
                            padding: "7px 10px", borderRadius: 7, fontSize: 12, cursor: locked ? "not-allowed" : "pointer",
                            background: isActive ? "var(--accent2)" : "transparent",
                            color: isActive ? "#fff" : locked ? "var(--muted)" : "var(--muted)",
                            opacity: locked ? 0.45 : 1, display: "flex", alignItems: "center", gap: 6,
                            transition: "background 0.15s",
                          }}
                          onMouseEnter={(e) => { if (!locked && !isActive) { (e.currentTarget as HTMLDivElement).style.background = "var(--surface)"; (e.currentTarget as HTMLDivElement).style.color = "var(--text)"; } }}
                          onMouseLeave={(e) => { if (!locked && !isActive) { (e.currentTarget as HTMLDivElement).style.background = "transparent"; (e.currentTarget as HTMLDivElement).style.color = "var(--muted)"; } }}
                        >
                          {isActive ? "✓ " : locked ? "🔒 " : ""}{m}
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Tools */}
          <div style={{ padding: "0 8px", maxHeight: 110, overflowY: "auto", flexShrink: 0 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.6px", padding: "4px 6px 4px" }}>Tools</div>
            {tools.map((t) => (
              <div key={t} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 8px", fontSize: 13, color: "var(--muted)" }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14" /></svg>
                {t.replace(/_/g, " ")}
              </div>
            ))}
          </div>

          {/* Bottom */}
          <div style={{ padding: "8px 12px 16px", borderTop: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: 4, flexShrink: 0 }}>
            <div onClick={onSaveWord} style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontSize: 13, color: "var(--muted)" }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.background = "var(--surface)"; (e.currentTarget as HTMLDivElement).style.color = "var(--text)"; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.background = "transparent"; (e.currentTarget as HTMLDivElement).style.color = "var(--muted)"; }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>
              Save chat as Word
            </div>
            <button onClick={toggle} style={{
              display: "flex", alignItems: "center", gap: 8, padding: "8px 10px", borderRadius: 8,
              background: "transparent", border: "none", color: "var(--muted)", fontSize: 13,
              cursor: "pointer", fontFamily: "inherit", textAlign: "left", width: "100%",
            }}>
              <span style={{ fontSize: 15 }}>{theme === "dark" ? "☀️" : "🌙"}</span>
              {theme === "dark" ? "Light mode" : "Dark mode"}
            </button>
            <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", borderRadius: 8 }}>
              <div style={{
                width: 30, height: 30, borderRadius: "50%",
                background: "linear-gradient(135deg, var(--accent2), #3b82d4)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 13, fontWeight: 700, color: "#fff", flexShrink: 0,
              }}>{username[0]?.toUpperCase()}</div>
              <span style={{ fontSize: 13, fontWeight: 500, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{username}</span>
              <button onClick={logout} title="Sign out" style={{ background: "none", border: "none", color: "var(--muted)", cursor: "pointer", padding: 4, borderRadius: 5 }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === "settings" && (
        <div style={{ flex: 1, overflowY: "auto", padding: 8, display: "flex", flexDirection: "column", gap: 10 }}>
          {[
            { label: "Agent Name", id: "name", type: "text" as const },
          ].map(({ label, id }) => (
            <div key={id}>
              <div style={{ fontSize: 11, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: 4 }}>{label}</div>
              <input value={(settings as Record<string,unknown>)[id] as string} onChange={(e) => setSettings({ ...settings, [id]: e.target.value })}
                style={{ width: "100%", padding: "9px 12px", borderRadius: 9, background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text)", fontSize: 13, outline: "none", fontFamily: "inherit" }} />
            </div>
          ))}

          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: 4 }}>System Prompt</div>
            <textarea value={settings.system_message} onChange={(e) => setSettings({ ...settings, system_message: e.target.value })}
              placeholder="Leave blank for default…" rows={4}
              style={{ width: "100%", padding: "9px 12px", borderRadius: 9, background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text)", fontSize: 13, outline: "none", resize: "vertical", fontFamily: "inherit" }} />
          </div>

          <div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
              <span style={{ fontSize: 13, fontWeight: 500 }}>Temperature</span>
              <span style={{ fontSize: 13, color: "var(--accent)", fontWeight: 600 }}>{settings.temperature.toFixed(2)}</span>
            </div>
            <input type="range" min={0} max={2} step={0.05} value={settings.temperature}
              onChange={(e) => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
              style={{ width: "100%", accentColor: "var(--accent2)" }} />
          </div>

          <div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
              <span style={{ fontSize: 13, fontWeight: 500 }}>Max Tokens</span>
              <span style={{ fontSize: 13, color: "var(--accent)", fontWeight: 600 }}>{settings.max_tokens}</span>
            </div>
            <input type="range" min={256} max={8192} step={256} value={settings.max_tokens}
              onChange={(e) => setSettings({ ...settings, max_tokens: parseInt(e.target.value) })}
              style={{ width: "100%", accentColor: "var(--accent2)" }} />
          </div>

          <button onClick={applySettings} style={{
            width: "100%", padding: 11, borderRadius: 10, background: "var(--accent2)",
            border: "none", color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer",
          }}>Apply Settings</button>
        </div>
      )}
    </aside>
  );
}
