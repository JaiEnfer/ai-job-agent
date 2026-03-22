import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function PackageDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [pkg, setPkg] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);

  const validId = id && id !== "undefined" && !isNaN(Number(id)) ? id : null;

  useEffect(() => {
    if (!validId) {
      navigate("/packages", { replace: true });
      return;
    }

    api
      .get(`/application-package-store/records/${validId}`)
      .then((response) => setPkg(response.data))
      .catch((err) => {
        console.error("Failed to load package:", err);
        setError("Failed to load package");
      })
      .finally(() => setLoading(false));
  }, [validId, navigate]);

  async function handleDownload(type) {
    if (!pkg?.id) return;
    const url = `/application-package-store/records/${pkg.id}/download/${type}`;
    try {
      const res = await api.get(url, { responseType: "blob" });
      const blobUrl = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `${type.replace("-", "_")}_${pkg.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch {
      setError("Failed to download file");
    }
  }

  async function handleDelete() {
    if (!pkg?.id) return;
    if (!window.confirm(`Are you sure you want to delete Package #${pkg.id}? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await api.delete(`/application-package-store/records/${pkg.id}`);
      navigate("/packages", { replace: true });
    } catch {
      setError("Failed to delete package");
      setDeleting(false);
    }
  }

  if (!validId) return null;
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

      <div className="card inline-actions">
        <button onClick={() => handleDownload("cv")} className="button">
          Download CV
        </button>
        <button onClick={() => handleDownload("cover-letter")} className="button">
          Download Cover Letter
        </button>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="button"
          style={{ marginLeft: "auto", color: "#ef4444", background: "none", border: "1px solid #e5e7eb" }}
        >
          {deleting ? "Deleting…" : "Delete Package"}
        </button>
      </div>

      {error && <div className="message-error">{error}</div>}

      <div className="card">
        <h2 className="section-title">Application Package Text</h2>
        <div className="pre-block">{pkg.application_package_text}</div>
      </div>
    </div>
  );
}