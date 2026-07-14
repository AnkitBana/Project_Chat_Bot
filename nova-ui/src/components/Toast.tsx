"use client";
import { useEffect, useRef, useState } from "react";

interface Props { message: string; visible: boolean; }

export default function Toast({ message, visible }: Props) {
  return (
    <div className={`toast ${visible ? "show" : ""}`}>{message}</div>
  );
}

// Hook for easy toast usage
export function useToast() {
  const [msg, setMsg] = useState("");
  const [visible, setVisible] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  function showToast(text: string) {
    setMsg(text);
    setVisible(true);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setVisible(false), 2600);
  }

  return { msg, visible, showToast };
}
