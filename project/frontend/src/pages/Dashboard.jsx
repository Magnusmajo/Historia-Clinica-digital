import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getApiError } from "../services/api";
import { getPatients } from "../services/patientService";
import { getSummary } from "../services/statsService";

export default function Dashboard() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState({
    patients: 0,
    appointments: 0,
    consultations: 0,
    implant_areas: 0,
    module_records: 0,
  });

  useEffect(() => {
    Promise.all([getPatients(), getSummary()])
      .then(([patientData, summaryData]) => {
        setPatients(patientData);
        setSummary(summaryData);
      })
      .catch((err) => setError(getApiError(err, "No se pudo cargar el panel")))
      .finally(() => setLoading(false));
  }, []);

  const recentPatients = useMemo(() => patients.slice(0, 5), [patients]);

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Resumen operativo</p>
          <h2>Dashboard</h2>
        </div>
        <button className="primary-action" onClick={() => navigate("/patients/new")}>
          Nuevo paciente
        </button>
      </div>

      {error && <div className="alert error">{error}</div>}

      <div className="metric-grid">
        <article className="metric-card">
          <span>Pacientes activos</span>
          <strong>{loading ? "..." : summary.patients}</strong>
        </article>
        <article className="metric-card">
          <span>Consultas agendadas</span>
          <strong>{loading ? "..." : summary.appointments}</strong>
        </article>
        <article className="metric-card">
          <span>Consultas registradas</span>
          <strong>{loading ? "..." : summary.consultations}</strong>
        </article>
        <article className="metric-card">
          <span>Areas planificadas</span>
          <strong>{loading ? "..." : summary.implant_areas}</strong>
        </article>
        <article className="metric-card">
          <span>Registros operativos</span>
          <strong>{loading ? "..." : summary.module_records}</strong>
        </article>
      </div>

      <article className="data-panel">
        <div className="panel-header">
          <h3>Pacientes recientes</h3>
          <button onClick={() => navigate("/patients")}>Ver todos</button>
        </div>

        {loading ? (
          <p className="empty-state">Cargando pacientes...</p>
        ) : recentPatients.length === 0 ? (
          <p className="empty-state">Todavia no hay pacientes cargados.</p>
        ) : (
          <div className="table-list">
            {recentPatients.map((patient) => (
              <button
                key={patient.id}
                className="table-row"
                onClick={() => navigate(`/patients/${patient.id}`)}
              >
                <span>{patient.name}</span>
                <span>{patient.ci}</span>
                <span>{patient.phone || "-"}</span>
              </button>
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
