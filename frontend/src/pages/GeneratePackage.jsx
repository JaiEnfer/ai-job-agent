import { useEffect, useState } from "react";
import api from "../services/api";

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
    <div>
      <h1>Generate Application Package</h1>

      <div style={{ display: "grid", gap: "10px", maxWidth: "600px" }}>
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
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h2>Package Generated</h2>
          <p><strong>Package ID:</strong> {result.id}</p>
          <p><strong>Status:</strong> {result.status}</p>
          <p><strong>Job ID:</strong> {result.job_id}</p>
          <p><strong>Profile ID:</strong> {result.profile_id}</p>
          <pre style={{ whiteSpace: "pre-wrap", background: "#f4f4f4", padding: "12px" }}>
            {result.application_package_text}
          </pre>
        </div>
      )}
    </div>
  );
}