import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  createConsultation,
  createImplantArea,
  deleteImplantArea,
  getClinicalNotes,
  saveClinicalNotes,
} from "../services/clinicalService";
import { getApiError } from "../services/api";
import { getPatient } from "../services/patientService";
import {
  deletePatientPhoto,
  getPatientPhotos,
  getPhotoUrl,
  uploadPatientPhoto,
} from "../services/photoService";

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

function formatDateTime(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("es-UY", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
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

function HumanScalpMap({ activeZones, view }) {
  const isSuperior = view === "superior";

  return (
    <div
      className={`clinical-scalp-map ${view}`}
      role="img"
      aria-label="Cabeza orientada al frente para planificacion capilar"
    >
      <div className="scalp-base">
        <span className="ear left" />
        <span className="ear right" />
        <span className="head-shape" />
        <span className="hair-rim" />
        <span className="hair-texture" />
        <span className="forehead" />
        <span className="brow left" />
        <span className="brow right" />
        <span className="nose" />
      </div>
      <svg className="scalp-overlay" viewBox="0 0 420 470" aria-hidden="true">
        {activeZones.has("Linea frontal") && (
          <path
            className="svg-zone zone-frontal"
            d={
              isSuperior
                ? "M92 302 C126 267 156 256 210 256 C264 256 294 267 328 302 C309 342 264 365 210 365 C156 365 111 342 92 302 Z"
                : "M101 302 C135 268 166 258 210 258 C254 258 285 268 319 302 C303 340 260 361 210 361 C160 361 117 340 101 302 Z"
            }
          />
        )}
        {activeZones.has("Entradas") && (
          <>
            <path
              className="svg-zone zone-temporal"
              d={
                isSuperior
                  ? "M70 124 C93 88 127 66 157 70 C146 145 137 220 130 300 C105 300 79 286 65 260 C62 216 61 168 70 124 Z"
                  : "M78 145 C98 109 128 90 154 94 C146 158 137 226 130 294 C105 292 82 278 70 253 C68 215 69 174 78 145 Z"
              }
            />
            <path
              className="svg-zone zone-temporal"
              d={
                isSuperior
                  ? "M350 124 C327 88 293 66 263 70 C274 145 283 220 290 300 C315 300 341 286 355 260 C358 216 359 168 350 124 Z"
                  : "M342 145 C322 109 292 90 266 94 C274 158 283 226 290 294 C315 292 338 278 350 253 C352 215 351 174 342 145 Z"
              }
            />
          </>
        )}
        {activeZones.has("Zona media") && (
          <path
            className="svg-zone zone-recipient"
            d="M155 68 C174 50 246 50 265 68 C278 132 277 206 260 258 C242 272 178 272 160 258 C143 206 142 132 155 68 Z"
          />
        )}
        {activeZones.has("Vertex") && (
          <ellipse className="svg-zone zone-vertex" cx="210" cy="119" rx="55" ry="54" />
        )}
        {activeZones.has("Coronilla") && (
          <ellipse className="svg-zone zone-crown" cx="210" cy="82" rx="70" ry="44" />
        )}
      </svg>
      <span className="map-caption">
        {isSuperior ? "Rostro hacia el frente" : "Referencia frontal"}
      </span>
    </div>
  );
}

export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [view, setView] = useState("superior");
  const [activeSection, setActiveSection] = useState("Historia clinica");
  const [activeStep, setActiveStep] = useState(5);
  const [zones, setZones] = useState(["Linea frontal", "Entradas", "Zona media"]);
  const [follicles, setFollicles] = useState("3500");
  const [notes, setNotes] = useState(
    "Alta densidad en linea frontal y entradas."
  );
  const [clinicalNotes, setClinicalNotes] = useState({});
  const [clinicalLoaded, setClinicalLoaded] = useState(false);
  const [clinicalDirty, setClinicalDirty] = useState(false);
  const [savingClinical, setSavingClinical] = useState(false);
  const [photos, setPhotos] = useState([]);
  const [uploadingPhotos, setUploadingPhotos] = useState(false);
  const [photoForm, setPhotoForm] = useState({
    view: "Frontal",
    takenAt: new Date().toISOString().slice(0, 10),
    notes: "",
  });

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

  const loadPhotos = useCallback(async () => {
    try {
      const data = await getPatientPhotos(id);
      setPhotos(data);
    } catch (err) {
      setError(getApiError(err, "No se pudieron cargar las fotos"));
    }
  }, [id]);

  useEffect(() => {
    Promise.resolve().then(loadPhotos);
  }, [loadPhotos]);

  useEffect(() => {
    Promise.resolve().then(() => setClinicalLoaded(false));
    getClinicalNotes(id)
      .then((data) => {
        setClinicalNotes(data);
        setClinicalDirty(false);
        setClinicalLoaded(true);
      })
      .catch((err) => {
        setError(getApiError(err, "No se pudo cargar la historia clinica"));
        setClinicalLoaded(true);
      });
  }, [id]);

  useEffect(() => {
    if (!clinicalLoaded || !clinicalDirty) return undefined;

    const timeout = setTimeout(() => {
      setSavingClinical(true);
      saveClinicalNotes(id, clinicalNotes)
        .then(() => setClinicalDirty(false))
        .catch((err) => {
          setClinicalDirty(true);
          setError(getApiError(err, "No se pudo guardar la historia clinica"));
        })
        .finally(() => {
          setSavingClinical(false);
        });
    }, 600);

    return () => {
      clearTimeout(timeout);
      setSavingClinical(false);
    };
  }, [clinicalDirty, clinicalLoaded, clinicalNotes, id]);

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
    setClinicalDirty(true);
    setClinicalNotes((current) => {
      return {
        ...current,
        [step]: {
          ...(current[step] || {}),
          [field]: value,
        },
      };
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

  const updatePhotoForm = (field, value) => {
    setPhotoForm((current) => ({ ...current, [field]: value }));
  };

  const uploadPhotos = async (event) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    try {
      setUploadingPhotos(true);
      setError("");
      const uploaded = [];

      for (const file of files) {
        const photo = await uploadPatientPhoto(id, {
          file,
          view: photoForm.view,
          notes: photoForm.notes,
          takenAt: photoForm.takenAt ? `${photoForm.takenAt}T00:00:00` : "",
        });
        uploaded.push(photo);
      }

      setPhotos((current) => [...uploaded, ...current]);
      setPhotoForm((current) => ({ ...current, notes: "" }));
    } catch (err) {
      setError(getApiError(err, "No se pudieron subir las fotos"));
    } finally {
      setUploadingPhotos(false);
      event.target.value = "";
    }
  };

  const removePhoto = async (photoId) => {
    try {
      setError("");
      await deletePatientPhoto(id, photoId);
      setPhotos((current) => current.filter((photo) => photo.id !== photoId));
    } catch (err) {
      setError(getApiError(err, "No se pudo eliminar la foto"));
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
                <div className="photo-upload-panel">
                  <label className="field">
                    <span>Vista</span>
                    <select
                      value={photoForm.view}
                      onChange={(event) => updatePhotoForm("view", event.target.value)}
                    >
                      <option>Frontal</option>
                      <option>Superior</option>
                      <option>Temporal izquierda</option>
                      <option>Temporal derecha</option>
                      <option>Posterior</option>
                      <option>Otra</option>
                    </select>
                  </label>
                  <label className="field">
                    <span>Fecha</span>
                    <input
                      type="date"
                      value={photoForm.takenAt}
                      onChange={(event) => updatePhotoForm("takenAt", event.target.value)}
                    />
                  </label>
                  <label className="field wide">
                    <span>Notas</span>
                    <textarea
                      rows="3"
                      value={photoForm.notes}
                      onChange={(event) => updatePhotoForm("notes", event.target.value)}
                    />
                  </label>
                  <label className="photo-dropzone">
                    <input
                      type="file"
                      accept="image/png,image/jpeg,image/webp"
                      multiple
                      onChange={uploadPhotos}
                      disabled={uploadingPhotos}
                    />
                    <strong>{uploadingPhotos ? "Subiendo fotos..." : "Agregar fotos"}</strong>
                    <span>Selecciona una o varias imagenes JPG, PNG o WebP</span>
                  </label>
                </div>

                {photos.length === 0 ? (
                  <p className="empty-state">Todavia no hay fotos de evolucion cargadas.</p>
                ) : (
                  <div className="photo-gallery">
                    {photos.map((photo) => (
                      <article className="photo-card" key={photo.id}>
                        <img src={getPhotoUrl(photo.url)} alt={photo.view || "Foto de evolucion"} />
                        <div>
                          <strong>{photo.view || "Foto clinica"}</strong>
                          <span>{formatDateTime(photo.taken_at || photo.created_at)}</span>
                          {photo.notes && <p>{photo.notes}</p>}
                        </div>
                        <button className="danger" onClick={() => removePhoto(photo.id)}>
                          Eliminar
                        </button>
                      </article>
                    ))}
                  </div>
                )}
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
            <p className="hint">
              {savingClinical
                ? "Guardando historia clinica..."
                : "Los datos se guardan automaticamente en la ficha del paciente."}
            </p>
          </div>
        )}

        {activeSection === "Historia clinica" && activeStep === 5 && (
        <div className="implant-workspace">
          <div className="implant-main">
            <div className="section-title">
              <h2>Area a implantar</h2>
              <div className="segmented-control">
                <button
                  className={view === "superior" ? "active" : ""}
                  onClick={() => setView("superior")}
                >
                  Vista superior
                </button>
                <button
                  className={view === "frontal" ? "active" : ""}
                  onClick={() => setView("frontal")}
                >
                  Referencia frontal
                </button>
              </div>
            </div>

            <div className={`scalp-board ${view}`}>
              <div className="tool-rail">
                <button className="active">Dibujar</button>
                <button onClick={() => setZones((current) => current.slice(0, -1))}>
                  Borrar
                </button>
                <button onClick={() => setZones(["Linea frontal", "Entradas", "Zona media"])}>
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
