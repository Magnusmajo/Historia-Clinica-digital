export default function Header() {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Historia clinica</p>
        <h1>Panel medico</h1>
      </div>

      <div className="topbar-actions">
        <span className="date-pill">15/05/2026</span>
        <div className="doctor-chip">
          <span className="avatar avatar-small">AR</span>
          <div>
            <strong>Dr. Alexis Rodriguez</strong>
            <small>Medico</small>
          </div>
        </div>
      </div>
    </header>
  );
}
