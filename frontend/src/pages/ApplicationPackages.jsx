import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function ApplicationPackages() {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");

  async function loadPackages() {
    setLoading(true);
    try {
      const response = await api.get("/application-package-store/records");
      setPackages(response.data);
    } catch (err) {
      console.error("Failed to load packages:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPackages();
  }, []);

  async function handleDelete(id) {
    if (!window.confirm(`Are you sure you want to delete Package #${id}? This cannot be undone.`)) return;
    setDeletingId(id);
    setError("");
    try {
      await api.delete(`/application-package-store/records/${id}`);
      setPackages((prev) => prev.filter((pkg) => pkg.id !== id));
    } catch (err) {
      console.error("Failed to delete package:", err);
      setError(`Failed to delete Package #${id}.`);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Application Packages</h1>
        <p className="page-subtitle">Generated CV, cover letter, ATS, and match bundles.</p>
      </div>

      {error && <div className="message-error">{error}</div>}

      {loading ? (
        <div className="card">Loading packages...</div>
      ) : packages.length === 0 ? (
        <div className="card">No application packages found.</div>
      ) : (
        <div className="list">
          {packages.filter((pkg) => pkg.id != null).map((pkg) => (
            <div key={pkg.id} className="list-item">
              <div className="inline-actions" style={{ justifyContent: "space-between" }}>
                <div>
                  <div className="list-item-title">
                    <Link to={`/packages/${pkg.id}`}>Package #{pkg.id}</Link>
                  </div>
                  <div className="list-item-subtitle">
                    Job {pkg.job_id} · Profile {pkg.profile_id}
                  </div>
                </div>
                <div className="inline-actions" style={{ gap: "10px" }}>
                  <StatusBadge status={pkg.status} />
                  <button
                    onClick={() => handleDelete(pkg.id)}
                    disabled={deletingId === pkg.id}
                    className="button"
                    style={{
                      background: "none",
                      border: "1px solid #e5e7eb",
                      color: deletingId === pkg.id ? "#9ca3af" : "#ef4444",
                      padding: "4px 10px",
                      borderRadius: "6px",
                      fontSize: "13px",
                      cursor: deletingId === pkg.id ? "not-allowed" : "pointer",
                    }}
                  >
                    {deletingId === pkg.id ? "Deleting…" : "Delete"}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}