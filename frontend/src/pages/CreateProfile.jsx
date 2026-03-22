import { useState } from "react";
import api from "../services/api";

// ── helpers ────────────────────────────────────────────────────────────────
function newExperience() {
  return { id: crypto.randomUUID(), company: "", title: "", from: "", to: "", current: false, description: "" };
}

function newProject() {
  return { id: crypto.randomUUID(), title: "", description: "", link: "" };
}

function newEducation() {
  return { id: crypto.randomUUID(), institution: "", degree: "", gpa: "", from: "", to: "", current: false };
}

function newCertification() {
  return { id: crypto.randomUUID(), name: "" };
}

function newLanguage() {
  return { id: crypto.randomUUID(), language: "", proficiency: "" };
}

// Serialise structured data → plain string for the backend
function serializeExperience(entries) {
  return entries
    .map((e) => {
      const period = e.current ? `${e.from} – Present` : `${e.from} – ${e.to}`;
      return `${e.title} at ${e.company} (${period})\n${e.description}`.trim();
    })
    .join("\n\n");
}

function serializeProjects(entries) {
  return entries
    .map((p) => {
      const link = p.link ? `\nLink: ${p.link}` : "";
      return `${p.title}\n${p.description}${link}`.trim();
    })
    .join("\n\n");
}

function serializeEducation(entries) {
  return entries
    .map((e) => {
      const period = e.current ? `${e.from} – Present` : `${e.from} – ${e.to}`;
      const gpa = e.gpa ? ` | Grade/GPA: ${e.gpa}` : "";
      return `${e.degree} – ${e.institution} (${period})${gpa}`.trim();
    })
    .join("\n\n");
}

function serializeCertifications(entries) {
  return entries.map((c) => c.name.trim()).filter(Boolean).join("\n");
}

function serializeLanguages(entries) {
  return entries
    .map((l) => (l.proficiency ? `${l.language} – ${l.proficiency}` : l.language))
    .join(", ");
}

// ── sub-components ─────────────────────────────────────────────────────────
function ExperienceEntry({ entry, onChange, onRemove }) {
  function update(field, value) {
    onChange({ ...entry, [field]: value });
  }

  return (
    <div style={styles.card}>
      <button type="button" onClick={onRemove} style={styles.removeBtn} title="Remove">✕</button>

      <div style={styles.row2}>
        <div style={styles.field}>
          <label style={styles.label}>Company Name</label>
          <input
            style={styles.input}
            placeholder="e.g. Google, Startup GmbH…"
            value={entry.company}
            onChange={(e) => update("company", e.target.value)}
          />
        </div>
        <div style={styles.field}>
          <label style={styles.label}>Job Title</label>
          <input
            style={styles.input}
            placeholder="e.g. Senior Data Scientist"
            value={entry.title}
            onChange={(e) => update("title", e.target.value)}
          />
        </div>
      </div>

      <div style={{ ...styles.row3, marginTop: 12 }}>
        <div style={styles.field}>
          <label style={styles.label}>From</label>
          <input
            type="month"
            style={styles.input}
            value={entry.from}
            onChange={(e) => update("from", e.target.value)}
          />
        </div>
        <div style={styles.field}>
          <label style={styles.label}>To</label>
          <input
            type="month"
            style={{ ...styles.input, opacity: entry.current ? 0.4 : 1 }}
            value={entry.to}
            disabled={entry.current}
            onChange={(e) => update("to", e.target.value)}
          />
        </div>
        <div style={styles.checkRow}>
          <input
            type="checkbox"
            id={`current-${entry.id}`}
            checked={entry.current}
            onChange={(e) => update("current", e.target.checked)}
            style={{ accentColor: "#1a1a2e", width: 15, height: 15 }}
          />
          <label htmlFor={`current-${entry.id}`} style={{ fontSize: 13, color: "#374151", cursor: "pointer" }}>
            Currently working here
          </label>
        </div>
      </div>

      <div style={{ ...styles.field, marginTop: 12 }}>
        <label style={styles.label}>Description (optional)</label>
        <textarea
          style={{ ...styles.input, minHeight: 68, resize: "vertical" }}
          placeholder="Briefly describe your role, responsibilities, and key achievements…"
          value={entry.description}
          onChange={(e) => update("description", e.target.value)}
        />
      </div>
    </div>
  );
}

function ProjectEntry({ entry, onChange, onRemove }) {
  function update(field, value) {
    onChange({ ...entry, [field]: value });
  }

  return (
    <div style={styles.card}>
      <button type="button" onClick={onRemove} style={styles.removeBtn} title="Remove">✕</button>

      <div style={styles.field}>
        <label style={styles.label}>Project Title</label>
        <input
          style={styles.input}
          placeholder="e.g. Real-time Fraud Detection System"
          value={entry.title}
          onChange={(e) => update("title", e.target.value)}
        />
      </div>

      <div style={{ ...styles.field, marginTop: 12 }}>
        <label style={styles.label}>Description</label>
        <textarea
          style={{ ...styles.input, minHeight: 72, resize: "vertical" }}
          placeholder="Describe what you built, the tech stack, and outcomes achieved…"
          value={entry.description}
          onChange={(e) => update("description", e.target.value)}
        />
      </div>

      <div style={{ ...styles.field, marginTop: 12 }}>
        <label style={styles.label}>Project Link (optional)</label>
        <input
          type="url"
          style={styles.input}
          placeholder="https://github.com/… or live demo URL"
          value={entry.link}
          onChange={(e) => update("link", e.target.value)}
        />
      </div>
    </div>
  );
}

function EducationEntry({ entry, onChange, onRemove }) {
  function update(field, value) {
    onChange({ ...entry, [field]: value });
  }

  return (
    <div style={styles.card}>
      <button type="button" onClick={onRemove} style={styles.removeBtn} title="Remove">✕</button>

      <div style={styles.row2}>
        <div style={styles.field}>
          <label style={styles.label}>Institution Name</label>
          <input
            style={styles.input}
            placeholder="e.g. TU Berlin, Harvard University…"
            value={entry.institution}
            onChange={(e) => update("institution", e.target.value)}
          />
        </div>
        <div style={styles.field}>
          <label style={styles.label}>Degree / Qualification</label>
          <input
            style={styles.input}
            placeholder="e.g. M.Sc. Data Science, B.Tech CS…"
            value={entry.degree}
            onChange={(e) => update("degree", e.target.value)}
          />
        </div>
      </div>

      <div style={{ ...styles.row3, marginTop: 12 }}>
        <div style={styles.field}>
          <label style={styles.label}>From</label>
          <input
            type="month"
            style={styles.input}
            value={entry.from}
            onChange={(e) => update("from", e.target.value)}
          />
        </div>
        <div style={styles.field}>
          <label style={styles.label}>To</label>
          <input
            type="month"
            style={{ ...styles.input, opacity: entry.current ? 0.4 : 1 }}
            value={entry.to}
            disabled={entry.current}
            onChange={(e) => update("to", e.target.value)}
          />
        </div>
        <div style={styles.checkRow}>
          <input
            type="checkbox"
            id={`current-${entry.id}`}
            checked={entry.current}
            onChange={(e) => update("current", e.target.checked)}
            style={{ accentColor: "#1a1a2e", width: 15, height: 15 }}
          />
          <label htmlFor={`current-${entry.id}`} style={{ fontSize: 13, color: "#374151", cursor: "pointer" }}>
            Currently studying here
          </label>
        </div>
      </div>

      <div style={{ ...styles.field, marginTop: 12, maxWidth: 200 }}>
        <label style={styles.label}>Grade / GPA (optional)</label>
        <input
          style={styles.input}
          placeholder="e.g. 1.3, 3.8 / 4.0, First Class…"
          value={entry.gpa}
          onChange={(e) => update("gpa", e.target.value)}
        />
      </div>
    </div>
  );
}

function CertificationEntry({ entry, onChange, onRemove }) {
  function update(field, value) {
    onChange({ ...entry, [field]: value });
  }

  return (
    <div style={styles.card}>
      <button type="button" onClick={onRemove} style={styles.removeBtn} title="Remove">✕</button>
      <div style={styles.field}>
        <label style={styles.label}>Certificate Name</label>
        <input
          style={styles.input}
          placeholder="e.g. AWS Certified Solutions Architect, LLM Applications…"
          value={entry.name}
          onChange={(e) => update("name", e.target.value)}
        />
      </div>
    </div>
  );
}

const PROFICIENCY_LEVELS = ["Native", "Fluent", "Advanced (C1)", "Upper-Intermediate (B2)", "Intermediate (B1)", "Basic (A2)", "Beginner (A1)"];

function LanguageEntry({ entry, onChange, onRemove }) {
  function update(field, value) {
    onChange({ ...entry, [field]: value });
  }

  return (
    <div style={styles.card}>
      <button type="button" onClick={onRemove} style={styles.removeBtn} title="Remove">✕</button>

      <div style={styles.row2}>
        <div style={styles.field}>
          <label style={styles.label}>Language</label>
          <input
            style={styles.input}
            placeholder="e.g. English, German, Hindi…"
            value={entry.language}
            onChange={(e) => update("language", e.target.value)}
          />
        </div>
        <div style={styles.field}>
          <label style={styles.label}>Proficiency Level</label>
          <select
            style={{ ...styles.input, cursor: "pointer" }}
            value={entry.proficiency}
            onChange={(e) => update("proficiency", e.target.value)}
          >
            <option value="">Select level…</option>
            {PROFICIENCY_LEVELS.map((lvl) => (
              <option key={lvl} value={lvl}>{lvl}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

// ── main component ─────────────────────────────────────────────────────────
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
    work_authorization: "",
    visa_status: "",
    open_to_relocation: true,
    open_to_remote: true,
  });

  const [experiences, setExperiences] = useState([]);
  const [projects, setProjects] = useState([]);
  const [educations, setEducations] = useState([]);
  const [certifications, setCertifications] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [extractedLinks, setExtractedLinks] = useState([]);
  const [cvFile, setCvFile] = useState(null);

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  }

  // Experience handlers
  function addExperience() { setExperiences([...experiences, newExperience()]); }
  function updateExperience(id, updated) {
    setExperiences(experiences.map((e) => (e.id === id ? updated : e)));
  }
  function removeExperience(id) {
    setExperiences(experiences.filter((e) => e.id !== id));
  }

  // Project handlers
  function addProject() { setProjects([...projects, newProject()]); }
  function updateProject(id, updated) {
    setProjects(projects.map((p) => (p.id === id ? updated : p)));
  }
  function removeProject(id) {
    setProjects(projects.filter((p) => p.id !== id));
  }

  // Education handlers
  function addEducation() { setEducations([...educations, newEducation()]); }
  function updateEducation(id, updated) {
    setEducations(educations.map((e) => (e.id === id ? updated : e)));
  }
  function removeEducation(id) {
    setEducations(educations.filter((e) => e.id !== id));
  }

  // Certification handlers
  function addCertification() { setCertifications([...certifications, newCertification()]); }
  function updateCertification(id, updated) {
    setCertifications(certifications.map((c) => (c.id === id ? updated : c)));
  }
  function removeCertification(id) {
    setCertifications(certifications.filter((c) => c.id !== id));
  }

  // Language handlers
  function addLanguage() { setLanguages([...languages, newLanguage()]); }
  function updateLanguage(id, updated) {
    setLanguages(languages.map((l) => (l.id === id ? updated : l)));
  }
  function removeLanguage(id) {
    setLanguages(languages.filter((l) => l.id !== id));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");

    const payload = {
      ...form,
      experience: serializeExperience(experiences),
      projects: serializeProjects(projects),
      education: serializeEducation(educations),
      certifications: serializeCertifications(certifications),
      languages: serializeLanguages(languages),
    };

    try {
      const response = await api.post("/candidate-profiles", payload);
      setMessage(`Profile created successfully with ID ${response.data.id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create profile");
    }
  }

  // ── CV response → structured state parsers ──────────────────────────────

  function parseExperiencesFromText(text) {
    if (!text) return [];
    // Split on double newline or on lines that look like job title patterns
    const blocks = text.split(/\n{2,}/);
    return blocks.filter(Boolean).map((block) => {
      const lines = block.split("\n").map((l) => l.trim()).filter(Boolean);
      // Try to extract date range from first line: "Title at Company (2022-01 – Present)"
      const dateMatch = lines[0]?.match(/\(?([\d]{4}[-\/]\d{2}|[\d]{4})\s*[–-]\s*([\d]{4}[-\/]?\d{0,2}|Present|present)\)?/);
      const from = dateMatch?.[1] || "";
      const to   = dateMatch?.[2]?.toLowerCase() === "present" ? "" : (dateMatch?.[2] || "");
      const current = dateMatch?.[2]?.toLowerCase() === "present";
      // Extract title and company from "Title at Company (period)"
      const titleLine = lines[0]?.replace(/\(.*?\)/, "").replace(dateMatch?.[0] || "", "").trim();
      const atIdx = titleLine?.indexOf(" at ");
      const title   = atIdx > -1 ? titleLine.slice(0, atIdx).trim() : titleLine || "";
      const company = atIdx > -1 ? titleLine.slice(atIdx + 4).trim() : "";
      const description = lines.slice(1).join("\n");
      return { id: crypto.randomUUID(), company, title, from, to, current, description };
    });
  }

  function parseProjectsFromText(text) {
    if (!text) return [];
    const blocks = text.split(/\n{2,}/);
    return blocks.filter(Boolean).map((block) => {
      const lines = block.split("\n").map((l) => l.trim()).filter(Boolean);
      const linkLine = lines.find((l) => l.startsWith("Link:") || l.startsWith("http"));
      const link = linkLine?.replace(/^Link:\s*/, "").trim() || "";
      const title = lines[0] || "";
      const description = lines.slice(1).filter((l) => l !== linkLine).join("\n");
      return { id: crypto.randomUUID(), title, description, link };
    });
  }

  function parseEducationsFromText(text) {
    if (!text) return [];
    const blocks = text.split(/\n{2,}/);
    return blocks.filter(Boolean).map((block) => {
      const lines = block.split("\n").map((l) => l.trim()).filter(Boolean);
      // Pattern: "Degree – Institution (period) | Grade/GPA: X"
      const dateMatch = lines[0]?.match(/([\d]{4}[-\/]\d{2}|[\d]{4})\s*[–-]\s*([\d]{4}[-\/]?\d{0,2}|Present|present)/);
      const from = dateMatch?.[1] || "";
      const to   = dateMatch?.[2]?.toLowerCase() === "present" ? "" : (dateMatch?.[2] || "");
      const current = dateMatch?.[2]?.toLowerCase() === "present";
      const gpaMatch = lines[0]?.match(/Grade\/GPA:\s*([^\s|]+)/);
      const gpa = gpaMatch?.[1] || "";
      const clean = lines[0]?.replace(/\(.*?\)/, "").replace(/\|.*$/, "").trim() || "";
      const dashIdx = clean.indexOf(" – ");
      const degree      = dashIdx > -1 ? clean.slice(0, dashIdx).trim() : clean;
      const institution = dashIdx > -1 ? clean.slice(dashIdx + 3).trim() : (lines[1] || "");
      return { id: crypto.randomUUID(), institution, degree, gpa, from, to, current };
    });
  }

  function parseCertificationsFromText(text) {
    if (!text) return [];
    return text.split(/\n|·|•/)
      .map((line) => line.trim())
      .filter(Boolean)
      .map((name) => ({ id: crypto.randomUUID(), name }));
  }

  function parseLanguagesFromText(text) {
    if (!text) return [];
    // Format: "English – Native, German – Fluent" or "English (C1), German (B1)"
    return text.split(",").map((part) => {
      part = part.trim();
      const dashIdx = part.indexOf(" – ");
      if (dashIdx > -1) {
        return { id: crypto.randomUUID(), language: part.slice(0, dashIdx).trim(), proficiency: part.slice(dashIdx + 3).trim() };
      }
      // Try "(level)" pattern: "English (C1/Advanced)"
      const parenMatch = part.match(/^([^(]+)\s*\(([^)]+)\)/);
      if (parenMatch) {
        return { id: crypto.randomUUID(), language: parenMatch[1].trim(), proficiency: parenMatch[2].trim() };
      }
      return { id: crypto.randomUUID(), language: part, proficiency: "" };
    }).filter((l) => l.language);
  }

  async function handleUpload() {
    if (!cvFile) { setError("Please select a CV file to upload"); return; }
    setMessage("");
    setError("");

    try {
      const formData = new FormData();
      formData.append("cv", cvFile);

      const response = await api.post("/candidate-profiles/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const data = response.data;

      // Populate flat form fields
      setForm((prev) => ({
        ...prev,
        full_name:        data.full_name        || prev.full_name,
        email:            data.email            || prev.email,
        phone:            data.phone            || prev.phone,
        location:         data.location         || prev.location,
        linkedin_url:     data.linkedin_url     || prev.linkedin_url,
        github_url:       data.github_url       || prev.github_url,
        portfolio_url:    data.portfolio_url    || prev.portfolio_url,
        headline:         data.headline         || prev.headline,
        summary:          data.summary          || prev.summary,
        skills:           data.skills           || prev.skills,
        work_authorization: data.work_authorization || prev.work_authorization,
        visa_status:      data.visa_status      || prev.visa_status,
        open_to_relocation: data.open_to_relocation ?? prev.open_to_relocation,
        open_to_remote:   data.open_to_remote   ?? prev.open_to_remote,
      }));

      // Populate structured sections from parsed text
      if (data.experience)     setExperiences(parseExperiencesFromText(data.experience));
      if (data.projects)       setProjects(parseProjectsFromText(data.projects));
      if (data.education)      setEducations(parseEducationsFromText(data.education));
      if (data.certifications) setCertifications(parseCertificationsFromText(data.certifications));
      if (data.languages)      setLanguages(parseLanguagesFromText(data.languages));

      setExtractedLinks(data.extracted_links || []);
      setMessage(`Profile created from CV with ID ${data.id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create profile from CV");
    }
  }

  return (
    <div>
      <h1>Create Candidate Profile</h1>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "10px", maxWidth: "800px" }}>

        {/* ── CV Upload ── */}
        <div>
          <label>
            Upload CV (PDF/DOCX/TXT):
            <input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setCvFile(e.target.files?.[0] || null)} />
          </label>
          <button type="button" onClick={handleUpload} style={{ marginTop: "10px" }}>
            Create Profile from CV
          </button>
        </div>

        <hr />

        {/* ── Basic fields ── */}
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

        {/* ── Experience ── */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <span style={styles.sectionTitle}>Experience</span>
            <button type="button" onClick={addExperience} style={styles.addBtn}>+ Add Experience</button>
          </div>

          {experiences.length === 0 && (
            <p style={styles.emptyHint}>No experience added yet. Click <strong>+ Add Experience</strong> to get started.</p>
          )}

          {experiences.map((entry) => (
            <ExperienceEntry
              key={entry.id}
              entry={entry}
              onChange={(updated) => updateExperience(entry.id, updated)}
              onRemove={() => removeExperience(entry.id)}
            />
          ))}
        </div>

        {/* ── Projects ── */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <span style={styles.sectionTitle}>Projects</span>
            <button type="button" onClick={addProject} style={styles.addBtn}>+ Add Project</button>
          </div>

          {projects.length === 0 && (
            <p style={styles.emptyHint}>No projects added yet. Click <strong>+ Add Project</strong> to get started.</p>
          )}

          {projects.map((entry) => (
            <ProjectEntry
              key={entry.id}
              entry={entry}
              onChange={(updated) => updateProject(entry.id, updated)}
              onRemove={() => removeProject(entry.id)}
            />
          ))}
        </div>

        {/* ── Remaining fields ── */}
        {/* ── Education ── */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <span style={styles.sectionTitle}>Education</span>
            <button type="button" onClick={addEducation} style={styles.addBtn}>+ Add Education</button>
          </div>

          {educations.length === 0 && (
            <p style={styles.emptyHint}>No education added yet. Click <strong>+ Add Education</strong> to get started.</p>
          )}

          {educations.map((entry) => (
            <EducationEntry
              key={entry.id}
              entry={entry}
              onChange={(updated) => updateEducation(entry.id, updated)}
              onRemove={() => removeEducation(entry.id)}
            />
          ))}
        </div>
        {/* ── Certifications ── */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <span style={styles.sectionTitle}>Certifications</span>
            <button type="button" onClick={addCertification} style={styles.addBtn}>+ Add Certification</button>
          </div>

          {certifications.length === 0 && (
            <p style={styles.emptyHint}>No certifications added yet. Click <strong>+ Add Certification</strong> to get started.</p>
          )}

          {certifications.map((entry) => (
            <CertificationEntry
              key={entry.id}
              entry={entry}
              onChange={(updated) => updateCertification(entry.id, updated)}
              onRemove={() => removeCertification(entry.id)}
            />
          ))}
        </div>

        {/* ── Languages ── */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <span style={styles.sectionTitle}>Languages</span>
            <button type="button" onClick={addLanguage} style={styles.addBtn}>+ Add Language</button>
          </div>

          {languages.length === 0 && (
            <p style={styles.emptyHint}>No languages added yet. Click <strong>+ Add Language</strong> to get started.</p>
          )}

          {languages.map((entry) => (
            <LanguageEntry
              key={entry.id}
              entry={entry}
              onChange={(updated) => updateLanguage(entry.id, updated)}
              onRemove={() => removeLanguage(entry.id)}
            />
          ))}
        </div>        <input name="work_authorization" placeholder="Work authorization" value={form.work_authorization} onChange={handleChange} />
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

      {extractedLinks.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3>Extracted links (click to open)</h3>
          <ul>
            {extractedLinks.map((link) => (
              <li key={link}>
                <a href={link} target="_blank" rel="noopener noreferrer">{link}</a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {message && <p style={{ color: "green" }}>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

// ── styles ─────────────────────────────────────────────────────────────────
const styles = {
  section: {
    border: "1px solid #e5e7eb",
    borderRadius: 10,
    padding: 16,
    background: "#fafafa",
  },
  sectionHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  sectionTitle: {
    fontWeight: 600,
    fontSize: 15,
    color: "#374151",
  },
  addBtn: {
    background: "#1a1a2e",
    color: "#fff",
    border: "none",
    borderRadius: 7,
    padding: "7px 13px",
    fontSize: 13,
    fontWeight: 500,
    cursor: "pointer",
  },
  emptyHint: {
    fontSize: 13,
    color: "#9ca3af",
    textAlign: "center",
    padding: "16px 0",
  },
  card: {
    border: "1.5px solid #e5e7eb",
    borderRadius: 9,
    padding: 16,
    marginBottom: 12,
    background: "#fff",
    position: "relative",
  },
  removeBtn: {
    position: "absolute",
    top: 12,
    right: 12,
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "#9ca3af",
    fontSize: 14,
    lineHeight: 1,
  },
  row2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 12,
  },
  row3: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr 1fr",
    gap: 12,
    alignItems: "end",
  },
  checkRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    paddingBottom: 8,
  },
  field: {
    display: "flex",
    flexDirection: "column",
    gap: 5,
  },
  label: {
    fontSize: 11.5,
    fontWeight: 500,
    color: "#6b7280",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
  },
  input: {
    border: "1.5px solid #e5e7eb",
    borderRadius: 7,
    padding: "8px 11px",
    fontSize: 13.5,
    color: "#1f2937",
    background: "#fff",
    outline: "none",
    fontFamily: "inherit",
    width: "100%",
  },
};