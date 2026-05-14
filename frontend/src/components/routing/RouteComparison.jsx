import { SplitSquareHorizontal } from "lucide-react";

export default function RouteComparison({ data, onRun }) {
  const routes = data?.wardrop || [
    { percentage: 52, eta_minutes: 31, name: "Ring Road" },
    { percentage: 29, eta_minutes: 33, name: "NH48" },
    { percentage: 19, eta_minutes: 36, name: "Bypass" }
  ];
  return (
    <section className="section">
      <div className="section-head">
        <div>
          <p className="eyebrow">Braess / Wardrop</p>
          <h2>Naive vs equilibrium routing</h2>
        </div>
        <button className="icon-button" onClick={onRun} title="Run route simulation">
          <SplitSquareHorizontal size={18} />
          <span>Run</span>
        </button>
      </div>
      <div className="route-grid">
        <div className="route-panel naive">
          <h3>Naive routing</h3>
          <strong>100%</strong>
          <p>Ring Road</p>
          <b>Secondary jam in 18 min</b>
        </div>
        <div className="route-panel wardrop">
          <h3>Wardrop equilibrium</h3>
          {routes.map((route, index) => (
            <div className="route-row" key={`${route.name}-${index}`}>
              <div><span style={{ width: `${route.percentage}%` }} /></div>
              <p>{route.percentage}% · Route {String.fromCharCode(65 + index)}</p>
              <em>{route.eta_minutes}m</em>
            </div>
          ))}
          <b>No secondary jam</b>
        </div>
      </div>
    </section>
  );
}
