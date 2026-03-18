import { useEffect, useState } from "react";
import api from "../services/api";

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/jobs")
      .then((response) => setJobs(response.data))
      .catch((error) => console.error("Failed to load jobs:", error))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Jobs</h1>
        <p className="page-subtitle">All stored roles from ingestion and manual entry.</p>
      </div>

      {loading ? (
        <div className="card">Loading jobs...</div>
      ) : jobs.length === 0 ? (
        <div className="card">No jobs found.</div>
      ) : (
        <div className="list">
          {jobs.map((job) => (
            <div key={job.id} className="list-item">
              <div className="list-item-title">{job.title}</div>
              <div className="list-item-subtitle">
                {job.company} · {job.location || "N/A"} · {job.source || "N/A"}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}