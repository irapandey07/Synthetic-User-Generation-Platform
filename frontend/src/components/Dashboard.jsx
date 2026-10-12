function scoreColor(score) {
  if (score >= 65) return "var(--teal)";
  if (score >= 40) return "var(--mustard)";
  return "var(--stamp-red)";
}

export default function Dashboard({ personas, insights, surveyResults, adoptionResult }) {
  if (!insights && !adoptionResult && !surveyResults) return null;

  const themes = insights?.themes || [];
  const sentiment = insights?.sentimentBreakdown;
  const stanceCounts = surveyResults?.summary?.counts;
  const quotes = personas.slice(0, 4).map((p) => ({ name: p.name, quote: p.quote }));

  return (
    <div className="intake-card" style={{ marginTop: 24, position: "static" }}>
      <p className="intake-label">Milestone 4 — Insights &amp; Experiment Results Dashboard</p>
      <h2>Dashboard</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: 16,
        }}
      >
        {/* Theme clusters */}
        {themes.length > 0 && (
          <div style={{ border: "1px solid var(--rule)", borderRadius: 3, padding: 12, background: "var(--card)" }}>
            <p className="section-label" style={{ marginTop: 0 }}>Theme clusters</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {themes.map((t, i) => (
                <span
                  key={i}
                  className="tag"
                  style={{ borderColor: "var(--teal)", color: "var(--teal-dark)" }}
                  title={t.description}
                >
                  {t.theme} ({t.supportingCount})
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Sentiment breakdown */}
        {sentiment && (
          <div style={{ border: "1px solid var(--rule)", borderRadius: 3, padding: 12, background: "var(--card)" }}>
            <p className="section-label" style={{ marginTop: 0 }}>Sentiment breakdown</p>
            <div style={{ display: "flex", height: 10, borderRadius: 3, overflow: "hidden", border: "1px solid var(--rule)", marginBottom: 8 }}>
              <span style={{ width: `${sentiment.positive}%`, background: "var(--teal)" }} />
              <span style={{ width: `${sentiment.neutral}%`, background: "var(--mustard)" }} />
              <span style={{ width: `${sentiment.negative}%`, background: "var(--stamp-red)" }} />
            </div>
            <p style={{ fontSize: 12, margin: 0, color: "var(--ink-soft)" }}>
              {sentiment.positive}% positive · {sentiment.neutral}% neutral · {sentiment.negative}% negative
            </p>
          </div>
        )}

        {/* Validation / stance scores */}
        {(adoptionResult || stanceCounts) && (
          <div style={{ border: "1px solid var(--rule)", borderRadius: 3, padding: 12, background: "var(--card)" }}>
            <p className="section-label" style={{ marginTop: 0 }}>Product validation score</p>
            {adoptionResult && (
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: "50%",
                    border: `3px solid ${scoreColor(adoptionResult.overallScore)}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: "var(--font-mono)",
                    fontWeight: 600,
                    fontSize: 13,
                  }}
                >
                  {adoptionResult.overallScore}
                </div>
                <span style={{ fontSize: 12, color: "var(--ink-soft)" }}>Adoption score / 100</span>
              </div>
            )}
            {stanceCounts && (
              <div className="tag-row">
                {Object.entries(stanceCounts).map(([stance, count]) => (
                  <span key={stance} className="tag">{stance}: {count}</span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Key persona quotes */}
        {quotes.length > 0 && (
          <div style={{ border: "1px solid var(--rule)", borderRadius: 3, padding: 12, background: "var(--card)" }}>
            <p className="section-label" style={{ marginTop: 0 }}>Key persona quotes</p>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {quotes.map((q, i) => (
                <p key={i} style={{ fontSize: 12.5, margin: 0, fontStyle: "italic", color: "var(--teal-dark)" }}>
                  &ldquo;{q.quote}&rdquo; <span style={{ fontStyle: "normal", color: "var(--ink-soft)" }}>— {q.name}</span>
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
