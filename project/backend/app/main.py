import logging
from secrets import compare_digest

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Base, SessionLocal, check_database, engine
from app.errors import register_exception_handlers
from app.logging_config import configure_logging
from app.rate_limiter import RateLimiter
from app.routes import (
    audit_log,
    appointment,
    auth,
    clinical_note,
    consultation,
    google_calendar,
    implant_area,
    module_record,
    patient,
    patient_photo,
    stats,
)
from app.security import decode_access_token, extract_access_token, extract_bearer_token

# Importar modelos explicitamente para crear tablas en desarrollo.
from app.models.audit_log import AuditLog
from app.models.appointment import Appointment
from app.models.consultation import Consultation
from app.models.clinical_note import ClinicalNote
from app.models.implant_area import ImplantArea
from app.models.module_record import ModuleRecord
from app.models.patient import Patient
from app.models.patient_photo import PatientPhoto
from app.models.user import User
from app.services.audit import write_audit_log
from app.services.bootstrap import ensure_default_admin

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()
settings.validate()
if settings.auto_create_tables:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_default_admin(db)

settings.upload_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Historia Clinica Digital", version="1.0.0")
register_exception_handlers(app)
rate_limiter = RateLimiter()

PUBLIC_PATHS = {
    "/health",
    "/health/ready",
    "/openapi.json",
    "/google-calendar/callback",
}
PUBLIC_PATH_PREFIXES = ("/docs", "/redoc")
AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
CSRF_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
CSRF_EXEMPT_PATHS = {
    "/auth/login",
    "/auth/refresh",
    "/auth/logout",
    "/google-calendar/callback",
}


def _user_id_from_request(request: Request):
    token = extract_access_token(request)
    payload = decode_access_token(token or "")
    if not payload:
        return None
    try:
        return int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        return None


def _resource_from_path(path: str):
    parts = [part for part in path.strip("/").split("/") if part]
    return parts[0] if parts else "root"


def _action_from_method(method: str):
    return {
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }.get(method, "access")


def _audit_request(request: Request, status_code: int):
    if request.method not in AUDITED_METHODS:
        return
    if request.url.path in {"/auth/login", "/auth/refresh"}:
        return

    db = SessionLocal()
    try:
        write_audit_log(
            db,
            user_id=_user_id_from_request(request),
            action=_action_from_method(request.method),
            resource=_resource_from_path(request.url.path),
            request=request,
            status_code=status_code,
        )
    except Exception:
        logger.exception("No se pudo registrar auditoria para %s", request.url.path)
    finally:
        db.close()


def _add_security_headers(request: Request, response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(), microphone=(), geolocation=()",
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data: blob:; style-src 'self' "
        "'unsafe-inline'; script-src 'self' 'unsafe-inline'; object-src 'none'; "
        "frame-ancestors 'none'; base-uri 'self'",
    )
    if settings.is_production:
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )
    if request.url.path.startswith("/uploads"):
        response.headers.setdefault("Cache-Control", "private, no-store")
    return response


def _csrf_is_valid(request: Request):
    if request.method not in CSRF_METHODS or request.url.path in CSRF_EXEMPT_PATHS:
        return True
    if extract_bearer_token(request):
        return True
    access_cookie = request.cookies.get(settings.access_cookie_name)
    if not access_cookie:
        return True
    csrf_cookie = request.cookies.get(settings.csrf_cookie_name, "")
    csrf_header = request.headers.get("x-csrf-token", "")
    return bool(csrf_cookie and csrf_header and compare_digest(csrf_cookie, csrf_header))


@app.middleware("http")
async def require_api_key(request: Request, call_next):
    is_public_path = request.url.path in PUBLIC_PATHS or request.url.path.startswith(
        PUBLIC_PATH_PREFIXES
    )
    try:
        rate_limiter.check(request)
    except HTTPException as exc:
        _audit_request(request, exc.status_code)
        return _add_security_headers(
            request,
            JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}),
        )

    if settings.require_api_key and request.method != "OPTIONS" and not is_public_path:
        provided_key = request.headers.get("x-api-key", "")
        if not provided_key or not compare_digest(provided_key, settings.api_key):
            _audit_request(request, 401)
            return _add_security_headers(
                request,
                JSONResponse(
                    status_code=401,
                    content={"detail": "API key invalida o ausente"},
                ),
            )

    if not _csrf_is_valid(request):
        _audit_request(request, 403)
        return _add_security_headers(
            request,
            JSONResponse(
                status_code=403,
                content={"detail": "Token CSRF invalido o ausente"},
            )
        )

    if (
        settings.require_user_auth
        and request.url.path.startswith("/uploads")
        and not decode_access_token(extract_access_token(request) or "")
    ):
        _audit_request(request, 401)
        return _add_security_headers(
            request,
            JSONResponse(
                status_code=401,
                content={"detail": "Sesion invalida o expirada"},
            ),
        )

    response = await call_next(request)
    _audit_request(request, response.status_code)
    return _add_security_headers(request, response)


if settings.allowed_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(patient_photo.router)
app.include_router(appointment.router)
app.include_router(consultation.router)
app.include_router(implant_area.router)
app.include_router(module_record.router)
app.include_router(clinical_note.router)
app.include_router(google_calendar.router)
app.include_router(stats.router)
app.include_router(audit_log.router)

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness_check():
    check_database()
    return {"status": "ready"}
