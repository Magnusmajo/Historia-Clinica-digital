import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div
      style={{
        width: "250px",
        height: "100vh",
        background: "#020617",
        padding: "20px",
      }}
    >
      <h2 style={{ marginBottom: "30px" }}>ELARA</h2>

      <nav style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
        <Link to="/" style={{ color: "white" }}>Dashboard</Link>
        <Link to="/patients" style={{ color: "white" }}>Pacientes</Link>
      </nav>
    </div>
  );
}