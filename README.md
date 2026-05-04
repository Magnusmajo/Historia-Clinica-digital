# Historia Clinica Digital

Sistema full-stack para gestion de pacientes, consultas y planificacion de areas de implante capilar.

## Stack

- Frontend: React, Vite, React Router, Axios
- Backend: FastAPI, SQLAlchemy, Pydantic
- Base de datos por defecto: SQLite local
- Base opcional: PostgreSQL mediante `DATABASE_URL`
- Migraciones: Alembic

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
- Login con usuarios, roles y proteccion por token.
- Administracion de usuarios y registro de auditoria para administradores.
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
APP_REQUIRE_USER_AUTH=true
SECRET_KEY=dev-local-secret-change-me
ACCESS_TOKEN_MINUTES=480
SEED_ADMIN_USER=true
DEFAULT_ADMIN_EMAIL=admin@elara.com
DEFAULT_ADMIN_PASSWORD=Admin12345
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

La API exige `X-API-Key` y token Bearer de usuario en las rutas privadas. En
desarrollo, el frontend envia `VITE_API_KEY` y el login inicial es:

```text
Email: admin@elara.com
Contrasena: Admin12345
```

En produccion cambia `APP_API_KEY`, `VITE_API_KEY`, `SECRET_KEY` y
`DEFAULT_ADMIN_PASSWORD` antes de levantar la app. Usa HTTPS si expones el
sistema fuera de tu maquina.

`AUTO_CREATE_TABLES=true` crea tablas automaticamente para desarrollo. En una
instalacion real conviene desactivarlo y administrar cambios de esquema con
migraciones.

## Migraciones

Alembic esta configurado en `project/backend/alembic`. Para crear o actualizar
la base con migraciones:

```powershell
cd project/backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

Si ya tienes una base creada con `AUTO_CREATE_TABLES=true`, haz backup y marca
la migracion inicial como aplicada con `alembic stamp head` antes de desactivar
`AUTO_CREATE_TABLES`.
