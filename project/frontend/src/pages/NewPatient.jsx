import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createPatient } from "../services/patientService";

export default function NewPatient() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    ci: "",
    age: "",
    sex: "",
    phone: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const validate = () => {
    if (!form.name || !form.ci) return "Nombre y CI son obligatorios";
    if (form.age && isNaN(form.age)) return "Edad inválida";
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await createPatient({
        ...form,
        age: form.age ? parseInt(form.age) : null,
      });

      navigate("/patients");
    } catch {
      setError("Error al crear paciente");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "600px" }}>
      <h2>Nuevo Paciente</h2>
      <form onSubmit={handleSubmit}>
        <input name="name" placeholder="Nombre" onChange={handleChange} />
        <input name="ci" placeholder="CI" onChange={handleChange} />
        <input name="age" placeholder="Edad" onChange={handleChange} />
        <input name="sex" placeholder="Sexo" onChange={handleChange} />
        <input name="phone" placeholder="Teléfono" onChange={handleChange} />
        <button type="submit" disabled={loading}>
          {loading ? "Guardando..." : "Crear Paciente"}
        </button>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </form>
    </div>
  );
}