import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getApiError } from "../services/api";
import { getPatients } from "../services/patientService";

export default function Patients() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const timeout = setTimeout(() => {
      setLoading(true);
      setError("");

      getPatients(search)
        .then(setPatients)
        .catch((err) =>
          setError(getApiError(err, "No se pudo cargar pacientes"))
        )
        .finally(() => setLoading(false));
    }, 250);

    return () => clearTimeout(timeout);
  }, [search]);

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Gestion clinica</p>
          <h2>Pacientes</h2>
        </div>
        <button className="primary-action" onClick={() => navigate("/patients/new")}>
          Nuevo paciente
        </button>
      </div>

      <article className="data-panel">
        <div className="toolbar">
          <label className="search-box">
            <span>Buscar</span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Nombre o CI"
            />
          </label>
        </div>

        {error && <div className="alert error">{error}</div>}

        {loading ? (
          <p className="empty-state">Cargando pacientes...</p>
        ) : patients.length === 0 ? (
          <p className="empty-state">No hay pacientes para mostrar.</p>
        ) : (
          <div className="patient-table">
            <div className="patient-table-head">
              <span>Paciente</span>
              <span>CI</span>
              <span>Edad</span>
              <span>Telefono</span>
            </div>
            {patients.map((patient) => (
              <button
                key={patient.id}
                className="patient-table-row"
                onClick={() => navigate(`/patients/${patient.id}`)}
              >
                <span>{patient.name}</span>
                <span>{patient.ci}</span>
                <span>{patient.age ?? "-"}</span>
                <span>{patient.phone || "-"}</span>
              </button>
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
