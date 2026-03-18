import { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    api.get("/application-summary")
      .then((res) => setSummary(res.data))
      .catch(() => {});
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Germany-focused AI job application workflow</p>

      {summary ? (
        <div>
          <p><strong>Total Applications:</strong> {summary.total_applications}</p>
          <h3>Status Breakdown</h3>
          <pre style={{ background: "#f4f4f4", padding: "12px" }}>
            {JSON.stringify(summary.status_breakdown, null, 2)}
          </pre>
        </div>
      ) : (
        <p>Loading summary...</p>
      )}
    </div>
  );
}