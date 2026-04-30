export default function Header() {
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
