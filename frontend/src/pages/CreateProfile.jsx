import { useState } from "react";
import api from "../services/api";

export default function CreateProfile() {
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    location: "",
    linkedin_url: "",
    github_url: "",
    portfolio_url: "",
    headline: "",
    summary: "",
    skills: "",
    experience: "",
    projects: "",
    education: "",
    certifications: "",
    languages: "",
    target_roles: "",
    preferred_locations: "",
    work_authorization: "",
    visa_status: "",
    open_to_relocation: true,
    open_to_remote: true,
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      const response = await api.post("/candidate-profiles", form);
      setMessage(`Profile created successfully with ID ${response.data.id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create profile");
    }
  }

  return (
    <div>
      <h1>Create Candidate Profile</h1>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "10px", maxWidth: "800px" }}>
        <input name="full_name" placeholder="Full name" value={form.full_name} onChange={handleChange} required />
        <input name="email" placeholder="Email" value={form.email} onChange={handleChange} />
        <input name="phone" placeholder="Phone" value={form.phone} onChange={handleChange} />
        <input name="location" placeholder="Location" value={form.location} onChange={handleChange} />
        <input name="linkedin_url" placeholder="LinkedIn URL" value={form.linkedin_url} onChange={handleChange} />
        <input name="github_url" placeholder="GitHub URL" value={form.github_url} onChange={handleChange} />
        <input name="portfolio_url" placeholder="Portfolio URL" value={form.portfolio_url} onChange={handleChange} />
        <input name="headline" placeholder="Headline" value={form.headline} onChange={handleChange} />
        <textarea name="summary" placeholder="Summary" value={form.summary} onChange={handleChange} rows={4} />
        <textarea name="skills" placeholder="Skills" value={form.skills} onChange={handleChange} rows={3} />
        <textarea name="experience" placeholder="Experience" value={form.experience} onChange={handleChange} rows={5} />
        <textarea name="projects" placeholder="Projects" value={form.projects} onChange={handleChange} rows={4} />
        <textarea name="education" placeholder="Education" value={form.education} onChange={handleChange} rows={3} />
        <textarea name="certifications" placeholder="Certifications" value={form.certifications} onChange={handleChange} rows={2} />
        <textarea name="languages" placeholder="Languages" value={form.languages} onChange={handleChange} rows={2} />
        <textarea name="target_roles" placeholder="Target roles" value={form.target_roles} onChange={handleChange} rows={2} />
        <textarea name="preferred_locations" placeholder="Preferred locations" value={form.preferred_locations} onChange={handleChange} rows={2} />
        <input name="work_authorization" placeholder="Work authorization" value={form.work_authorization} onChange={handleChange} />
        <input name="visa_status" placeholder="Visa status" value={form.visa_status} onChange={handleChange} />

        <label>
          <input type="checkbox" name="open_to_relocation" checked={form.open_to_relocation} onChange={handleChange} />
          Open to relocation
        </label>

        <label>
          <input type="checkbox" name="open_to_remote" checked={form.open_to_remote} onChange={handleChange} />
          Open to remote
        </label>

        <button type="submit">Create Profile</button>
      </form>

      {message && <p style={{ color: "green" }}>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}