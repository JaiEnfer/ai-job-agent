import { useEffect, useState } from "react";
import api from "../services/api";

export default function Profiles() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    api
      .get("/candidate-profiles")
      .then((response) => setProfiles(response.data))
      .catch((error) => {
        console.error("Failed to load profiles:", error);
        setError("Failed to load profiles");
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(id) {
    if (!window.confirm("Delete this profile? This cannot be undone.")) return;

    setError("");
    setDeleting(id);

    try {
      await api.delete(`/candidate-profiles/${id}`);
      setProfiles((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      console.error("Failed to delete profile:", err);
      setError("Failed to delete profile");
    } finally {
      setDeleting(null);
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Candidate Profiles</h1>
        <p className="page-subtitle">Reusable source profiles for tailored applications.</p>
      </div>

      {error && <div className="message-error">{error}</div>}

      {loading ? (
        <div className="card">Loading profiles...</div>
      ) : profiles.length === 0 ? (
        <div className="card">No profiles found.</div>
      ) : (
        <div className="list">
          {profiles.map((profile) => (
            <div key={profile.id} className="list-item">
              <div>
                <div className="list-item-title">{profile.full_name}</div>
                <div className="list-item-subtitle">
                  {profile.headline || "No headline"} · {profile.location || "N/A"}
                </div>
              </div>
              <button
                className="button button--danger"
                disabled={deleting === profile.id}
                onClick={() => handleDelete(profile.id)}
              >
                {deleting === profile.id ? "Deleting..." : "Delete"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}