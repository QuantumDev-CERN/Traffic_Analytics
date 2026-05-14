import { useCallback, useState } from "react";
import AlertFeed from "./components/alerts/AlertFeed.jsx";
import ChatBot from "./components/chatbot/ChatBot.jsx";
import HysteresisPanel from "./components/dashboard/HysteresisPanel.jsx";
import NetworkCriticalityMap from "./components/dashboard/NetworkCriticalityMap.jsx";
import PhantomJamAlert from "./components/dashboard/PhantomJamAlert.jsx";
import PredictionDashboard from "./components/dashboard/PredictionDashboard.jsx";
import CascadeAnimation from "./components/map/CascadeAnimation.jsx";
import CongestionMap from "./components/map/CongestionMap.jsx";
import EmergencyRoute from "./components/map/EmergencyRoute.jsx";
import RouteComparison from "./components/routing/RouteComparison.jsx";
import TollEstimator from "./components/routing/TollEstimator.jsx";
import { useTrafficState } from "./hooks/useTrafficState.js";
import { useWebSocket } from "./hooks/useWebSocket.js";

export default function App() {
  const { state, setState, loading, error, apiBase } = useTrafficState();
  const [routeData, setRouteData] = useState(null);
  const [emergency, setEmergency] = useState(null);
  const handleWs = useCallback((data) => setState(data), [setState]);
  useWebSocket(handleWs);

  async function injectCascade() {
    const res = await fetch(`${apiBase}/api/cascade/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location: "Connaught Place", severity: 0.92 })
    });
    const data = await res.json();
    setState((prev) => ({ ...prev, cascade_events: data.cascade_events }));
  }

  async function runRoutes() {
    const res = await fetch(`${apiBase}/api/route/equilibrium`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origin: "Connaught Place", destination: "Cyber Hub Gurgaon", users: 10000 })
    });
    setRouteData(await res.json());
  }

  async function runEmergency() {
    const res = await fetch(`${apiBase}/api/emergency/route`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origin: "India Gate", destination: "IGI Airport T3", vehicle: "ambulance" })
    });
    setEmergency(await res.json());
  }

  if (loading || !state) {
    return (
      <main className="loading">
        <span>{error ? `Traffic backend unavailable: ${error}` : "Loading traffic intelligence..."}</span>
      </main>
    );
  }
  const akshardham = state.locations?.["Akshardham Route"];

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">HackZilla 2026</p>
          <h1>AI-Powered Smart Traffic Congestion Predictor</h1>
        </div>
        <div className="status-strip">
          <span>{Object.values(state.locations).filter((l) => l.congestion === "Very High").length} severe</span>
          <span>{state.alerts.length} alerts</span>
          <span>{state.cascade_events.length} cascade hits</span>
        </div>
      </header>

      <div className="hero-grid" aria-label="Live traffic operations">
        <CongestionMap locations={state.locations} cascadeEvents={state.cascade_events} />
        <div className="side-stack">
          <CascadeAnimation cascadeEvents={state.cascade_events} onInject={injectCascade} />
          <EmergencyRoute result={emergency} onRun={runEmergency} />
        </div>
      </div>

      <div className="content-grid" aria-label="Traffic intelligence panels">
        <div className="main-column">
          <RouteComparison data={routeData} onRun={runRoutes} />
          <PredictionDashboard locations={state.locations} />
          <ChatBot apiBase={apiBase} />
        </div>
        <div className="stack side-column">
          <AlertFeed alerts={state.alerts} />
          <PhantomJamAlert location={akshardham} />
          <HysteresisPanel />
          <NetworkCriticalityMap locations={state.locations} />
          <TollEstimator />
        </div>
      </div>
    </main>
  );
}
