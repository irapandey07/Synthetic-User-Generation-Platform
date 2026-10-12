function scoreColor(score) {
  if (score >= 65) return "var(--teal)";
  if (score >= 40) return "var(--mustard)";
  return "var(--stamp-red)";
}

export default function AdoptionScore({ result }) {
  if (!result) return null;
  const { overallScore, segments = [], summary } = result;

  return (
    <div className="intake-card" style={{ marginTop: 24, position: "static" }}>
      <p className="intake-label">Adoption Scoring — Milestone 3</p>
      <h2>Would people use this?</h2>

      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 14 }}>
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: "50%",
            border: `4px solid ${scoreColor(overallScore)}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "var(--font-mono)",
            fontWeight: 600,
            fontSize: 16,
          }}
        >
          {overallScore}
        </div>
        <p style={{ fontSize: 13, margin: 0, color: "var(--ink-soft)" }}>{summary}</p>
      </div>

      <p className="section-label">By segment</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {segments.map((s) => (
          <div key={s.segment} style={{ border: "1px solid var(--rule)", borderRadius: 2, padding: "8px 10px", background: "var(--card)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <strong style={{ fontFamily: "var(--font-display)", fontSize: 14 }}>{s.segment}</strong>
              <span
                className="tag"
                style={{ borderColor: scoreColor(s.score), color: scoreColor(s.score) }}
              >
                {s.score}/100 · {s.personaCount} people
              </span>
            </div>
            <p style={{ fontSize: 12.5, margin: "4px 0 0", color: "var(--ink-soft)" }}>{s.reasoning}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
