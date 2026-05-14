import PhaseGauge from "./PhaseGauge.jsx";
import { colorForCongestion } from "../../utils/congestionColors";

export default function PredictionDashboard({ locations }) {
  const rows = Object.values(locations || {}).sort((a, b) => b.load - a.load);
  return (
    <section className="section">
      <div className="section-head">
        <div>
          <p className="eyebrow">AI prediction dashboard</p>
          <h2>16 monitored NCR nodes</h2>
        </div>
      </div>
      <div className="location-grid">
        {rows.map((loc) => (
          <article className="location-card" key={loc.name}>
            <div className="card-top">
              <strong>{loc.name}</strong>
              <span style={{ color: colorForCongestion(loc.congestion) }}>{loc.congestion}</span>
            </div>
            <PhaseGauge value={loc.instability_index} phase={loc.phase?.phase} />
            <div className="card-metrics">
              <span>{loc.speed} km/h</span>
              <span>{loc.volume} veh/hr</span>
              <span>{Math.round(loc.load * 100)}% load</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
