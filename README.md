# Historia Clinica Digital

Sistema full-stack para gestion de pacientes, consultas y planificacion de areas de implante capilar.

## Stack

- Frontend: React, Vite, React Router, Axios
- Backend: FastAPI, SQLAlchemy, Pydantic
- Base de datos por defecto: SQLite local
- Base opcional: PostgreSQL mediante `DATABASE_URL`

## Ejecutar backend

```powershell
cd project/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

API: `http://localhost:8000`

Documentacion interactiva: `http://localhost:8000/docs`

## Ejecutar frontend

```powershell
cd project/frontend
npm install
copy .env.example .env
npm run dev
```

App: `http://localhost:5173`

## Funcionalidad incluida

- Dashboard con metricas reales.
- Alta de pacientes.
- Busqueda y listado de pacientes.
- Ficha clinica del paciente.
- Creacion automatica de consulta al guardar un area de implante.
- Registro de zonas, vista, notas y foliculos estimados.
- Eliminacion de areas planificadas.

## Variables de entorno

Backend:

```env
DATABASE_URL=sqlite:///./historia_clinica.db
FRONTEND_ORIGIN=http://localhost:5173
APP_API_KEY=dev-local-api-key
APP_REQUIRE_API_KEY=true
AUTO_CREATE_TABLES=true
```

Frontend:

```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=dev-local-api-key
```

Para PostgreSQL, usar por ejemplo:

```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/historia_clinica
```

## Seguridad local

La API exige `X-API-Key` en las rutas privadas. En desarrollo, el frontend envia
`VITE_API_KEY`; en produccion cambia `APP_API_KEY` y `VITE_API_KEY` por un valor
propio. Para exponer el sistema en red real, agrega autenticacion de usuarios y
HTTPS delante de esta API key compartida.

`AUTO_CREATE_TABLES=true` crea tablas automaticamente para desarrollo. En una
instalacion real conviene desactivarlo y administrar cambios de esquema con
migraciones.
