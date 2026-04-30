import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  createConsultation,
  createImplantArea,
  deleteImplantArea,
} from "../services/clinicalService";
import { getApiError } from "../services/api";
import { getPatient } from "../services/patientService";

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

function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("es-UY").format(new Date(value));
}

function initials(name = "") {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [view, setView] = useState("frontal");
  const [zones, setZones] = useState(["Linea frontal", "Entradas"]);
  const [follicles, setFollicles] = useState("3500");
  const [notes, setNotes] = useState(
    "Alta densidad en linea frontal y entradas."
  );

  const loadPatient = useCallback(async () => {
    try {
      const data = await getPatient(id);
      setPatient(data);
      setError("");
    } catch (err) {
      setError(getApiError(err, "No se pudo cargar el paciente"));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    Promise.resolve().then(loadPatient);
  }, [loadPatient]);

  const activeZones = useMemo(() => new Set(zones), [zones]);
  const consultations = useMemo(
    () => patient?.consultations || [],
    [patient?.consultations]
  );
  const selectedAreas = useMemo(
    () =>
      consultations.flatMap((consultation) =>
        (consultation.implant_areas || []).map((area) => ({
          ...area,
          consultationDate: consultation.date,
        }))
      ),
    [consultations]
  );

  const toggleZone = (zone) => {
    setZones((current) =>
      current.includes(zone)
        ? current.filter((item) => item !== zone)
        : [...current, zone]
    );
  };

  const clearArea = () => {
    setZones([]);
    setFollicles("");
    setNotes("");
  };

  const saveArea = async () => {
    if (zones.length === 0) {
      setError("Selecciona al menos una zona");
      return;
    }

    const grafts = Number(follicles);
    if (!Number.isFinite(grafts) || grafts < 0) {
      setError("Los foliculos estimados deben ser un numero valido");
      return;
    }

    try {
      setSaving(true);
      setError("");

      const consultation =
        consultations[0] || (await createConsultation(Number(id)));

      await createImplantArea({
        consultationId: consultation.id,
        grafts,
        drawingData: {
          view,
          zones,
          notes,
          created_at: new Date().toISOString(),
        },
      });

      await loadPatient();
    } catch (err) {
      setError(getApiError(err, "No se pudo guardar el area"));
    } finally {
      setSaving(false);
    }
  };

  const removeArea = async (areaId) => {
    try {
      setError("");
      await deleteImplantArea(areaId);
      await loadPatient();
    } catch (err) {
      setError(getApiError(err, "No se pudo eliminar el area"));
    }
  };

  if (loading && !patient) {
    return <div className="screen-state">Cargando paciente...</div>;
  }

  if (!patient) {
    return (
      <div className="screen-state">
        <div>
          <p>{error || "Paciente no encontrado"}</p>
          <button className="secondary-action" onClick={() => navigate("/patients")}>
            Volver a pacientes
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="clinical-screen">
      <section className="patient-column">
        <button className="back-button" onClick={() => navigate("/patients")}>
          Volver a pacientes
        </button>

        <article className="patient-card">
          <div className="patient-header">
            <span className="patient-photo">{initials(patient.name)}</span>
            <div>
              <h2>{patient.name}</h2>
              <p>CI: {patient.ci}</p>
            </div>
          </div>

          <dl className="patient-data">
            <div>
              <dt>Edad</dt>
              <dd>{patient.age ?? "-"} anos</dd>
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
          {consultations.length === 0 ? (
            <p className="empty-state">Sin consultas registradas.</p>
          ) : (
            consultations.map((consultation) => (
              <div className="previous-row" key={consultation.id}>
                <span>{formatDate(consultation.date)}</span>
                <strong>Consulta #{consultation.id}</strong>
              </div>
            ))
          )}
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

        {error && <div className="alert error in-panel">{error}</div>}

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
                <button onClick={() => setZones((current) => current.slice(0, -1))}>
                  Borrar
                </button>
                <button onClick={() => setZones(["Linea frontal", "Entradas"])}>
                  Deshacer
                </button>
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

            <p className="hint">
              Dibuja el area donde se realizara el implante capilar.
            </p>
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

            <p className="info-note">
              Puedes dibujar multiples zonas si es necesario.
            </p>

            <div className="panel-actions">
              <button onClick={clearArea}>Cancelar</button>
              <button>Anterior</button>
              <button className="primary" onClick={saveArea} disabled={saving}>
                {saving ? "Guardando..." : "Guardar area"}
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
                  Area {index + 1} -{" "}
                  {(area.drawing_data?.zones || []).join(" y ") || "Sin zonas"}
                </strong>
                <p>Foliculos estimados: {area.grafts || "-"}</p>
                <p>Fecha: {formatDate(area.consultationDate)}</p>
                {area.drawing_data?.notes && <p>{area.drawing_data.notes}</p>}
              </div>
              <button className="danger" onClick={() => removeArea(area.id)}>
                Eliminar area
              </button>
            </article>
          ))
        )}
      </section>
    </div>
  );
}
