import { NavLink } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Sidebar() {
  const { user } = useAuth();
  const menu = [
    ["Dashboard", "/"],
    ["Pacientes", "/patients"],
    ["Agenda", "/agenda"],
    ["Consultas", "/consultations"],
    ["Procedimientos", "/procedures"],
    ["Evolucion", "/evolution"],
    ["Reportes", "/reports"],
    ["Configuracion", "/settings"],
  ];
  const adminMenu = user?.role === "admin"
    ? [
        ["Usuarios", "/users"],
        ["Auditoria", "/audit"],
      ]
    : [];

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
        {[...menu, ...adminMenu].map(([label, to]) => (
          <NavLink
            key={label}
            to={to}
            className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}
          >
            <span className="nav-icon">{label.slice(0, 1)}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      <NavLink to="/patients/new" className="new-patient-button">
        + Nuevo paciente
      </NavLink>

      <div className="clinic-chip">
        <span className="avatar">CE</span>
        <div>
          <strong>{user?.name || "Clinica Elara"}</strong>
          <small>{user?.role || "Sesion"}</small>
        </div>
      </div>
    </aside>
  );
}
