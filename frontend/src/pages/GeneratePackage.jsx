import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function GeneratePackage() {
  const navigate = useNavigate();

  const [jobs, setJobs] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [selectedProfileId, setSelectedProfileId] = useState("");
  const [language, setLanguage] = useState("english");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/jobs").then((r) => setJobs(r.data)).catch(() => setError("Failed to load jobs"));
    api.get("/candidate-profiles").then((r) => setProfiles(r.data)).catch(() => setError("Failed to load profiles"));
  }, []);

  async function handleGenerate() {
    if (!selectedJobId || !selectedProfileId) {
      setError("Please select both a job and a profile.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await api.post(
        `/application-package-store/generate/${selectedJobId}/${selectedProfileId}?language=${language}`
      );
      navigate(`/packages/${response.data.id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to generate package.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Generate Package</h1>
        <p className="page-subtitle">Select a job and a candidate profile to generate an application package.</p>
      </div>

      <div className="card" style={{ display: "grid", gap: "14px" }}>
        <div>
          <label style={{ display: "block", marginBottom: 6, fontWeight: 500 }}>Job</label>
          <select
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: "1.5px solid #e5e7eb", fontSize: 14 }}
          >
            <option value="">Select a job…</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                #{job.id} — {job.title} @ {job.company}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: 6, fontWeight: 500 }}>Candidate Profile</label>
          <select
            value={selectedProfileId}
            onChange={(e) => setSelectedProfileId(e.target.value)}
            style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: "1.5px solid #e5e7eb", fontSize: 14 }}
          >
            <option value="">Select a profile…</option>
            {profiles.map((profile) => (
              <option key={profile.id} value={profile.id}>
                #{profile.id} — {profile.full_name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: 6, fontWeight: 500 }}>CV & Cover Letter Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: "1.5px solid #e5e7eb", fontSize: 14 }}
          >
            <option value="english">English</option>
            <option value="german">German (Deutsch)</option>
          </select>
        </div>

        {error && <div className="message-error">{error}</div>}

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="button"
          style={{ justifySelf: "start" }}
        >
          {loading ? "Generating…" : "Generate Package"}
        </button>
      </div>
    </div>
  );
}