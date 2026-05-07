# Historia Clinica Digital

Aplicacion full-stack para gestion clinica de pacientes, agenda, fotos de evolucion, planificacion de areas de implante capilar, usuarios, roles y auditoria.

## Stack

- Frontend: React, Vite, React Router, Axios
- Backend: FastAPI, SQLAlchemy, Pydantic
- Base de datos: PostgreSQL
- Migraciones: Alembic
- Produccion: Docker Compose, Nginx, Gunicorn/Uvicorn

## Variables Requeridas

Backend:

```env
APP_ENV
DATABASE_URL
FRONTEND_ORIGIN
FRONTEND_ORIGINS
ALLOWED_HOSTS
APP_TIMEZONE
APP_API_KEY
APP_REQUIRE_API_KEY
APP_REQUIRE_USER_AUTH
SECRET_KEY
ACCESS_TOKEN_MINUTES
REFRESH_TOKEN_DAYS
SEED_ADMIN_USER
DEFAULT_ADMIN_NAME
DEFAULT_ADMIN_EMAIL
DEFAULT_ADMIN_PASSWORD
AUTO_CREATE_TABLES
COOKIE_SECURE
COOKIE_SAMESITE
COOKIE_DOMAIN
UPLOAD_DIR
MAX_UPLOAD_MB
GOOGLE_CALENDAR_ID
GOOGLE_CREDENTIALS_FILE
GOOGLE_TOKEN_FILE
GOOGLE_OAUTH_STATE_FILE
GOOGLE_REDIRECT_URI
DB_POOL_SIZE
DB_MAX_OVERFLOW
DB_POOL_RECYCLE_SECONDS
DB_POOL_TIMEOUT_SECONDS
DB_STATEMENT_TIMEOUT_MS
DB_CONNECT_TIMEOUT_SECONDS
RATE_LIMIT_ENABLED
REDIS_URL
RATE_LIMIT_REQUESTS
RATE_LIMIT_WINDOW_SECONDS
AUTH_RATE_LIMIT_REQUESTS
LOG_LEVEL
```

Frontend:

```env
VITE_API_URL
VITE_API_KEY
VITE_CSRF_COOKIE_NAME
```

Docker Compose tambien requiere:

```env
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
FRONTEND_PORT
```

## Ejecucion Local

Backend:

```powershell
cd project/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd project/frontend
npm install
npm run dev
```

## Produccion Con Docker

Usa variables de entorno reales, con secretos generados fuera del repositorio:

```powershell
docker compose --env-file project/backend/.env up --build -d
```

Servicios:

- Frontend/Nginx: `http://localhost`
- Backend interno: `backend:8000`
- PostgreSQL interno: `db:5432`
- Redis interno: `redis:6379`

El backend espera la base de datos, ejecuta `alembic upgrade head` y luego inicia Gunicorn con workers Uvicorn.

## Verificacion

Backend:

```powershell
cd project/backend
python -m pytest
python -m alembic upgrade head
```

Frontend:

```powershell
cd project/frontend
npm run lint
npm run build
```

Healthchecks:

- `GET /health`
- `GET /health/ready`

## Seguridad

- PostgreSQL obligatorio fuera de tests.
- Cookies HttpOnly para access/refresh token.
- CSRF double-submit para escrituras con cookies.
- API key obligatoria para rutas privadas.
- Roles por endpoint.
- Rate limiting por IP y ruta.
- Headers de seguridad en backend y Nginx.
- Uploads clinicos protegidos por sesion, con validacion de extension, MIME, firma binaria y tamano.
- Auditoria de operaciones de escritura.
- `AUTO_CREATE_TABLES=false`; el esquema se administra con Alembic.
