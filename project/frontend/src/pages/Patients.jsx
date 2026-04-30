import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";

export default function Patients() {
  const navigate = useNavigate();

  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const res = await api.get("/patients");
        setPatients(res.data);
      } catch (error) {
        console.error("Error cargando pacientes", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h1>Pacientes</h1>

        <button onClick={() => navigate("/patients/new")}>
          + Nuevo paciente
        </button>
      </div>

      <div style={{ marginTop: "20px" }}>
        {loading ? (
          <p>Cargando...</p>
        ) : patients.length === 0 ? (
          <p>No hay pacientes</p>
        ) : (
          patients.map((p) => (
            <div
              key={p.id}
              onClick={() => navigate(`/patients/${p.id}`)}
              style={{
                padding: "12px",
                borderBottom: "1px solid #1e293b",
                cursor: "pointer",
              }}
            >
              <strong>{p.name}</strong> - {p.ci}
            </div>
          ))
        )}
      </div>
    </div>
  );
}