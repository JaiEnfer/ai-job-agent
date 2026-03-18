import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Jobs from "./pages/Jobs";
import Profiles from "./pages/Profiles";
import ApplicationPackages from "./pages/ApplicationPackages";

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
        <nav style={{ marginBottom: "20px", display: "flex", gap: "15px" }}>
          <Link to="/">Dashboard</Link>
          <Link to="/jobs">Jobs</Link>
          <Link to="/profiles">Profiles</Link>
          <Link to="/packages">Packages</Link>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/profiles" element={<Profiles />} />
          <Route path="/packages" element={<ApplicationPackages />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}