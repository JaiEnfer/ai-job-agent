import { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [packages, setPackages] = useState([]);

  useEffect(() => {
    api.get("/application-summary").then((res) => setSummary(res.data)).catch(() => {});
    api.get("/jobs").then((res) => setJobs(res.data)).catch(() => {});
    api.get("/candidate-profiles").then((res) => setProfiles(res.data)).catch(() => {});
    api.get("/application-package-store/records").then((res) => setPackages(res.data)).catch(() => {});
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Germany-focused AI job application workflow</p>

      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", marginTop: "20px" }}>
        <div style={{ border: "1px solid #ddd", padding: "16px", borderRadius: "8px", minWidth: "180px" }}>
          <h3>Jobs</h3>
          <p>{jobs.length}</p>
        </div>

        <div style={{ border: "1px solid #ddd", padding: "16px", borderRadius: "8px", minWidth: "180px" }}>
          <h3>Profiles</h3>
          <p>{profiles.length}</p>
        </div>

        <div style={{ border: "1px solid #ddd", padding: "16px", borderRadius: "8px", minWidth: "180px" }}>
          <h3>Packages</h3>
          <p>{packages.length}</p>
        </div>

        <div style={{ border: "1px solid #ddd", padding: "16px", borderRadius: "8px", minWidth: "180px" }}>
          <h3>Applications</h3>
          <p>{summary?.total_applications || 0}</p>
        </div>
      </div>

      <div style={{ marginTop: "24px" }}>
        <h3>Status Breakdown</h3>
        <pre style={{ background: "#f4f4f4", padding: "12px", borderRadius: "8px" }}>
          {JSON.stringify(summary?.status_breakdown || {}, null, 2)}
        </pre>
      </div>
    </div>
  );
}