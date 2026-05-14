import { useState } from "react";
import { Send } from "lucide-react";

export default function ChatBot({ apiBase }) {
  const [text, setText] = useState("What's the fastest way from India Gate to IGI Airport right now?");
  const [answer, setAnswer] = useState("");

  async function ask() {
    const res = await fetch(`${apiBase}/api/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    setAnswer(data.response);
  }

  return (
    <section className="section">
      <div className="section-head">
        <div>
          <p className="eyebrow">Traffic assistant</p>
          <h2>Commuter chat</h2>
        </div>
        <button className="icon-button" onClick={ask} title="Ask assistant">
          <Send size={18} />
        </button>
      </div>
      <textarea value={text} onChange={(e) => setText(e.target.value)} />
      {answer && <p className="chat-answer">{answer}</p>}
    </section>
  );
}
