export default function PersonaCard({ persona }) {
  const {
    id,
    name,
    age,
    occupation,
    location,
    quote,
    personalityTraits = [],
    behavioralPatterns = [],
    psychProfile,
    painPoints = [],
    techSavviness,
  } = persona;

  return (
    <article className="persona-card">
      <span className="punch-hole" aria-hidden="true" />
      <span className="card-id">{id}</span>

      <div className="card-top">
        <h3 className="persona-name">{name}</h3>
        <p className="persona-meta">
          {age} · {occupation}
          {location ? ` · ${location}` : ""}
        </p>
      </div>

      {quote && <p className="persona-quote">&ldquo;{quote}&rdquo;</p>}

      {personalityTraits.length > 0 && (
        <>
          <p className="section-label">Personality traits</p>
          {personalityTraits.map((t) => (
            <div className="trait-row" key={t.trait}>
              <span className="trait-name">{t.trait}</span>
              <span className="trait-bar-track">
                <span
                  className="trait-bar-fill"
                  style={{ width: `${Math.min(Math.max(t.score, 0), 100)}%` }}
                />
              </span>
            </div>
          ))}
        </>
      )}

      {psychProfile && (
        <>
          <p className="section-label">Psychological profile</p>
          <p className="psych-profile">{psychProfile}</p>
        </>
      )}

      {behavioralPatterns.length > 0 && (
        <>
          <p className="section-label">Behavioral patterns</p>
          <ul className="behavior-list">
            {behavioralPatterns.map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ul>
        </>
      )}

      {painPoints.length > 0 && (
        <>
          <p className="section-label">Pain points</p>
          <div className="tag-row">
            {painPoints.map((p, i) => (
              <span className="tag" key={i}>
                {p}
              </span>
            ))}
          </div>
        </>
      )}

      {techSavviness && (
        <span className="tech-badge">Tech savviness: {techSavviness}</span>
      )}
    </article>
  );
}
