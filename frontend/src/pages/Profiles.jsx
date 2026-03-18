import { useEffect, useState } from "react";
import api from "../services/api";

export default function Profiles() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/candidate-profiles")
      .then((response) => setProfiles(response.data))
      .catch((error) => console.error("Failed to load profiles:", error))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Candidate Profiles</h1>
        <p className="page-subtitle">Reusable source profiles for tailored applications.</p>
      </div>

      {loading ? (
        <div className="card">Loading profiles...</div>
      ) : profiles.length === 0 ? (
        <div className="card">No profiles found.</div>
      ) : (
        <div className="list">
          {profiles.map((profile) => (
            <div key={profile.id} className="list-item">
              <div className="list-item-title">{profile.full_name}</div>
              <div className="list-item-subtitle">
                {profile.headline || "No headline"} · {profile.location || "N/A"}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}