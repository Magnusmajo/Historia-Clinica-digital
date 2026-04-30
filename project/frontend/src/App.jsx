import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./layout/MainLayout";

import Dashboard from "./pages/Dashboard";
import Patients from "./pages/Patients";
import NewPatient from "./pages/NewPatient";
import OperationalPage from "./pages/OperationalPage";
import PatientDetail from "./pages/PatientDetail.jsx";

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/patients/new" element={<NewPatient />} />
          <Route path="/patients/:id" element={<PatientDetail />} />
          <Route path="/agenda" element={<OperationalPage type="agenda" />} />
          <Route path="/consultations" element={<OperationalPage type="consultations" />} />
          <Route path="/procedures" element={<OperationalPage type="procedures" />} />
          <Route path="/evolution" element={<OperationalPage type="evolution" />} />
          <Route path="/reports" element={<OperationalPage type="reports" />} />
          <Route path="/settings" element={<OperationalPage type="settings" />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
}

export default App;
