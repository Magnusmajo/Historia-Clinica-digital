import { useAuth } from "../auth/AuthContext";

export default function Header() {
  const { logout, user } = useAuth();
  const currentDate = new Intl.DateTimeFormat("es-UY").format(new Date());

  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Historia clinica</p>
        <h1>Panel medico</h1>
      </div>

      <div className="topbar-actions">
        <span className="date-pill">{currentDate}</span>
        <div className="doctor-chip">
          <span className="avatar avatar-small">
            {(user?.name || "US").slice(0, 2).toUpperCase()}
          </span>
          <div>
            <strong>{user?.name || "Usuario"}</strong>
            <small>{user?.role || "Sesion"}</small>
          </div>
        </div>
        <button className="secondary-action compact-action" type="button" onClick={logout}>
          Salir
        </button>
      </div>
    </header>
  );
}
