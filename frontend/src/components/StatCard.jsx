export default function StatCard({ title, value }) {
  return (
    <div className="card">
      <div className="stat-card-title">{title}</div>
      <div className="stat-card-value">{value}</div>
    </div>
  );
}