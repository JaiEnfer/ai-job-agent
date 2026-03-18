import { useEffect, useState } from "react";
import api from "../services/api";

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
    <div>
      <h1>Applications</h1>

      {loading ? (
        <p>Loading applications...</p>
      ) : applications.length === 0 ? (
        <p>No applications found.</p>
      ) : (
        <div style={{ display: "grid", gap: "16px" }}>
          {applications.map((app) => (
            <div
              key={app.id}
              style={{
                border: "1px solid #ddd",
                padding: "12px",
                borderRadius: "8px",
                background: "#fafafa",
              }}
            >
              <p><strong>Application #{app.id}</strong></p>
              <p>Job ID: {app.job_id}</p>
              <p>Profile ID: {app.profile_id}</p>
              <p>Package ID: {app.application_package_id || "N/A"}</p>
              <p>Channel: {app.application_channel || "N/A"}</p>
              <p>Recruiter: {app.recruiter_name || "N/A"}</p>
              <p>Applied At: {app.applied_at || "N/A"}</p>
              <p>Notes: {app.notes || "N/A"}</p>

              <div style={{ display: "flex", gap: "10px", alignItems: "center", marginTop: "10px" }}>
                <strong>Status:</strong>
                <select
                  value={app.status}
                  onChange={(e) => updateStatus(app.id, e.target.value)}
                >
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