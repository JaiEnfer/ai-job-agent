import { useState } from "react";
import api from "../services/api";

export default function JobChat() {
  const [jobFile, setJobFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!jobFile) {
      setError("Please upload a job description file first.");
      return;
    }

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("job_file", jobFile);
      formData.append("question", question);

      const res = await api.post("/job-chat", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setResponse(res.data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to get response.");
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="stack">
      <div className="page-header">
        <h1 className="page-title">Job Description Chat</h1>
        <p className="page-subtitle">
          Upload a job description file and ask a question about it, like Claude AI.
        </p>
      </div>

      <form className="card form-grid" onSubmit={handleSubmit}>
        <label>
          Job description file (PDF / DOCX / TXT):
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => setJobFile(e.target.files?.[0] || null)}
          />
        </label>

        <label>
          Your question:
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            placeholder="e.g. What are the key responsibilities?"
          />
        </label>

        <button type="submit" className="button" disabled={loading}>
          {loading ? "Thinking…" : "Ask"}
        </button>

        {error && <div className="message-error">{error}</div>}
      </form>

      {response && (
        <div className="card">
          <h2 className="section-title">AI Response</h2>
          <div className="pre-block">{response.answer}</div>

          <h2 className="section-title">Extracted Job Text</h2>
          <div className="pre-block">{response.job_text}</div>
        </div>
      )}
    </div>
  );
}
