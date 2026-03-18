import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Jobs from "./pages/Jobs";
import Profiles from "./pages/Profiles";
import ApplicationPackages from "./pages/ApplicationPackages";
import CreateJob from "./pages/CreateJob";
import CreateProfile from "./pages/CreateProfile";
import GeneratePackage from "./pages/GeneratePackage";
import Applications from "./pages/Applications";
import PackageDetail from "./pages/PackageDetail";

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
        <h1>AI Job Application Agent</h1>

        <nav style={{ marginBottom: "20px", display: "flex", gap: "15px", flexWrap: "wrap" }}>
          <Link to="/">Dashboard</Link>
          <Link to="/jobs">Jobs</Link>
          <Link to="/jobs/create">Create Job</Link>
          <Link to="/profiles">Profiles</Link>
          <Link to="/profiles/create">Create Profile</Link>
          <Link to="/generate-package">Generate Package</Link>
          <Link to="/packages">Packages</Link>
          <Link to="/applications">Applications</Link>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/jobs/create" element={<CreateJob />} />
          <Route path="/profiles" element={<Profiles />} />
          <Route path="/profiles/create" element={<CreateProfile />} />
          <Route path="/generate-package" element={<GeneratePackage />} />
          <Route path="/packages" element={<ApplicationPackages />} />
          <Route path="/packages/:id" element={<PackageDetail />} />
          <Route path="/applications" element={<Applications />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}