import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function PackageDetail() {
  const { id } = useParams();
  const [pkg, setPkg] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get(`/application-package-store/records/${id}`)
      .then((response) => setPkg(response.data))
      .catch((error) => console.error("Failed to load package:", error))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="card">Loading package...</div>;
  if (!pkg) return <div className="card">Package not found.</div>;

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Package Detail #{pkg.id}</h1>
        <p className="page-subtitle">Generated application package record.</p>
      </div>

      <div className="card kv">
        <div className="kv-row"><span className="kv-label">Status:</span> <StatusBadge status={pkg.status} /></div>
        <div className="kv-row"><span className="kv-label">Job ID:</span> {pkg.job_id}</div>
        <div className="kv-row"><span className="kv-label">Profile ID:</span> {pkg.profile_id}</div>
      </div>

      <div className="card">
        <h2 className="section-title">Application Package Text</h2>
        <div className="pre-block">{pkg.application_package_text}</div>
      </div>
    </div>
  );
}