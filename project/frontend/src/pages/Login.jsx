import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { getApiError } from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, login } = useAuth();
  const [form, setForm] = useState({
    email: "admin@elara.com",
    password: "Admin12345",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (isAuthenticated) {
    return <Navigate to={location.state?.from?.pathname || "/"} replace />;
  }

  const updateForm = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      setLoading(true);
      setError("");
      await login(form);
      navigate(location.state?.from?.pathname || "/", { replace: true });
    } catch (err) {
      setError(getApiError(err, "No se pudo iniciar sesion"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-screen">
      <form className="login-panel" onSubmit={handleSubmit}>
        <div className="brand login-brand">
          <div className="brand-mark">E</div>
          <div>
            <h2>ELARA</h2>
            <span>Historia clinica digital</span>
          </div>
        </div>

        <label className="field">
          <span>Email</span>
          <input
            type="email"
            value={form.email}
            onChange={(event) => updateForm("email", event.target.value)}
            autoComplete="username"
          />
        </label>
        <label className="field">
          <span>Contrasena</span>
          <input
            type="password"
            value={form.password}
            onChange={(event) => updateForm("password", event.target.value)}
            autoComplete="current-password"
          />
        </label>

        {error && <div className="alert error">{error}</div>}

        <button className="primary-action" type="submit" disabled={loading}>
          {loading ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
    </main>
  );
}
