import { useEffect, useState } from "react";

import { getApiError } from "../services/api";
import { getAuditLogs } from "../services/auditService";

function formatDate(value) {
  return new Intl.DateTimeFormat("es-UY", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAuditLogs()
      .then(setLogs)
      .catch((err) => setError(getApiError(err, "No se pudo cargar auditoria")))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Seguridad</p>
          <h2>Auditoria</h2>
        </div>
      </div>

      {error && <div className="alert error">{error}</div>}

      <article className="data-panel">
        <div className="panel-header">
          <h3>Accesos y acciones</h3>
        </div>
        {loading ? (
          <p className="empty-state">Cargando auditoria...</p>
        ) : logs.length === 0 ? (
          <p className="empty-state">Todavia no hay eventos registrados.</p>
        ) : (
          <div className="audit-list">
            {logs.map((log) => (
              <div className="audit-row" key={log.id}>
                <div>
                  <strong>{log.action} / {log.resource}</strong>
                  <p>{log.path || "-"} - {log.method || "-"}</p>
                </div>
                <span>{log.user?.email || "Sistema"}</span>
                <span>{log.status_code || "-"}</span>
                <span>{formatDate(log.created_at)}</span>
              </div>
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
