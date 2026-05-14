import { useMemo, useState } from "react";
import { Clock, Siren } from "lucide-react";

export default function CascadeAnimation({ cascadeEvents = [], onInject }) {
  const [timeOffset, setTimeOffset] = useState(25);
  const active = useMemo(
    () => cascadeEvents.filter((event) => event.arrival_time <= timeOffset),
    [cascadeEvents, timeOffset]
  );

  return (
    <section className="section">
      <div className="section-head">
        <div>
          <p className="eyebrow">Cascading propagation</p>
          <h2>Incident wave timeline</h2>
        </div>
        <button className="icon-button danger" onClick={onInject} title="Inject Connaught Place accident">
          <Siren size={18} />
          <span>Inject CP</span>
        </button>
      </div>
      <div className="slider-row">
        <Clock size={18} />
        <input min="0" max="60" value={timeOffset} onChange={(e) => setTimeOffset(Number(e.target.value))} type="range" />
        <strong>T+{timeOffset}m</strong>
      </div>
      <div className="timeline">
        {active.map((event) => (
          <div className="timeline-item" key={`${event.location}-${event.cause}`}>
            <span>T+{Math.round(event.arrival_time)}m</span>
            <strong>{event.location}</strong>
            <em>{event.cause.replace("_", " ")}</em>
            <b>{Math.round(event.severity * 100)}%</b>
          </div>
        ))}
      </div>
    </section>
  );
}
