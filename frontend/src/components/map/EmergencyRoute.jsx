import { Ambulance } from "lucide-react";

export default function EmergencyRoute({ onRun, result }) {
  return (
    <section className="section compact-section">
      <div className="section-head">
        <div>
          <p className="eyebrow">Emergency priority</p>
          <h2>Green corridor</h2>
        </div>
        <button className="icon-button civic" onClick={onRun} title="Run emergency corridor">
          <Ambulance size={18} />
          <span>Route</span>
        </button>
      </div>
      <p className="metric-line">
        {result?.green_corridor?.[0]?.eta_minutes || 18} min ETA · signal preemption active
      </p>
    </section>
  );
}
