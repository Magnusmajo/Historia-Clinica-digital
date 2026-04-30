import { useEffect, useMemo, useState } from "react";

import { getApiError } from "../services/api";
import {
  createModuleRecord,
  deleteModuleRecord,
  getModuleRecords,
} from "../services/moduleService";

const pageCopy = {
  agenda: {
    eyebrow: "Planificacion diaria",
    title: "Agenda",
    empty: "No hay eventos agendados.",
    action: "Agregar evento",
    fields: ["Fecha", "Paciente", "Motivo", "Estado"],
    defaults: {
      Fecha: new Date().toISOString().slice(0, 10),
      Paciente: "",
      Motivo: "Consulta capilar",
      Estado: "Pendiente",
    },
  },
  consultations: {
    eyebrow: "Atencion clinica",
    title: "Consultas",
    empty: "No hay consultas manuales registradas.",
    action: "Registrar consulta",
    fields: ["Fecha", "Paciente", "Resumen", "Profesional"],
    defaults: {
      Fecha: new Date().toISOString().slice(0, 10),
      Paciente: "",
      Resumen: "",
      Profesional: "Dr. Alexis Rodriguez",
    },
  },
  procedures: {
    eyebrow: "Actividad quirurgica",
    title: "Procedimientos",
    empty: "No hay procedimientos cargados.",
    action: "Agregar procedimiento",
    fields: ["Fecha", "Paciente", "Procedimiento", "Estado"],
    defaults: {
      Fecha: new Date().toISOString().slice(0, 10),
      Paciente: "",
      Procedimiento: "Implante capilar",
      Estado: "Planificado",
    },
  },
  evolution: {
    eyebrow: "Seguimiento",
    title: "Evolucion",
    empty: "No hay controles de evolucion.",
    action: "Agregar control",
    fields: ["Fecha", "Paciente", "Control", "Notas"],
    defaults: {
      Fecha: new Date().toISOString().slice(0, 10),
      Paciente: "",
      Control: "Seguimiento",
      Notas: "",
    },
  },
  reports: {
    eyebrow: "Indicadores",
    title: "Reportes",
    empty: "No hay reportes guardados.",
    action: "Guardar reporte",
    fields: ["Periodo", "Indicador", "Resultado", "Notas"],
    defaults: {
      Periodo: new Date().toISOString().slice(0, 7),
      Indicador: "Pacientes activos",
      Resultado: "",
      Notas: "",
    },
  },
  settings: {
    eyebrow: "Administracion",
    title: "Configuracion",
    empty: "No hay configuraciones personalizadas.",
    action: "Guardar ajuste",
    fields: ["Parametro", "Valor", "Responsable", "Notas"],
    defaults: {
      Parametro: "Clinica",
      Valor: "Clinica Elara",
      Responsable: "Admin",
      Notas: "",
    },
  },
};

export default function OperationalPage({ type }) {
  const config = pageCopy[type];
  const [records, setRecords] = useState([]);
  const [form, setForm] = useState(config.defaults);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const completed = useMemo(() => records.length, [records.length]);

  useEffect(() => {
    Promise.resolve().then(() => {
      setLoading(true);
      setError("");
      setForm(config.defaults);
    });

    getModuleRecords(type)
      .then(setRecords)
      .catch((err) =>
        setError(getApiError(err, "No se pudo cargar el modulo"))
      )
      .finally(() => setLoading(false));
  }, [config.defaults, type]);

  const updateForm = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const saveRecord = async (event) => {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");
      const record = await createModuleRecord(type, form);
      setRecords((current) => [record, ...current]);
      setForm(config.defaults);
    } catch (err) {
      setError(getApiError(err, "No se pudo guardar el registro"));
    } finally {
      setSaving(false);
    }
  };

  const deleteRecord = async (id) => {
    try {
      setError("");
      await deleteModuleRecord(type, id);
      setRecords((current) => current.filter((record) => record.id !== id));
    } catch (err) {
      setError(getApiError(err, "No se pudo eliminar el registro"));
    }
  };

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">{config.eyebrow}</p>
          <h2>{config.title}</h2>
        </div>
        <div className="module-counter">
          <strong>{completed}</strong>
          <span>registros</span>
        </div>
      </div>

      <form className="form-panel" onSubmit={saveRecord}>
        <div className="form-grid">
          {config.fields.map((field) => (
            <label className="field" key={field}>
              <span>{field}</span>
              <input
                value={form[field] || ""}
                onChange={(event) => updateForm(field, event.target.value)}
              />
            </label>
          ))}
        </div>
        {error && <div className="alert error">{error}</div>}
        <div className="form-actions">
          <button className="primary-action" type="submit" disabled={saving}>
            {saving ? "Guardando..." : config.action}
          </button>
        </div>
      </form>

      <article className="data-panel">
        <div className="panel-header">
          <h3>Registros</h3>
        </div>
        {loading ? (
          <p className="empty-state">Cargando registros...</p>
        ) : records.length === 0 ? (
          <p className="empty-state">{config.empty}</p>
        ) : (
          <div className="module-list">
            {records.map((record) => (
              <div className="module-row" key={record.id}>
                <div>
                  <strong>{record[config.fields[1]] || record[config.fields[0]]}</strong>
                  <p>{record[config.fields[2]] || "-"}</p>
                </div>
                <span>{record[config.fields[0]]}</span>
                <button className="danger" onClick={() => deleteRecord(record.id)}>
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
