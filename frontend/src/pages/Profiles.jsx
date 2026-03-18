import { useEffect, useState } from "react";
import api from "../services/api";

export default function Profiles() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/candidate-profiles")
      .then((response) => {
        setProfiles(response.data);
      })
      .catch((error) => {
        console.error("Failed to load profiles:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h1>Candidate Profiles</h1>

      {loading ? (
        <p>Loading profiles...</p>
      ) : profiles.length === 0 ? (
        <p>No profiles found.</p>
      ) : (
        <ul>
          {profiles.map((profile) => (
            <li key={profile.id}>
              <strong>{profile.full_name}</strong> — {profile.headline || "No headline"}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}