import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import MainLayout from "./layout/MainLayout";

import Dashboard from "./pages/Dashboard";
import Agenda from "./pages/Agenda";
import AuditLogs from "./pages/AuditLogs";
import Patients from "./pages/Patients";
import NewPatient from "./pages/NewPatient";
import Login from "./pages/Login";
import OperationalPage from "./pages/OperationalPage";
import PatientDetail from "./pages/PatientDetail.jsx";
import Users from "./pages/Users";

function ProtectedShell() {
  const location = useLocation();
  const { loading, isAuthenticated, user } = useAuth();

  if (loading) {
    return <div className="screen-state">Cargando sesion...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/patients" element={<Patients />} />
        <Route path="/patients/new" element={<NewPatient />} />
        <Route path="/patients/:id" element={<PatientDetail />} />
        <Route path="/agenda" element={<Agenda />} />
        <Route path="/consultations" element={<OperationalPage type="consultations" />} />
        <Route path="/procedures" element={<OperationalPage type="procedures" />} />
        <Route path="/evolution" element={<OperationalPage type="evolution" />} />
        <Route path="/reports" element={<OperationalPage type="reports" />} />
        <Route path="/settings" element={<OperationalPage type="settings" />} />
        {user?.role === "admin" && <Route path="/users" element={<Users />} />}
        {user?.role === "admin" && <Route path="/audit" element={<AuditLogs />} />}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </MainLayout>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<ProtectedShell />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
