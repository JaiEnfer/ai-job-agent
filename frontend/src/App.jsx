import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Jobs from "./pages/Jobs";
import Profiles from "./pages/Profiles";
import ApplicationPackages from "./pages/ApplicationPackages";
import CreateJob from "./pages/CreateJob";
import CreateProfile from "./pages/CreateProfile";
import GeneratePackage from "./pages/GeneratePackage";
import Applications from "./pages/Applications";
import PackageDetail from "./pages/PackageDetail";
import CreateApplication from "./pages/CreateApplication";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
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
          <Route path="/applications/create" element={<CreateApplication />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}