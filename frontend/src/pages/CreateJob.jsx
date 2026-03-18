import { useState } from "react";
import api from "../services/api";

export default function CreateJob() {
  const [form, setForm] = useState({
    title: "",
    company: "",
    location: "",
    source: "",
    job_url: "",
    description: "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      const response = await api.post("/jobs", form);
      setMessage(`Job created successfully with ID ${response.data.id}`);
      setForm({
        title: "",
        company: "",
        location: "",
        source: "",
        job_url: "",
        description: "",
      });
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create job");
    }
  }

  return (
    <div>
      <h1>Create Job</h1>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "10px", maxWidth: "700px" }}>
        <input name="title" placeholder="Title" value={form.title} onChange={handleChange} required />
        <input name="company" placeholder="Company" value={form.company} onChange={handleChange} required />
        <input name="location" placeholder="Location" value={form.location} onChange={handleChange} />
        <input name="source" placeholder="Source" value={form.source} onChange={handleChange} />
        <input name="job_url" placeholder="Job URL" value={form.job_url} onChange={handleChange} />
        <textarea
          name="description"
          placeholder="Job description"
          value={form.description}
          onChange={handleChange}
          rows={10}
          required
        />
        <button type="submit">Create Job</button>
      </form>

      {message && <p style={{ color: "green" }}>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}