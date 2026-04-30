import { Link } from "react-router-dom";

export default function Sidebar() {
  const menu = [
    ["Dashboard", "/"],
    ["Pacientes", "/patients"],
    ["Agenda", "/"],
    ["Consultas", "/"],
    ["Procedimientos", "/"],
    ["Evolucion", "/"],
    ["Reportes", "/"],
    ["Configuracion", "/"],
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">E</div>
        <div>
          <h2>ELARA</h2>
          <span>Implante capilar</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {menu.map(([label, to]) => (
          <Link
            key={label}
            to={to}
            className={label === "Pacientes" ? "nav-item active" : "nav-item"}
          >
            <span className="nav-icon">{label.slice(0, 1)}</span>
            {label}
          </Link>
        ))}
      </nav>

      <Link to="/patients/new" className="new-patient-button">
        + Nuevo paciente
      </Link>

      <div className="clinic-chip">
        <span className="avatar">CE</span>
        <div>
          <strong>Clinica Elara</strong>
          <small>Admin</small>
        </div>
      </div>
    </aside>
  );
}
