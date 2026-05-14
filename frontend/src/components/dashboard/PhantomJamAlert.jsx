export default function PhantomJamAlert({ location }) {
  const data = (location?.speed_history || [60, 40, 55, 35, 42, 24]).map((speed, i) => ({ i, speed }));
  const points = data
    .map((point, index) => {
      const x = (index / Math.max(1, data.length - 1)) * 280;
      const y = 78 - ((point.speed - 10) / 55) * 68;
      return `${x.toFixed(1)},${Math.max(6, Math.min(80, y)).toFixed(1)}`;
    })
    .join(" ");
  return (
    <section className="section compact-section alert-section">
      <p className="eyebrow">Jamiton detector</p>
      <h2>Phantom jam</h2>
      <p className="metric-line">{location?.name || "Akshardham Route"} · no incident flag</p>
      <div className="mini-chart">
        <svg viewBox="0 0 280 86" role="img" aria-label="Phantom jam speed oscillation" className="mini-svg">
          <polyline points={points} fill="none" stroke="#dc2626" strokeWidth="4" strokeLinejoin="round" strokeLinecap="round" />
          {points.split(" ").map((point, index) => {
            const [x, y] = point.split(",");
            return <circle key={index} cx={x} cy={y} r="3" fill="#dc2626" />;
          })}
        </svg>
      </div>
    </section>
  );
}
