import { useEffect, useState } from "react";
import api from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function GeneratePackage() {
  const [jobs, setJobs] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [jobId, setJobId] = useState("");
  const [profileId, setProfileId] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/jobs").then((res) => setJobs(res.data)).catch(() => {});
    api.get("/candidate-profiles").then((res) => setProfiles(res.data)).catch(() => {});
  }, []);

  async function handleGenerate() {
    setError("");
    setResult(null);
    setLoading(true);

    try {
      const res = await api.post(`/application-package-store/generate/${jobId}/${profileId}`);
      setResult(res.data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to generate package");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Generate Application Package</h1>
        <p className="page-subtitle">Select a job and profile to build a tailored application package.</p>
      </div>

      <div className="card form-grid">
        <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
          <option value="">Select Job</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.id} - {job.title} - {job.company}
            </option>
          ))}
        </select>

        <select value={profileId} onChange={(e) => setProfileId(e.target.value)}>
          <option value="">Select Profile</option>
          {profiles.map((profile) => (
            <option key={profile.id} value={profile.id}>
              {profile.id} - {profile.full_name}
            </option>
          ))}
        </select>

        <button onClick={handleGenerate} disabled={!jobId || !profileId || loading}>
          {loading ? "Generating..." : "Generate Package"}
        </button>

        {error && <div className="message-error">{error}</div>}
      </div>

      {result && (
        <div className="card stack">
          <div className="inline-actions" style={{ justifyContent: "space-between" }}>
            <h2 className="section-title" style={{ margin: 0 }}>Generated Package</h2>
            <StatusBadge status={result.status} />
          </div>
          <div className="kv">
            <div className="kv-row"><span className="kv-label">Package ID:</span> {result.id}</div>
            <div className="kv-row"><span className="kv-label">Job ID:</span> {result.job_id}</div>
            <div className="kv-row"><span className="kv-label">Profile ID:</span> {result.profile_id}</div>
          </div>
          <div className="pre-block">{result.application_package_text}</div>
        </div>
      )}
    </div>
  );
}