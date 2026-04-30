import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { getApiError } from "../services/api";
import { createPatient } from "../services/patientService";

const initialForm = {
  name: "",
  ci: "",
  age: "",
  sex: "",
  phone: "",
  email: "",
  occupation: "",
  city: "",
};

export default function NewPatient() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const validate = () => {
    if (!form.name.trim()) return "El nombre es obligatorio";
    if (!form.ci.trim()) return "La CI es obligatoria";
    if (form.age && Number.isNaN(Number(form.age))) return "Edad invalida";
    return "";
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    const payload = {
      ...form,
      name: form.name.trim(),
      ci: form.ci.trim(),
      age: form.age ? Number(form.age) : null,
      sex: form.sex || null,
      phone: form.phone || null,
      email: form.email || null,
      occupation: form.occupation || null,
      city: form.city || null,
    };

    try {
      setLoading(true);
      setError("");
      const patient = await createPatient(payload);
      navigate(`/patients/${patient.id}`);
    } catch (err) {
      setError(getApiError(err, "Error al crear paciente"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Alta de paciente</p>
          <h2>Nuevo paciente</h2>
        </div>
        <button className="secondary-action" onClick={() => navigate("/patients")}>
          Cancelar
        </button>
      </div>

      <form className="form-panel" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label className="field">
            <span>Nombre completo</span>
            <input name="name" value={form.name} onChange={handleChange} />
          </label>
          <label className="field">
            <span>CI</span>
            <input name="ci" value={form.ci} onChange={handleChange} />
          </label>
          <label className="field">
            <span>Edad</span>
            <input name="age" value={form.age} onChange={handleChange} />
          </label>
          <label className="field">
            <span>Sexo</span>
            <select name="sex" value={form.sex} onChange={handleChange}>
              <option value="">Seleccionar</option>
              <option value="Masculino">Masculino</option>
              <option value="Femenino">Femenino</option>
              <option value="Otro">Otro</option>
            </select>
          </label>
          <label className="field">
            <span>Telefono</span>
            <input name="phone" value={form.phone} onChange={handleChange} />
          </label>
          <label className="field">
            <span>Email</span>
            <input name="email" value={form.email} onChange={handleChange} />
          </label>
          <label className="field">
            <span>Ocupacion</span>
            <input
              name="occupation"
              value={form.occupation}
              onChange={handleChange}
            />
          </label>
          <label className="field">
            <span>Reside en</span>
            <input name="city" value={form.city} onChange={handleChange} />
          </label>
        </div>

        {error && <div className="alert error">{error}</div>}

        <div className="form-actions">
          <button type="button" onClick={() => navigate("/patients")}>
            Volver
          </button>
          <button className="primary-action" type="submit" disabled={loading}>
            {loading ? "Guardando..." : "Crear paciente"}
          </button>
        </div>
      </form>
    </section>
  );
}
