import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function ApplicationPackages() {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/application-package-store/records")
      .then((response) => {
        setPackages(response.data);
      })
      .catch((error) => {
        console.error("Failed to load packages:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h1>Application Packages</h1>

      {loading ? (
        <p>Loading packages...</p>
      ) : packages.length === 0 ? (
        <p>No application packages found.</p>
      ) : (
        <ul>
          {packages.map((pkg) => (
            <li key={pkg.id}>
              <Link to={`/packages/${pkg.id}`}>
                Package #{pkg.id}
              </Link>{" "}
              — Job {pkg.job_id} / Profile {pkg.profile_id} / Status: {pkg.status}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}