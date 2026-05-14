export const congestionColors = {
  Low: "#16a34a",
  Medium: "#ca8a04",
  High: "#f97316",
  "Very High": "#dc2626"
};

export function colorForCongestion(level) {
  return congestionColors[level] || "#64748b";
}
