import { useState } from "react";

export default function InterviewChat({ personas, lastBrief }) {
  const [selectedId, setSelectedId] = useState("");
  const [messages, setMessages] = useState([]); // { role: 'user' | 'persona', content }
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [chatError, setChatError] = useState(null);

  const selectedPersona = personas.find((p) => p.id === selectedId);

  function handleSelectPersona(id) {
    setSelectedId(id);
    setMessages([]);
    setChatError(null);
  }

  async function handleSend() {
    if (!input.trim() || !selectedPersona) return;
    const userMessage = { role: "user", content: input.trim() };
    const newHistory = [...messages, userMessage];
    setMessages(newHistory);
    setInput("");
    setIsSending(true);
    setChatError(null);

    try {
      const res = await fetch("/api/interview-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          persona: selectedPersona,
          productDescription: lastBrief?.productDescription,
          targetAudience: lastBrief?.targetAudience,
          researchObjective: lastBrief?.researchObjective,
          history: messages,
          message: userMessage.content,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to get a reply.");
      setMessages([...newHistory, { role: "persona", content: data.reply }]);
    } catch (err) {
      setChatError(err.message);
    } finally {
      setIsSending(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  if (personas.length === 0) return null;

  return (
    <div className="intake-card" style={{ marginTop: 24, position: "static" }}>
      <p className="intake-label">Interview Mode — Milestone 3</p>
      <h2>Talk to a persona</h2>

      <div className="field">
        <label htmlFor="persona-select">Choose who to interview</label>
        <select
          id="persona-select"
          value={selectedId}
          onChange={(e) => handleSelectPersona(e.target.value)}
          style={{
            width: "100%",
            fontFamily: "var(--font-body)",
            fontSize: 14,
            padding: "9px 10px",
            border: "1px solid var(--rule-strong)",
            borderRadius: 2,
            background: "var(--card)",
          }}
        >
          <option value="">— Select a persona —</option>
          {personas.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.occupation})
            </option>
          ))}
        </select>
      </div>

      {selectedPersona && (
        <>
          <div
            style={{
              border: "1px solid var(--rule)",
              borderRadius: 2,
              background: "var(--card)",
              minHeight: 120,
              maxHeight: 360,
              overflowY: "auto",
              padding: "12px 14px",
              marginBottom: 10,
              display: "flex",
              flexDirection: "column",
              gap: 10,
            }}
          >
            {messages.length === 0 && (
              <p style={{ fontSize: 12.5, color: "var(--ink-soft)", margin: 0 }}>
                Ask {selectedPersona.name} anything about the product. They'll stay in
                character and remember earlier turns in this conversation.
              </p>
            )}
            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                  maxWidth: "80%",
                }}
              >
                <p
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: "var(--ink-soft)",
                    margin: "0 0 2px",
                    textAlign: m.role === "user" ? "right" : "left",
                  }}
                >
                  {m.role === "user" ? "You" : selectedPersona.name}
                </p>
                <p
                  style={{
                    margin: 0,
                    fontSize: 13.5,
                    padding: "8px 10px",
                    borderRadius: 4,
                    background: m.role === "user" ? "var(--teal)" : "var(--paper)",
                    color: m.role === "user" ? "var(--paper-light)" : "var(--ink)",
                  }}
                >
                  {m.content}
                </p>
              </div>
            ))}
            {isSending && (
              <p style={{ fontSize: 12, color: "var(--ink-soft)", margin: 0 }}>
                {selectedPersona.name} is typing…
              </p>
            )}
          </div>

          {chatError && <p className="error-note">{chatError}</p>}

          <div style={{ display: "flex", gap: 8 }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask ${selectedPersona.name} a question…`}
              style={{
                flex: 1,
                fontFamily: "var(--font-body)",
                fontSize: 14,
                padding: "9px 10px",
                border: "1px solid var(--rule-strong)",
                borderRadius: 2,
                background: "var(--card)",
              }}
            />
            <button
              className="generate-btn"
              style={{ width: "auto", padding: "9px 18px" }}
              onClick={handleSend}
              disabled={isSending || !input.trim()}
            >
              Send
            </button>
          </div>
        </>
      )}
    </div>
  );
}
