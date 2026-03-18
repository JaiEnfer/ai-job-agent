import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

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

  if (loading) return <p>Loading package...</p>;
  if (!pkg) return <p>Package not found.</p>;

  return (
    <div>
      <h1>Package Detail #{pkg.id}</h1>
      <p><strong>Status:</strong> {pkg.status}</p>
      <p><strong>Job ID:</strong> {pkg.job_id}</p>
      <p><strong>Profile ID:</strong> {pkg.profile_id}</p>

      <h2>Application Package Text</h2>
      <pre style={{ whiteSpace: "pre-wrap", background: "#f4f4f4", padding: "12px" }}>
        {pkg.application_package_text}
      </pre>
    </div>
  );
}