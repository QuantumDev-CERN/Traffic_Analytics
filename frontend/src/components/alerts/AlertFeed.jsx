import { Bell } from "lucide-react";

export default function AlertFeed({ alerts = [] }) {
  return (
    <section className="section">
      <div className="section-head">
        <div>
          <p className="eyebrow">Live commuter alerts</p>
          <h2>Signal feed</h2>
        </div>
        <Bell size={20} />
      </div>
      <div className="alerts">
        {alerts.slice(0, 6).map((alert, index) => (
          <article className={`alert ${alert.severity}`} key={`${alert.type}-${index}`}>
            <strong>{alert.type.replace("_", " ")}</strong>
            <p>{alert.message}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
