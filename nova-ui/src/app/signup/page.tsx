"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { signup } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState({ username: "", password: "", email: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const data = await signup(form.username, form.password, form.email || undefined);
      localStorage.setItem("nova_token", data.access_token);
      localStorage.setItem("nova_username", data.username);
      router.replace("/");
    } catch (err: unknown) {
      setError((err as Error).message);
    } finally { setLoading(false); }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)" }}>
      <div style={{ width: "100%", maxWidth: 400, padding: "0 24px" }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            width: 52, height: 52, borderRadius: 14, margin: "0 auto 16px",
            background: "linear-gradient(135deg, var(--accent2), #3b82d4)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 24, fontWeight: 800, color: "#fff",
          }}>N</div>
          <h1 style={{ fontSize: 22, fontWeight: 700 }}>Create account</h1>
          <p style={{ color: "var(--muted)", fontSize: 14, marginTop: 4 }}>Get started with Nova AI</p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {[
            { field: "username", label: "Username", type: "text", required: true },
            { field: "email",    label: "Email (optional)", type: "email", required: false },
            { field: "password", label: "Password", type: "password", required: true },
          ].map(({ field, label, type, required }) => (
            <div key={field}>
              <label style={{ fontSize: 13, fontWeight: 500, display: "block", marginBottom: 6 }}>{label}</label>
              <input
                type={type}
                value={(form as Record<string, string>)[field]}
                onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                required={required}
                style={{
                  width: "100%", padding: "10px 14px", borderRadius: 10,
                  background: "var(--surface)", border: "1px solid var(--border)",
                  color: "var(--text)", fontSize: 14, outline: "none", fontFamily: "inherit",
                }}
              />
            </div>
          ))}

          {error && <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 8, padding: "10px 14px", fontSize: 13, color: "#ef4444" }}>{error}</div>}

          <button type="submit" disabled={loading} style={{
            padding: "12px", borderRadius: 10, background: "var(--accent2)", border: "none",
            color: "#fff", fontSize: 14, fontWeight: 600, cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.7 : 1, marginTop: 4,
          }}>{loading ? "Creating account…" : "Create account"}</button>
        </form>

        <p style={{ textAlign: "center", marginTop: 20, fontSize: 13, color: "var(--muted)" }}>
          Already have an account?{" "}
          <a href="/login" style={{ color: "var(--accent2)", textDecoration: "none", fontWeight: 500 }}>Sign in</a>
        </p>
      </div>
    </div>
  );
}
