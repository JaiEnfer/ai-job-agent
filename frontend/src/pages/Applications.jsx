import { useEffect, useState } from "react";
import api from "../services/api";

export default function Applications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/applications")
      .then((response) => setApplications(response.data))
      .catch((error) => console.error("Failed to load applications:", error))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1>Applications</h1>

      {loading ? (
        <p>Loading applications...</p>
      ) : applications.length === 0 ? (
        <p>No applications found.</p>
      ) : (
        <ul>
          {applications.map((app) => (
            <li key={app.id}>
              <strong>Application #{app.id}</strong> — Job {app.job_id} / Profile {app.profile_id} / Status: {app.status}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}