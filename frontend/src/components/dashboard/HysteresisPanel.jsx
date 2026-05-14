const data = Array.from({ length: 8 }, (_, i) => ({
  minute: i * 5,
  capacity: Math.round(90 + 10 * (1 - Math.exp((-3 * i) / 7)))
}));

export default function HysteresisPanel() {
  return (
    <section className="section compact-section">
      <p className="eyebrow">Hysteresis</p>
      <h2>Recovery mode</h2>
      <p className="metric-line">DND Flyway · 28 min to full capacity</p>
      <div className="mini-chart">
        <svg viewBox="0 0 280 86" role="img" aria-label="Recovery capacity curve" className="mini-svg">
          <path d="M0 74 C35 70 48 58 72 51 C105 41 120 31 150 25 C188 18 220 14 280 11 L280 86 L0 86 Z" fill="#99f6e4" />
          <path d="M0 74 C35 70 48 58 72 51 C105 41 120 31 150 25 C188 18 220 14 280 11" fill="none" stroke="#0f766e" strokeWidth="4" />
          {data.map((point, index) => (
            <circle key={point.minute} cx={(index / (data.length - 1)) * 280} cy={86 - ((point.capacity - 88) / 13) * 76} r="2.6" fill="#0f766e" />
          ))}
        </svg>
      </div>
    </section>
  );
}
