from pathlib import Path
from secrets import compare_digest

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Base, engine
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
from app.security import decode_access_token, extract_bearer_token

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
from app.database import SessionLocal
from app.services.audit import write_audit_log
from app.services.bootstrap import ensure_default_admin

settings = get_settings()
if settings.auto_create_tables:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_default_admin(db)

Path("uploads").mkdir(exist_ok=True)

app = FastAPI(title="Historia Clinica Digital", version="1.0.0")

PUBLIC_PATHS = {
    "/health",
    "/openapi.json",
    "/google-calendar/callback",
}
PUBLIC_PATH_PREFIXES = ("/docs", "/redoc")
AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _user_id_from_request(request: Request):
    token = extract_bearer_token(request)
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
    if request.url.path == "/auth/login":
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
    finally:
        db.close()


@app.middleware("http")
async def require_api_key(request: Request, call_next):
    is_public_path = request.url.path in PUBLIC_PATHS or request.url.path.startswith(
        PUBLIC_PATH_PREFIXES
    )
    if settings.require_api_key and request.method != "OPTIONS" and not is_public_path:
        provided_key = request.headers.get("x-api-key", "")
        if not provided_key or not compare_digest(provided_key, settings.api_key):
            _audit_request(request, 401)
            return JSONResponse(
                status_code=401,
                content={"detail": "API key invalida o ausente"},
            )

    if (
        settings.require_user_auth
        and request.url.path.startswith("/uploads")
        and not decode_access_token(extract_bearer_token(request) or "")
    ):
        _audit_request(request, 401)
        return JSONResponse(
            status_code=401,
            content={"detail": "Sesion invalida o expirada"},
        )

    response = await call_next(request)
    _audit_request(request, response.status_code)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
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

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
def health_check():
    return {"status": "ok"}
