export default function InsightsPanel({ insights }) {
  if (!insights) return null;
  const {
    themes = [],
    sentimentBreakdown,
    agreementPatterns = [],
    behavioralTrends = [],
    summary,
    dataCoverage,
  } = insights;

  return (
    <div className="intake-card" style={{ marginTop: 24, position: "static" }}>
      <p className="intake-label">Insight Extraction Agent — Milestone 3</p>
      <h2>Extracted insights</h2>

      {dataCoverage && (
        <p style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--ink-soft)", marginTop: -8 }}>
          {dataCoverage}
        </p>
      )}

      {summary && (
        <p className="psych-profile" style={{ marginBottom: 16 }}>
          {summary}
        </p>
      )}

      {sentimentBreakdown && (
        <>
          <p className="section-label">Sentiment breakdown</p>
          <div
            style={{
              display: "flex",
              height: 10,
              borderRadius: 3,
              overflow: "hidden",
              marginBottom: 8,
              border: "1px solid var(--rule)",
            }}
          >
            <span title={`Positive: ${sentimentBreakdown.positive}%`} style={{ width: `${sentimentBreakdown.positive}%`, background: "var(--teal)" }} />
            <span title={`Neutral: ${sentimentBreakdown.neutral}%`} style={{ width: `${sentimentBreakdown.neutral}%`, background: "var(--mustard)" }} />
            <span title={`Negative: ${sentimentBreakdown.negative}%`} style={{ width: `${sentimentBreakdown.negative}%`, background: "var(--stamp-red)" }} />
          </div>
          <div className="tag-row" style={{ marginBottom: 16 }}>
            <span className="tag" style={{ borderColor: "var(--teal)", color: "var(--teal)" }}>Positive: {sentimentBreakdown.positive}%</span>
            <span className="tag" style={{ borderColor: "var(--mustard)", color: "var(--mustard)" }}>Neutral: {sentimentBreakdown.neutral}%</span>
            <span className="tag" style={{ borderColor: "var(--stamp-red)", color: "var(--stamp-red)" }}>Negative: {sentimentBreakdown.negative}%</span>
          </div>
        </>
      )}

      {themes.length > 0 && (
        <>
          <p className="section-label">Recurring themes</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 16 }}>
            {themes.map((t, i) => (
              <div key={i} style={{ border: "1px solid var(--rule)", borderRadius: 2, padding: "8px 10px", background: "var(--card)" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <strong style={{ fontFamily: "var(--font-display)", fontSize: 14 }}>{t.theme}</strong>
                  <span className="tag">{t.supportingCount} signals</span>
                </div>
                <p style={{ fontSize: 12.5, margin: "4px 0 0", color: "var(--ink-soft)" }}>{t.description}</p>
              </div>
            ))}
          </div>
        </>
      )}

      {agreementPatterns.length > 0 && (
        <>
          <p className="section-label">Agreement patterns</p>
          <ul className="behavior-list" style={{ marginBottom: 16 }}>
            {agreementPatterns.map((a, i) => <li key={i}>{a}</li>)}
          </ul>
        </>
      )}

      {behavioralTrends.length > 0 && (
        <>
          <p className="section-label">Behavioral trends</p>
          <ul className="behavior-list">
            {behavioralTrends.map((b, i) => <li key={i}>{b}</li>)}
          </ul>
        </>
      )}
    </div>
  );
}
