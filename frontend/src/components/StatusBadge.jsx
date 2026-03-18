export default function StatusBadge({ status }) {
  const safeStatus = status || "unknown";
  return <span className={`badge badge-${safeStatus}`}>{safeStatus}</span>;
}