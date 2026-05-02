import { useEffect, useMemo, useRef, useState } from "react";

import {
  createAppointment,
  deleteAppointment,
  getAppointments,
  getGoogleCalendarAuthUrl,
  getGoogleCalendarStatus,
  syncAppointment,
} from "../services/appointmentService";
import { getApiError } from "../services/api";
import { createPatient, getPatients } from "../services/patientService";

const initialForm = {
  patient_id: "",
  title: "Consulta capilar",
  date: new Date().toISOString().slice(0, 10),
  time: "09:00",
  duration: "45",
  location: "Clinica Elara",
  reminder_value: "24",
  reminder_unit: "hours",
  reminder_method: "email",
  notes: "",
  sync_google: true,
};

const reminderUnits = {
  minutes: 1,
  hours: 60,
  days: 1440,
};

function toDateInput(value) {
  return new Date(value).toLocaleDateString("es-UY", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function buildDateTime(date, time) {
  return new Date(`${date}T${time}:00`);
}

function buildLocalIso(date, time) {
  return `${date}T${time}:00`;
}

function toLocalDatePart(value) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function toLocalTimePart(value) {
  const hours = String(value.getHours()).padStart(2, "0");
  const minutes = String(value.getMinutes()).padStart(2, "0");
  return `${hours}:${minutes}`;
}

export default function Agenda() {
  const patientSelectRef = useRef(null);
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [calendarStatus, setCalendarStatus] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [creatingPatient, setCreatingPatient] = useState(false);
  const [showQuickPatient, setShowQuickPatient] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [quickPatient, setQuickPatient] = useState({
    name: "",
    ci: "",
    email: "",
    phone: "",
  });

  const pendingSync = useMemo(
    () => appointments.filter((appointment) => !appointment.google_synced).length,
    [appointments]
  );

  const loadAgenda = async () => {
    const [appointmentData, patientData, statusData] = await Promise.all([
      getAppointments(),
      getPatients(),
      getGoogleCalendarStatus(),
    ]);
    setAppointments(appointmentData);
    setPatients(patientData);
    setCalendarStatus(statusData);
    if (patientData.length === 1) {
      setForm((current) => ({ ...current, patient_id: String(patientData[0].id) }));
    }
  };

  useEffect(() => {
    Promise.resolve()
      .then(loadAgenda)
      .catch((err) => setError(getApiError(err, "No se pudo cargar la agenda")))
      .finally(() => setLoading(false));
  }, []);

  const updateForm = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const updateQuickPatient = (field, value) => {
    setQuickPatient((current) => ({ ...current, [field]: value }));
  };

  const createQuickPatient = async () => {
    if (!quickPatient.name.trim()) {
      setError("El nombre del paciente es obligatorio");
      return;
    }
    if (!quickPatient.ci.trim()) {
      setError("La CI del paciente es obligatoria");
      return;
    }

    try {
      setCreatingPatient(true);
      setError("");
      const patient = await createPatient({
        name: quickPatient.name.trim(),
        ci: quickPatient.ci.trim(),
        email: quickPatient.email.trim() || null,
        phone: quickPatient.phone.trim() || null,
      });
      setPatients((current) => [...current, patient].sort((a, b) => a.name.localeCompare(b.name)));
      setForm((current) => ({ ...current, patient_id: String(patient.id) }));
      setQuickPatient({ name: "", ci: "", email: "", phone: "" });
      setShowQuickPatient(false);
      setNotice("Paciente creado y seleccionado para la consulta.");
    } catch (err) {
      setError(getApiError(err, "No se pudo crear el paciente"));
    } finally {
      setCreatingPatient(false);
    }
  };

  const connectGoogle = async () => {
    try {
      setError("");
      if (calendarStatus?.credentials_file === false) {
        setError("Falta project/backend/credentials.json para conectar Google Calendar");
        return;
      }
      const authUrl = await getGoogleCalendarAuthUrl();
      window.open(authUrl, "_blank", "noopener,noreferrer");
      setNotice("Autoriza Google Calendar en la ventana nueva y luego actualiza el estado.");
    } catch (err) {
      setError(getApiError(err, "No se pudo iniciar la conexion con Google"));
    }
  };

  const refreshCalendarStatus = async () => {
    try {
      setError("");
      const status = await getGoogleCalendarStatus();
      setCalendarStatus(status);
      setNotice(status.connected ? "Google Calendar conectado." : "");
    } catch (err) {
      setError(getApiError(err, "No se pudo consultar Google Calendar"));
    }
  };

  const validate = () => {
    if (!form.patient_id) return "Selecciona un paciente";
    if (!form.date || !form.time) return "Selecciona fecha y hora";
    if (Number(form.duration) <= 0) return "La duracion debe ser mayor a cero";
    if (Number(form.reminder_value) < 0) return "La antelacion no puede ser negativa";
    return "";
  };

  const submitAppointment = async (event) => {
    event.preventDefault();
    const validationError = validate();

    if (validationError) {
      setError(validationError);
      if (!form.patient_id) {
        patientSelectRef.current?.focus();
        patientSelectRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      return;
    }

    const startsAt = buildDateTime(form.date, form.time);
    const endsAt = new Date(startsAt.getTime() + Number(form.duration) * 60000);
    const reminderMinutes =
      Number(form.reminder_value) * reminderUnits[form.reminder_unit];

    try {
      setSaving(true);
      setError("");
      setNotice("");

      const appointment = await createAppointment({
        patient_id: Number(form.patient_id),
        title: form.title,
        starts_at: buildLocalIso(form.date, form.time),
        ends_at: buildLocalIso(toLocalDatePart(endsAt), toLocalTimePart(endsAt)),
        location: form.location || null,
        notes: form.notes || null,
        reminder_minutes: reminderMinutes,
        reminder_method: form.reminder_method,
        sync_google: form.sync_google,
      });

      setAppointments((current) => [...current, appointment]);
      setForm(initialForm);
      setNotice(
        appointment.sync_error
          ? `Consulta agendada localmente. Google Calendar no sincronizo: ${appointment.sync_error}`
          : appointment.google_synced
          ? "Consulta agendada y sincronizada con Google Calendar."
          : "Consulta agendada localmente. Puedes sincronizarla cuando conectes Google."
      );
    } catch (err) {
      setError(getApiError(err, "No se pudo agendar la consulta"));
      await loadAgenda();
    } finally {
      setSaving(false);
    }
  };

  const syncOne = async (id) => {
    try {
      setError("");
      const appointment = await syncAppointment(id);
      setAppointments((current) =>
        current.map((item) => (item.id === id ? appointment : item))
      );
      setNotice("Cita sincronizada con Google Calendar.");
    } catch (err) {
      setError(getApiError(err, "No se pudo sincronizar la cita"));
    }
  };

  const removeAppointment = async (id) => {
    try {
      setError("");
      await deleteAppointment(id);
      setAppointments((current) => current.filter((item) => item.id !== id));
    } catch (err) {
      setError(getApiError(err, "No se pudo eliminar la cita"));
    }
  };

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Agenda integrada</p>
          <h2>Consultas y recordatorios</h2>
        </div>
        <div className={calendarStatus?.connected ? "calendar-status ok" : "calendar-status"}>
          <strong>{calendarStatus?.connected ? "Google conectado" : "Google pendiente"}</strong>
          <span>{pendingSync} sin sincronizar</span>
        </div>
      </div>

      <article className="calendar-connect-panel">
        <div>
          <h3>Google Calendar</h3>
          <p>
            {calendarStatus?.credentials_file === false
              ? "Falta configurar credentials.json en el backend para conectar Google Calendar."
              : "Las citas se crean en tu calendario y pueden invitar al paciente por email si tiene correo cargado."}
          </p>
        </div>
        <div className="calendar-actions">
          <button className="secondary-action" type="button" onClick={refreshCalendarStatus}>
            Actualizar estado
          </button>
          <button className="primary-action" type="button" onClick={connectGoogle}>
            Conectar Google
          </button>
        </div>
      </article>

      <form className="form-panel agenda-form" onSubmit={submitAppointment}>
        <div className="agenda-patient-strip">
          <label className="field agenda-patient-field">
            <span>Paciente</span>
            <select
              ref={patientSelectRef}
              value={form.patient_id}
              onChange={(event) => updateForm("patient_id", event.target.value)}
            >
              <option value="">
                {patients.length === 0 ? "No hay pacientes cargados" : "Seleccionar paciente"}
              </option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.name} - CI {patient.ci}
                </option>
              ))}
            </select>
          </label>
          <button
            className="secondary-action"
            type="button"
            onClick={() => setShowQuickPatient((current) => !current)}
          >
            Nuevo paciente
          </button>
        </div>

        {showQuickPatient && (
          <div className="quick-patient-panel">
            <label className="field">
              <span>Nombre</span>
              <input
                value={quickPatient.name}
                onChange={(event) => updateQuickPatient("name", event.target.value)}
              />
            </label>
            <label className="field">
              <span>CI</span>
              <input
                value={quickPatient.ci}
                onChange={(event) => updateQuickPatient("ci", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Email</span>
              <input
                value={quickPatient.email}
                onChange={(event) => updateQuickPatient("email", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Telefono</span>
              <input
                value={quickPatient.phone}
                onChange={(event) => updateQuickPatient("phone", event.target.value)}
              />
            </label>
            <div className="quick-patient-actions">
              <button type="button" onClick={() => setShowQuickPatient(false)}>
                Cancelar
              </button>
              <button
                className="primary-action"
                type="button"
                onClick={createQuickPatient}
                disabled={creatingPatient}
              >
                {creatingPatient ? "Creando..." : "Crear y seleccionar"}
              </button>
            </div>
          </div>
        )}

        <div className="form-grid agenda-grid">
          <label className="field">
            <span>Motivo</span>
            <input value={form.title} onChange={(event) => updateForm("title", event.target.value)} />
          </label>
          <label className="field">
            <span>Fecha</span>
            <input type="date" value={form.date} onChange={(event) => updateForm("date", event.target.value)} />
          </label>
          <label className="field">
            <span>Hora</span>
            <input type="time" value={form.time} onChange={(event) => updateForm("time", event.target.value)} />
          </label>
          <label className="field">
            <span>Duracion</span>
            <select value={form.duration} onChange={(event) => updateForm("duration", event.target.value)}>
              <option value="30">30 minutos</option>
              <option value="45">45 minutos</option>
              <option value="60">1 hora</option>
              <option value="90">1 hora 30 minutos</option>
            </select>
          </label>
          <label className="field">
            <span>Lugar</span>
            <input value={form.location} onChange={(event) => updateForm("location", event.target.value)} />
          </label>
          <label className="field">
            <span>Recordatorio</span>
            <div className="reminder-row">
              <input
                type="number"
                min="0"
                value={form.reminder_value}
                onChange={(event) => updateForm("reminder_value", event.target.value)}
              />
              <select
                value={form.reminder_unit}
                onChange={(event) => updateForm("reminder_unit", event.target.value)}
              >
                <option value="minutes">minutos antes</option>
                <option value="hours">horas antes</option>
                <option value="days">dias antes</option>
              </select>
            </div>
          </label>
          <label className="field">
            <span>Metodo</span>
            <select
              value={form.reminder_method}
              onChange={(event) => updateForm("reminder_method", event.target.value)}
            >
              <option value="email">Email</option>
              <option value="popup">Notificacion Google</option>
            </select>
          </label>
          <label className="field wide">
            <span>Notas para la cita</span>
            <textarea rows="3" value={form.notes} onChange={(event) => updateForm("notes", event.target.value)} />
          </label>
          <label className="toggle-field">
            <input
              type="checkbox"
              checked={form.sync_google}
              onChange={(event) => updateForm("sync_google", event.target.checked)}
            />
            <span>Sincronizar con Google Calendar al guardar</span>
          </label>
        </div>

        {error && <div className="alert error">{error}</div>}
        {notice && <div className="alert success">{notice}</div>}

        <div className="form-actions">
          <button className="primary-action" type="submit" disabled={saving || patients.length === 0}>
            {saving ? "Agendando..." : "Agendar consulta"}
          </button>
        </div>
      </form>

      <article className="data-panel">
        <div className="panel-header">
          <h3>Proximas consultas</h3>
        </div>
        {loading ? (
          <p className="empty-state">Cargando agenda...</p>
        ) : appointments.length === 0 ? (
          <p className="empty-state">No hay consultas agendadas.</p>
        ) : (
          <div className="appointment-list">
            {appointments.map((appointment) => (
              <div className="appointment-row" key={appointment.id}>
                <div>
                  <strong>{appointment.patient.name}</strong>
                  <p>{appointment.title} - {toDateInput(appointment.starts_at)}</p>
                </div>
                <span className={appointment.google_synced ? "sync-pill ok" : "sync-pill"}>
                  {appointment.google_synced ? "Google" : "Local"}
                </span>
                {!appointment.google_synced && (
                  <button type="button" onClick={() => syncOne(appointment.id)}>
                    Sincronizar
                  </button>
                )}
                <button className="danger" type="button" onClick={() => removeAppointment(appointment.id)}>
                  Eliminar
                </button>
              </div>
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
