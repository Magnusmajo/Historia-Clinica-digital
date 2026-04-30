import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Patients() {
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    api.get("/patients").then((res) => setPatients(res.data));
  }, []);

  return (
    <div>
      <h1>Pacientes</h1>

      <div style={{ marginTop: "20px" }}>
        {patients.map((p) => (
          <div
            key={p.id}
            style={{
              padding: "10px",
              borderBottom: "1px solid #1e293b",
            }}
          >
            {p.name} - {p.ci}
          </div>
        ))}
      </div>
    </div>
  );
}