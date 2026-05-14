import { CircleMarker, MapContainer, Polyline, Popup, TileLayer } from "react-leaflet";
import { colorForCongestion } from "../../utils/congestionColors";

export default function CongestionMap({ locations, cascadeEvents = [], emergencyRoute = [] }) {
  const points = Object.values(locations || {});
  return (
    <div className="map-shell">
      <MapContainer center={[28.58, 77.23]} zoom={10} scrollWheelZoom className="map">
        <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {points.map((loc) => (
          <CircleMarker
            key={loc.name}
            center={[loc.lat, loc.lng]}
            radius={loc.congestion === "Very High" ? 13 : 9}
            pathOptions={{ color: colorForCongestion(loc.congestion), fillOpacity: 0.82 }}
          >
            <Popup>
              <strong>{loc.name}</strong>
              <br />
              {loc.congestion} · {loc.speed} km/h
            </Popup>
          </CircleMarker>
        ))}
        {cascadeEvents.slice(0, 6).map((event, index) => {
          const loc = locations?.[event.location];
          if (!loc || index === 0) return null;
          const prev = locations?.[cascadeEvents[index - 1]?.location];
          if (!prev) return null;
          return (
            <Polyline
              key={`${event.location}-${index}`}
              positions={[
                [prev.lat, prev.lng],
                [loc.lat, loc.lng]
              ]}
              pathOptions={{ color: "#dc2626", opacity: 0.55, weight: 4 }}
            />
          );
        })}
        {emergencyRoute.length > 1 && (
          <Polyline positions={emergencyRoute} pathOptions={{ color: "#0f766e", opacity: 0.9, weight: 6 }} />
        )}
      </MapContainer>
    </div>
  );
}
