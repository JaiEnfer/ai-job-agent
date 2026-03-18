import { useEffect, useState } from "react";
import api from "../services/api";

export default function CreateApplication() {
  const [jobs, setJobs] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [packages, setPackages] = useState([]);

  const [form, setForm] = useState({
    job_id: "",
    profile_id: "",
    application_package_id: "",
    status: "draft",
    application_channel: "",
    external_application_id: "",
    recruiter_name: "",
    recruiter_email: "",
    notes: "",
    response_notes: "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/jobs").then((res) => setJobs(res.data)).catch(() => {});
    api.get("/candidate-profiles").then((res) => setProfiles(res.data)).catch(() => {});
    api.get("/application-package-store/records").then((res) => setPackages(res.data)).catch(() => {});
  }, []);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      const payload = {
        ...form,
        job_id: Number(form.job_id),
        profile_id: Number(form.profile_id),
        application_package_id: form.application_package_id ? Number(form.application_package_id) : null,
      };

      const res = await api.post("/applications", payload);
      setMessage(`Application created successfully with ID ${res.data.id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create application");
    }
  }

  return (
    <div>
      <h1>Create Application</h1>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "10px", maxWidth: "700px" }}>
        <select name="job_id" value={form.job_id} onChange={handleChange} required>
          <option value="">Select Job</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.id} - {job.title} - {job.company}
            </option>
          ))}
        </select>

        <select name="profile_id" value={form.profile_id} onChange={handleChange} required>
          <option value="">Select Profile</option>
          {profiles.map((profile) => (
            <option key={profile.id} value={profile.id}>
              {profile.id} - {profile.full_name}
            </option>
          ))}
        </select>

        <select name="application_package_id" value={form.application_package_id} onChange={handleChange}>
          <option value="">Select Package (Optional)</option>
          {packages.map((pkg) => (
            <option key={pkg.id} value={pkg.id}>
              Package #{pkg.id} - Job {pkg.job_id} / Profile {pkg.profile_id}
            </option>
          ))}
        </select>

        <select name="status" value={form.status} onChange={handleChange}>
          <option value="draft">draft</option>
          <option value="generated">generated</option>
          <option value="reviewed">reviewed</option>
          <option value="ready_to_apply">ready_to_apply</option>
          <option value="applied">applied</option>
          <option value="interview">interview</option>
          <option value="rejected">rejected</option>
          <option value="offer">offer</option>
        </select>

        <input
          name="application_channel"
          placeholder="Application channel"
          value={form.application_channel}
          onChange={handleChange}
        />
        <input
          name="external_application_id"
          placeholder="External application ID"
          value={form.external_application_id}
          onChange={handleChange}
        />
        <input
          name="recruiter_name"
          placeholder="Recruiter name"
          value={form.recruiter_name}
          onChange={handleChange}
        />
        <input
          name="recruiter_email"
          placeholder="Recruiter email"
          value={form.recruiter_email}
          onChange={handleChange}
        />
        <textarea
          name="notes"
          placeholder="Notes"
          value={form.notes}
          onChange={handleChange}
          rows={4}
        />
        <textarea
          name="response_notes"
          placeholder="Response notes"
          value={form.response_notes}
          onChange={handleChange}
          rows={4}
        />

        <button type="submit">Create Application</button>
      </form>

      {message && <p style={{ color: "green" }}>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}