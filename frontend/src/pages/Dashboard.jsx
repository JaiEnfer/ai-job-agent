import { useEffect, useState } from "react";
import api from "../services/api";
import StatCard from "../components/StatCard";

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
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">
          Track jobs, packages, and applications in one place.
        </p>
      </div>

      <div className="grid grid-4">
        <StatCard title="Jobs" value={jobs.length} />
        <StatCard title="Profiles" value={profiles.length} />
        <StatCard title="Packages" value={packages.length} />
        <StatCard title="Applications" value={summary?.total_applications || 0} />
      </div>

      <div className="card">
        <h2 className="section-title">Application Status Breakdown</h2>
        <div className="pre-block">
          {JSON.stringify(summary?.status_breakdown || {}, null, 2)}
        </div>
      </div>
    </div>
  );
}