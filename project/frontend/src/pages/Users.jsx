import { useEffect, useState } from "react";

import { getApiError } from "../services/api";
import { createUser, getUsers, updateUser } from "../services/authService";

const initialForm = {
  name: "",
  email: "",
  password: "",
  role: "doctor",
  is_active: true,
};

const roleLabels = {
  admin: "Administrador",
  doctor: "Medico",
  staff: "Equipo",
  viewer: "Lectura",
};

export default function Users() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadUsers = async () => {
    const data = await getUsers();
    setUsers(data);
  };

  useEffect(() => {
    Promise.resolve()
      .then(loadUsers)
      .catch((err) => setError(getApiError(err, "No se pudo cargar usuarios")))
      .finally(() => setLoading(false));
  }, []);

  const updateForm = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const saveUser = async (event) => {
    event.preventDefault();
    try {
      setSaving(true);
      setError("");
      setNotice("");
      const user = await createUser(form);
      setUsers((current) => [...current, user].sort((a, b) => a.name.localeCompare(b.name)));
      setForm(initialForm);
      setNotice("Usuario creado correctamente.");
    } catch (err) {
      setError(getApiError(err, "No se pudo crear el usuario"));
    } finally {
      setSaving(false);
    }
  };

  const changeRole = async (user, role) => {
    try {
      setError("");
      const updated = await updateUser(user.id, { role });
      setUsers((current) => current.map((item) => (item.id === user.id ? updated : item)));
    } catch (err) {
      setError(getApiError(err, "No se pudo actualizar el rol"));
    }
  };

  const toggleActive = async (user) => {
    try {
      setError("");
      const updated = await updateUser(user.id, { is_active: !user.is_active });
      setUsers((current) => current.map((item) => (item.id === user.id ? updated : item)));
    } catch (err) {
      setError(getApiError(err, "No se pudo actualizar el usuario"));
    }
  };

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Seguridad</p>
          <h2>Usuarios y roles</h2>
        </div>
      </div>

      <form className="form-panel" onSubmit={saveUser}>
        <div className="form-grid">
          <label className="field">
            <span>Nombre</span>
            <input value={form.name} onChange={(event) => updateForm("name", event.target.value)} />
          </label>
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={form.email}
              onChange={(event) => updateForm("email", event.target.value)}
            />
          </label>
          <label className="field">
            <span>Contrasena inicial</span>
            <input
              type="password"
              value={form.password}
              onChange={(event) => updateForm("password", event.target.value)}
            />
          </label>
          <label className="field">
            <span>Rol</span>
            <select value={form.role} onChange={(event) => updateForm("role", event.target.value)}>
              {Object.entries(roleLabels).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </label>
        </div>

        {error && <div className="alert error">{error}</div>}
        {notice && <div className="alert success">{notice}</div>}

        <div className="form-actions">
          <button className="primary-action" type="submit" disabled={saving}>
            {saving ? "Creando..." : "Crear usuario"}
          </button>
        </div>
      </form>

      <article className="data-panel">
        <div className="panel-header">
          <h3>Usuarios</h3>
        </div>
        {loading ? (
          <p className="empty-state">Cargando usuarios...</p>
        ) : (
          <div className="admin-table">
            {users.map((user) => (
              <div className="admin-row" key={user.id}>
                <div>
                  <strong>{user.name}</strong>
                  <p>{user.email}</p>
                </div>
                <select value={user.role} onChange={(event) => changeRole(user, event.target.value)}>
                  {Object.entries(roleLabels).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
                <button className="secondary-action" type="button" onClick={() => toggleActive(user)}>
                  {user.is_active ? "Activo" : "Inactivo"}
                </button>
              </div>
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
