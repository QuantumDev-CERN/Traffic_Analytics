import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function useTrafficState() {
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/api/state`);
        if (!res.ok) throw new Error(`State request failed: ${res.status}`);
        const data = await res.json();
        if (alive) {
          setState(data);
          setError("");
        }
      } catch (err) {
        if (alive) setError(err instanceof Error ? err.message : "Traffic state unavailable");
      } finally {
        if (alive) setLoading(false);
      }
    }
    load();
    const id = setInterval(load, 5000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  return { state, setState, loading, error, apiBase: API_BASE };
}
