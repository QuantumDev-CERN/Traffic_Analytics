import { useEffect } from "react";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/live";

export function useWebSocket(onMessage) {
  useEffect(() => {
    const socket = new WebSocket(WS_URL);
    socket.onmessage = (event) => onMessage(JSON.parse(event.data));
    socket.onerror = () => {};
    return () => socket.close();
  }, [onMessage]);
}
