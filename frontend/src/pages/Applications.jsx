import { useEffect, useState } from "react";
import api from "../services/api";
import StatusBadge from "../components/StatusBadge";

const STATUS_OPTIONS = [
  "draft",
  "generated",
  "reviewed",
  "ready_to_apply",
  "applied",
  "interview",
  "rejected",
  "offer",
];

export default function Applications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  async function loadApplications() {
    setLoading(true);
    try {
      const response = await api.get("/applications");
      setApplications(response.data);
    } catch (error) {
      console.error("Failed to load applications:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadApplications();
  }, []);

  async function updateStatus(id, status) {
    try {
      await api.put(`/applications/${id}`, { status });
      loadApplications();
    } catch (error) {
      console.error("Failed to update status:", error);
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Applications</h1>
        <p className="page-subtitle">Track live application workflow across statuses.</p>
      </div>

      {loading ? (
        <div className="card">Loading applications...</div>
      ) : applications.length === 0 ? (
        <div className="card">No applications found.</div>
      ) : (
        <div className="list">
          {applications.map((app) => (
            <div key={app.id} className="list-item">
              <div className="inline-actions" style={{ justifyContent: "space-between" }}>
                <div>
                  <div className="list-item-title">Application #{app.id}</div>
                  <div className="list-item-subtitle">
                    Job {app.job_id} · Profile {app.profile_id} · Package {app.application_package_id || "N/A"}
                  </div>
                </div>
                <StatusBadge status={app.status} />
              </div>

              <div className="kv" style={{ marginTop: "12px" }}>
                <div className="kv-row"><span className="kv-label">Channel:</span> {app.application_channel || "N/A"}</div>
                <div className="kv-row"><span className="kv-label">Recruiter:</span> {app.recruiter_name || "N/A"}</div>
                <div className="kv-row"><span className="kv-label">Applied At:</span> {app.applied_at || "N/A"}</div>
                <div className="kv-row"><span className="kv-label">Notes:</span> {app.notes || "N/A"}</div>
              </div>

              <div className="inline-actions" style={{ marginTop: "12px" }}>
                <span className="kv-label">Update Status:</span>
                <select value={app.status} onChange={(e) => updateStatus(app.id, e.target.value)}>
                  {STATUS_OPTIONS.map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}