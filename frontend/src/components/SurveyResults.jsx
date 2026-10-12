const STANCE_COLOR = {
  "Would switch": "var(--teal)",
  "Would not switch": "var(--stamp-red)",
  Undecided: "var(--mustard)",
};

export default function SurveyResults({ results }) {
  if (!results) return null;
  const { responses = [], summary } = results;
  const total = responses.length || 1;

  return (
    <div className="intake-card" style={{ marginTop: 24, position: "static" }}>
      <p className="intake-label">Survey Simulation Agent — Results</p>
      <h2>Simulated responses</h2>

      {summary && (
        <>
          <p className="section-label">Stance breakdown</p>
          <div style={{ display: "flex", height: 10, borderRadius: 3, overflow: "hidden", marginBottom: 10, border: "1px solid var(--rule)" }}>
            {Object.entries(summary.counts || {}).map(([stance, count]) => (
              <span
                key={stance}
                title={`${stance}: ${count}`}
                style={{
                  width: `${(count / total) * 100}%`,
                  background: STANCE_COLOR[stance] || "var(--rule)",
                }}
              />
            ))}
          </div>
          <div className="tag-row" style={{ marginBottom: 14 }}>
            {Object.entries(summary.counts || {}).map(([stance, count]) => (
              <span
                key={stance}
                className="tag"
                style={{
                  borderColor: STANCE_COLOR[stance] || "var(--rule)",
                  color: STANCE_COLOR[stance] || "var(--ink)",
                }}
              >
                {stance}: {count}
              </span>
            ))}
          </div>

          <p className="section-label">Key insight</p>
          <p className="psych-profile" style={{ marginBottom: 16 }}>
            {summary.keyInsight}
          </p>
        </>
      )}

      <p className="section-label">Per-persona responses</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {responses.map((r) => (
          <div
            key={r.personaId}
            style={{
              border: "1px solid var(--rule)",
              borderRadius: 2,
              padding: "10px 12px",
              background: "var(--card)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <strong style={{ fontFamily: "var(--font-display)", fontSize: 15 }}>
                {r.name}
              </strong>
              <span
                className="tag"
                style={{
                  borderColor: STANCE_COLOR[r.stance] || "var(--rule)",
                  color: STANCE_COLOR[r.stance] || "var(--ink)",
                }}
              >
                {r.stance} · {r.confidence}%
              </span>
            </div>
            {r.quote && (
              <p className="persona-quote" style={{ margin: "8px 0 6px", paddingLeft: 12 }}>
                &ldquo;{r.quote}&rdquo;
              </p>
            )}
            {r.reasoning && (
              <p style={{ fontSize: 12.5, color: "var(--ink-soft)", margin: 0 }}>
                {r.reasoning}
              </p>
            )}
            {r.answers && r.answers.length > 0 && (
              <div style={{ marginTop: 8, borderTop: "1px dashed var(--rule)", paddingTop: 8, display: "flex", flexDirection: "column", gap: 6 }}>
                {r.answers.map((a, i) => (
                  <div key={i}>
                    <p
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: 10.5,
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                        color: "var(--teal-dark)",
                        margin: "0 0 2px",
                      }}
                    >
                      Q{i + 1}. {a.question}
                    </p>
                    <p style={{ fontSize: 12.5, margin: 0 }}>{a.answer}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
