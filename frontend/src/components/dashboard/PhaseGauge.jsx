export default function PhaseGauge({ value = 0, phase = "stable" }) {
  const deg = Math.min(180, Math.max(0, value * 180));
  return (
    <div className="gauge-wrap">
      <div className="gauge">
        <div className="needle" style={{ transform: `rotate(${deg - 90}deg)` }} />
      </div>
      <div className={`phase-pill ${phase}`}>{phase.replace("_", " ")}</div>
    </div>
  );
}
