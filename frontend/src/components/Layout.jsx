import { Link } from "react-router-dom";

export default function Layout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand">AI Job Agent</div>
          <div className="brand-subtitle">
            Germany-focused AI application workflow
          </div>
        </div>

        <div className="nav-group">
          <Link className="nav-link" to="/">Dashboard</Link>
          <Link className="nav-link" to="/jobs">Jobs</Link>
          <Link className="nav-link" to="/jobs/create">Create Job</Link>
          <Link className="nav-link" to="/profiles">Profiles</Link>
          <Link className="nav-link" to="/profiles/create">Create Profile</Link>
          <Link className="nav-link" to="/generate-package">Generate Package</Link>
          <Link className="nav-link" to="/packages">Packages</Link>
          <Link className="nav-link" to="/applications">Applications</Link>
          <Link className="nav-link" to="/applications/create">Create Application</Link>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}