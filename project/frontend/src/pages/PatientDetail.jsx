import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../services/api";

const historySteps = [
  "Antecedentes",
  "Historia de alopecia",
  "Evaluacion general",
  "Evaluacion capilar",
  "Patron y sintomas",
  "Area a implantar",
  "Diagnostico y plan",
  "Consentimiento",
  "Observaciones",
];

const availableZones = [
  "Linea frontal",
  "Entradas",
  "Vertex",
  "Coronilla",
  "Zona media",
];

const fallbackPatient = {
  name: "Juan Perez",
  ci: "4.123.456-7",
  age: 32,
  sex: "Masculino",
  phone: "099 123 456",
  email: "juanperez@email.com",
  occupation: "Ingeniero",
  city: "Montevideo",
};

export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("frontal");
  const [zones, setZones] = useState(["Linea frontal", "Entradas"]);
  const [follicles, setFollicles] = useState("3500");
  const [notes, setNotes] = useState(
    "Alta densidad en linea frontal y entradas."
  );
  const [selectedAreas, setSelectedAreas] = useState([]);

  useEffect(() => {
    const fetchPatient = async () => {
      try {
        const res = await api.get(`/patients/${id}`);
        setPatient({ ...fallbackPatient, ...res.data });
      } catch (error) {
        console.error("Error cargando paciente", error);
        setPatient(fallbackPatient);
      } finally {
        setLoading(false);
      }
    };

    fetchPatient();
  }, [id]);

  const activeZones = useMemo(() => new Set(zones), [zones]);

  const toggleZone = (zone) => {
    setZones((current) =>
      current.includes(zone)
        ? current.filter((item) => item !== zone)
        : [...current, zone]
    );
  };

  const saveArea = () => {
    if (zones.length === 0) return;

    setSelectedAreas((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        name: zones.join(" y "),
        follicles,
        notes,
        date: "15/05/2026",
      },
    ]);
  };

  const clearArea = () => {
    setZones([]);
    setFollicles("");
    setNotes("");
  };

  if (loading) {
    return <div className="screen-state">Cargando paciente...</div>;
  }

  return (
    <div className="clinical-screen">
      <section className="patient-column">
        <button className="back-button" onClick={() => navigate("/patients")}>
          Volver a pacientes
        </button>

        <article className="patient-card">
          <div className="patient-header">
            <span className="patient-photo">JP</span>
            <div>
              <h2>{patient.name}</h2>
              <p>CI: {patient.ci}</p>
            </div>
          </div>

          <dl className="patient-data">
            <div>
              <dt>Edad</dt>
              <dd>{patient.age || "-"} anos</dd>
            </div>
            <div>
              <dt>Sexo</dt>
              <dd>{patient.sex || "-"}</dd>
            </div>
            <div>
              <dt>Telefono</dt>
              <dd>{patient.phone || "-"}</dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>{patient.email || "-"}</dd>
            </div>
            <div>
              <dt>Ocupacion</dt>
              <dd>{patient.occupation || "-"}</dd>
            </div>
            <div>
              <dt>Reside en</dt>
              <dd>{patient.city || "-"}</dd>
            </div>
          </dl>
        </article>

        <article className="patient-card compact">
          <button>Datos generales</button>
          <button className="selected">Historia clinica</button>
          <button>Evolucion fotos</button>
          <button>Procedimientos</button>
          <button>Documentos</button>
        </article>

        <article className="patient-card compact">
          <h3>Consultas anteriores</h3>
          <div className="previous-row">
            <span>10/03/2026</span>
            <strong>Control</strong>
          </div>
          <div className="previous-row">
            <span>12/02/2026</span>
            <strong>Implante</strong>
          </div>
          <div className="previous-row">
            <span>15/01/2026</span>
            <strong>Consulta inicial</strong>
          </div>
        </article>
      </section>

      <section className="history-panel">
        <div className="stepper">
          {historySteps.map((step, index) => (
            <div
              key={step}
              className={index === 5 ? "step active" : "step"}
              title={step}
            >
              <span>{index + 1}</span>
              <p>{step}</p>
            </div>
          ))}
        </div>

        <div className="implant-workspace">
          <div className="implant-main">
            <div className="section-title">
              <h2>Area a implantar</h2>
              <div className="segmented-control">
                <button
                  className={view === "frontal" ? "active" : ""}
                  onClick={() => setView("frontal")}
                >
                  Vista frontal
                </button>
                <button
                  className={view === "superior" ? "active" : ""}
                  onClick={() => setView("superior")}
                >
                  Vista superior
                </button>
              </div>
            </div>

            <div className={`scalp-board ${view}`}>
              <div className="tool-rail">
                <button className="active">Dibujar</button>
                <button>Borrar</button>
                <button>Deshacer</button>
                <button onClick={clearArea}>Limpiar</button>
              </div>

              <div className="head-model" aria-label="Mapa capilar">
                <div className="hair-shape" />
                {activeZones.has("Linea frontal") && (
                  <div className="implant-zone frontal-zone" />
                )}
                {activeZones.has("Entradas") && (
                  <>
                    <div className="implant-zone left-entry" />
                    <div className="implant-zone right-entry" />
                  </>
                )}
                {activeZones.has("Zona media") && (
                  <div className="implant-zone mid-zone" />
                )}
                {activeZones.has("Vertex") && (
                  <div className="implant-zone vertex-zone" />
                )}
                {activeZones.has("Coronilla") && (
                  <div className="implant-zone crown-zone" />
                )}
                <div className="face-shape" />
              </div>
            </div>

            <p className="hint">Dibuja el area donde se realizara el implante capilar.</p>
          </div>

          <aside className="implant-controls">
            <h3>Zonas disponibles</h3>
            <div className="check-list">
              {availableZones.map((zone) => (
                <label key={zone}>
                  <input
                    type="checkbox"
                    checked={zones.includes(zone)}
                    onChange={() => toggleZone(zone)}
                  />
                  <span>{zone}</span>
                </label>
              ))}
            </div>

            <label className="field">
              <span>Foliculos estimados</span>
              <div className="inline-input">
                <input
                  value={follicles}
                  onChange={(event) => setFollicles(event.target.value)}
                />
                <small>foliculos</small>
              </div>
            </label>

            <label className="field">
              <span>Notas</span>
              <textarea
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
                rows="5"
              />
            </label>

            <p className="info-note">Puedes dibujar multiples zonas si es necesario.</p>

            <div className="panel-actions">
              <button onClick={clearArea}>Cancelar</button>
              <button>Anterior</button>
              <button className="primary" onClick={saveArea}>
                Guardar area
              </button>
            </div>
          </aside>
        </div>
      </section>

      <section className="selected-areas">
        <h3>Areas seleccionadas</h3>
        {selectedAreas.length === 0 ? (
          <p className="empty-state">Todavia no hay areas guardadas.</p>
        ) : (
          selectedAreas.map((area, index) => (
            <article className="selected-area-card" key={area.id}>
              <div className="mini-scalp" />
              <div>
                <strong>
                  Area {index + 1} - {area.name}
                </strong>
                <p>Foliculos estimados: {area.follicles || "-"}</p>
                <p>Fecha: {area.date}</p>
              </div>
              <button
                className="danger"
                onClick={() =>
                  setSelectedAreas((current) =>
                    current.filter((item) => item.id !== area.id)
                  )
                }
              >
                Eliminar area
              </button>
            </article>
          ))
        )}
      </section>
    </div>
  );
}
