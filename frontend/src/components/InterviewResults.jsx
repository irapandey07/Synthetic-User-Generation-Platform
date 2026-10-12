export default function InterviewResults({ results }) {
  if (!results) return null;
  const { transcripts = [], themes = [] } = results;

  return (
    <div className="intake-card" style={{ marginTop: 24, position: "static" }}>
      <p className="intake-label">Interview Simulation Agent — Results</p>
      <h2>Simulated interviews</h2>

      {themes.length > 0 && (
        <>
          <p className="section-label">Cross-persona themes</p>
          <ul className="behavior-list" style={{ marginBottom: 16 }}>
            {themes.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </>
      )}

      <p className="section-label">Transcripts</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {transcripts.map((t) => (
          <div
            key={t.personaId}
            style={{
              border: "1px solid var(--rule)",
              borderRadius: 2,
              padding: "12px 14px",
              background: "var(--card)",
            }}
          >
            <strong style={{ fontFamily: "var(--font-display)", fontSize: 15 }}>
              {t.name}
            </strong>
            <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 8 }}>
              {t.qa.map((qa, i) => (
                <div key={i}>
                  <p
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: 11,
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      color: "var(--teal-dark)",
                      margin: "0 0 2px",
                    }}
                  >
                    Q{i + 1}. {qa.question}
                  </p>
                  <p style={{ fontSize: 13, margin: 0, color: "var(--ink)" }}>
                    {qa.answer}
                  </p>
                </div>
              ))}
            </div>
            {t.takeaway && (
              <p
                style={{
                  fontSize: 12.5,
                  color: "var(--ink-soft)",
                  marginTop: 10,
                  marginBottom: 0,
                  borderTop: "1px dashed var(--rule)",
                  paddingTop: 8,
                }}
              >
                <strong>Takeaway:</strong> {t.takeaway}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
