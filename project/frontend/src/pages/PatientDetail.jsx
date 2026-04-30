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

const clinicalDefaults = {
  0: {
    title: "Antecedentes",
    fields: {
      "Antecedentes familiares": "",
      "Antecedentes medicos": "",
      Medicacion: "",
      Alergias: "",
    },
  },
  1: {
    title: "Historia de alopecia",
    fields: {
      "Inicio de caida": "",
      "Evolucion temporal": "",
      "Tratamientos previos": "",
      "Respuesta observada": "",
    },
  },
  2: {
    title: "Evaluacion general",
    fields: {
      "Estado general": "",
      "Habitos relevantes": "",
      "Contraindicaciones": "",
      "Observaciones generales": "",
    },
  },
  3: {
    title: "Evaluacion capilar",
    fields: {
      "Densidad donante": "",
      "Calibre del pelo": "",
      "Elasticidad del cuero cabelludo": "",
      "Miniaturizacion": "",
    },
  },
  4: {
    title: "Patron y sintomas",
    fields: {
      "Patron de alopecia": "",
      Sintomas: "",
      "Grado Norwood/Ludwig": "",
      "Prioridad estetica": "",
    },
  },
  6: {
    title: "Diagnostico y plan",
    fields: {
      Diagnostico: "",
      "Plan terapeutico": "",
      "Cantidad estimada de sesiones": "",
      "Indicaciones": "",
    },
  },
  7: {
    title: "Consentimiento",
    fields: {
      "Consentimiento informado": "Pendiente",
      "Riesgos explicados": "",
      "Expectativas conversadas": "",
      "Firma/validacion": "",
    },
  },
  8: {
    title: "Observaciones",
    fields: {
      "Notas internas": "",
      "Proximo control": "",
      "Alertas clinicas": "",
      "Resumen final": "",
    },
  },
};

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

function getStoredClinicalNotes(patientId) {
  try {
    return JSON.parse(localStorage.getItem(`elara:clinical:${patientId}`)) || {};
  } catch {
    return {};
  }
}

function HumanScalpMap({ activeZones, view }) {
  const isSuperior = view === "superior";

  return (
    <svg
      className={`human-scalp ${view}`}
      viewBox="0 0 420 470"
      role="img"
      aria-label="Cabeza humana para planificacion capilar"
    >
      <defs>
        <linearGradient id="skinTone" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#f3c5a8" />
          <stop offset="100%" stopColor="#d59a7d" />
        </linearGradient>
        <radialGradient id="hairTexture" cx="50%" cy="35%" r="65%">
          <stop offset="0%" stopColor="#5b4032" />
          <stop offset="55%" stopColor="#3b2a22" />
          <stop offset="100%" stopColor="#211713" />
        </radialGradient>
        <pattern id="follicles" width="18" height="18" patternUnits="userSpaceOnUse">
          <circle cx="4" cy="5" r="1.5" fill="#6f4b3a" opacity="0.45" />
          <circle cx="13" cy="10" r="1.2" fill="#2a1d18" opacity="0.35" />
          <circle cx="8" cy="15" r="1" fill="#8b6350" opacity="0.32" />
        </pattern>
      </defs>

      <rect width="420" height="470" rx="18" fill="#fbfdff" />
      {isSuperior ? (
        <>
          <ellipse cx="210" cy="230" rx="132" ry="170" fill="url(#skinTone)" />
          <ellipse cx="210" cy="205" rx="146" ry="176" fill="url(#hairTexture)" />
          <ellipse cx="210" cy="205" rx="146" ry="176" fill="url(#follicles)" opacity="0.55" />
          <ellipse cx="210" cy="390" rx="52" ry="26" fill="#d39173" opacity="0.4" />
        </>
      ) : (
        <>
          <path
            d="M92 215 C88 118 135 52 210 52 C285 52 332 118 328 215 C326 322 280 414 210 414 C140 414 94 322 92 215 Z"
            fill="url(#skinTone)"
          />
          <path
            d="M96 191 C91 101 144 42 210 42 C276 42 329 101 324 191 C291 164 256 150 210 150 C164 150 129 164 96 191 Z"
            fill="url(#hairTexture)"
          />
          <path
            d="M96 191 C91 101 144 42 210 42 C276 42 329 101 324 191 C291 164 256 150 210 150 C164 150 129 164 96 191 Z"
            fill="url(#follicles)"
            opacity="0.5"
          />
          <path d="M154 283 C184 302 235 302 266 283" fill="none" stroke="#9f6f5c" strokeWidth="5" strokeLinecap="round" opacity="0.55" />
          <ellipse cx="155" cy="222" rx="13" ry="8" fill="#573a2d" opacity="0.55" />
          <ellipse cx="265" cy="222" rx="13" ry="8" fill="#573a2d" opacity="0.55" />
          <path d="M204 226 C196 258 198 274 210 278 C222 274 224 258 216 226" fill="#cd9277" opacity="0.55" />
        </>
      )}

      {activeZones.has("Linea frontal") && (
        <path
          className="svg-zone"
          d={isSuperior
            ? "M105 270 C132 232 171 214 210 214 C249 214 288 232 315 270 C294 308 252 330 210 330 C168 330 126 308 105 270 Z"
            : "M103 187 C136 158 172 145 210 145 C248 145 284 158 317 187 C306 223 265 242 210 242 C155 242 114 223 103 187 Z"}
        />
      )}
      {activeZones.has("Entradas") && (
        <>
          <path
            className="svg-zone"
            d={isSuperior
              ? "M80 183 C99 145 127 125 153 130 C146 171 128 206 98 229 C87 219 80 202 80 183 Z"
              : "M98 147 C122 116 151 105 172 122 C160 155 143 181 111 195 C101 183 96 166 98 147 Z"}
          />
          <path
            className="svg-zone"
            d={isSuperior
              ? "M340 183 C321 145 293 125 267 130 C274 171 292 206 322 229 C333 219 340 202 340 183 Z"
              : "M322 147 C298 116 269 105 248 122 C260 155 277 181 309 195 C319 183 324 166 322 147 Z"}
          />
        </>
      )}
      {activeZones.has("Zona media") && (
        <ellipse className="svg-zone" cx="210" cy={isSuperior ? "205" : "112"} rx="74" ry="58" />
      )}
      {activeZones.has("Vertex") && (
        <ellipse className="svg-zone" cx="210" cy={isSuperior ? "150" : "85"} rx="52" ry="42" />
      )}
      {activeZones.has("Coronilla") && (
        <ellipse className="svg-zone" cx="210" cy={isSuperior ? "112" : "72"} rx="70" ry="52" />
      )}

      <text x="210" y="444" textAnchor="middle" className="map-caption">
        {isSuperior ? "Vista superior" : "Vista frontal"}
      </text>
    </svg>
  );
}

export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [view, setView] = useState("frontal");
  const [activeSection, setActiveSection] = useState("Historia clinica");
  const [activeStep, setActiveStep] = useState(5);
  const [zones, setZones] = useState(["Linea frontal", "Entradas"]);
  const [follicles, setFollicles] = useState("3500");
  const [notes, setNotes] = useState(
    "Alta densidad en linea frontal y entradas."
  );
  const [clinicalNotes, setClinicalNotes] = useState(() =>
    getStoredClinicalNotes(id)
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

  const updateClinicalField = (step, field, value) => {
    setClinicalNotes((current) => {
      const next = {
        ...current,
        [step]: {
          ...(current[step] || {}),
          [field]: value,
        },
      };
      localStorage.setItem(`elara:clinical:${id}`, JSON.stringify(next));
      return next;
    });
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
          {[
            "Datos generales",
            "Historia clinica",
            "Evolucion fotos",
            "Procedimientos",
            "Documentos",
          ].map((section) => (
            <button
              key={section}
              className={activeSection === section ? "selected" : ""}
              onClick={() => setActiveSection(section)}
            >
              {section}
            </button>
          ))}
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
        {activeSection === "Historia clinica" && (
          <div className="stepper">
            {historySteps.map((step, index) => (
              <button
                key={step}
                className={index === activeStep ? "step active" : "step"}
                title={step}
                onClick={() => setActiveStep(index)}
              >
                <span>{index + 1}</span>
                <p>{step}</p>
              </button>
            ))}
          </div>
        )}

        {error && <div className="alert error in-panel">{error}</div>}

        {activeSection !== "Historia clinica" && (
          <div className="clinical-tab-panel">
            {activeSection === "Datos generales" && (
              <>
                <h2>Datos generales</h2>
                <div className="read-grid">
                  <span>Nombre</span><strong>{patient.name}</strong>
                  <span>CI</span><strong>{patient.ci}</strong>
                  <span>Telefono</span><strong>{patient.phone || "-"}</strong>
                  <span>Email</span><strong>{patient.email || "-"}</strong>
                  <span>Ocupacion</span><strong>{patient.occupation || "-"}</strong>
                  <span>Residencia</span><strong>{patient.city || "-"}</strong>
                </div>
              </>
            )}
            {activeSection === "Evolucion fotos" && (
              <>
                <h2>Evolucion fotos</h2>
                <div className="media-grid">
                  <div className="upload-slot">Frontal</div>
                  <div className="upload-slot">Superior</div>
                  <div className="upload-slot">Temporal izquierda</div>
                  <div className="upload-slot">Temporal derecha</div>
                </div>
              </>
            )}
            {activeSection === "Procedimientos" && (
              <>
                <h2>Procedimientos</h2>
                <div className="procedure-summary">
                  <strong>{selectedAreas.length}</strong>
                  <span>areas planificadas</span>
                  <strong>{selectedAreas.reduce((sum, area) => sum + (area.grafts || 0), 0)}</strong>
                  <span>foliculos estimados</span>
                </div>
              </>
            )}
            {activeSection === "Documentos" && (
              <>
                <h2>Documentos</h2>
                <div className="document-list">
                  <div><strong>Consentimiento informado</strong><span>Pendiente</span></div>
                  <div><strong>Plan quirurgico</strong><span>Generado desde areas guardadas</span></div>
                  <div><strong>Ficha clinica</strong><span>Disponible en sistema</span></div>
                </div>
              </>
            )}
          </div>
        )}

        {activeSection === "Historia clinica" && activeStep !== 5 && (
          <div className="clinical-form-panel">
            <h2>{clinicalDefaults[activeStep].title}</h2>
            <div className="form-grid">
              {Object.keys(clinicalDefaults[activeStep].fields).map((field) => (
                <label className="field" key={field}>
                  <span>{field}</span>
                  <textarea
                    rows="4"
                    value={
                      clinicalNotes[activeStep]?.[field] ??
                      clinicalDefaults[activeStep].fields[field]
                    }
                    onChange={(event) =>
                      updateClinicalField(activeStep, field, event.target.value)
                    }
                  />
                </label>
              ))}
            </div>
            <p className="hint">Los datos se guardan automaticamente en esta estacion local.</p>
          </div>
        )}

        {activeSection === "Historia clinica" && activeStep === 5 && (
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

              <HumanScalpMap activeZones={activeZones} view={view} />
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
        )}
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
