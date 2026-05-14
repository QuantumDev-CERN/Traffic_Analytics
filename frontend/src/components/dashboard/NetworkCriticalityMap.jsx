export default function NetworkCriticalityMap({ locations }) {
  const ranked = Object.values(locations || {}).sort((a, b) => b.criticality - a.criticality).slice(0, 6);
  return (
    <section className="section compact-section">
      <p className="eyebrow">Network criticality</p>
      <h2>Highest-risk nodes</h2>
      <div className="rank-list">
        {ranked.map((loc, index) => (
          <div key={loc.name}>
            <span>{index + 1}</span>
            <strong>{loc.name}</strong>
            <em>{Math.round(loc.criticality * 100)}</em>
          </div>
        ))}
      </div>
    </section>
  );
}
