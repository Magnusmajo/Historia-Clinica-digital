import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../services/api";

export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPatient = async () => {
      try {
        const res = await api.get(`/patients/${id}`);
        setPatient(res.data);
      } catch (error) {
        console.error("Error cargando paciente", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPatient();
  }, [id]);

  if (loading) return <p style={{ padding: "20px" }}>Cargando...</p>;

  if (!patient) return <p style={{ padding: "20px" }}>Paciente no encontrado</p>;

  return (
    <div style={{ padding: "20px" }}>
      {/* HEADER */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: "20px",
        }}
      >
        <div>
          <h1>{patient.name}</h1>
          <p>CI: {patient.ci}</p>
        </div>

        <button onClick={() => navigate("/patients")}>
          ← Volver
        </button>
      </div>

      {/* INFO GENERAL */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 2fr",
          gap: "20px",
        }}
      >
        {/* CARD IZQUIERDA */}
        <div
          style={{
            background: "#0f172a",
            padding: "20px",
            borderRadius: "8px",
          }}
        >
          <h3>Datos del paciente</h3>

          <p><strong>Edad:</strong> {patient.age || "-"}</p>
          <p><strong>Sexo:</strong> {patient.sex || "-"}</p>
          <p><strong>Teléfono:</strong> {patient.phone || "-"}</p>
        </div>

        {/* CARD DERECHA */}
        <div
          style={{
            background: "#0f172a",
            padding: "20px",
            borderRadius: "8px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "10px",
            }}
          >
            <h3>Consultas</h3>

            <button
              onClick={() => navigate(`/consultations/new/${patient.id}`)}
            >
              + Nueva consulta
            </button>
          </div>

          {patient.consultations && patient.consultations.length > 0 ? (
            patient.consultations.map((c) => (
              <div
                key={c.id}
                style={{
                  padding: "10px",
                  borderBottom: "1px solid #1e293b",
                }}
              >
                Consulta #{c.id} —{" "}
                {new Date(c.date).toLocaleDateString()}
              </div>
            ))
          ) : (
            <p>No hay consultas</p>
          )}
        </div>
      </div>
    </div>
  );
}