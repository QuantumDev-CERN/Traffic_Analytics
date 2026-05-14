export const pct = (value) => `${Math.round((value || 0) * 100)}%`;
export const eta = (minutes) => (minutes == null ? "--" : `${Math.round(minutes)} min`);
export const timeLabel = (value) => new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
