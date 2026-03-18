import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function ApplicationPackages() {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/application-package-store/records")
      .then((response) => setPackages(response.data))
      .catch((error) => console.error("Failed to load packages:", error))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Application Packages</h1>
        <p className="page-subtitle">Generated CV, cover letter, ATS, and match bundles.</p>
      </div>

      {loading ? (
        <div className="card">Loading packages...</div>
      ) : packages.length === 0 ? (
        <div className="card">No application packages found.</div>
      ) : (
        <div className="list">
          {packages.map((pkg) => (
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
                <StatusBadge status={pkg.status} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}