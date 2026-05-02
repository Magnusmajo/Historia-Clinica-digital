from pathlib import Path
from secrets import compare_digest

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Base, engine
from app.routes import (
    appointment,
    clinical_note,
    consultation,
    google_calendar,
    implant_area,
    module_record,
    patient,
    patient_photo,
    stats,
)

# Importar modelos explicitamente para crear tablas en desarrollo.
from app.models.appointment import Appointment
from app.models.consultation import Consultation
from app.models.clinical_note import ClinicalNote
from app.models.implant_area import ImplantArea
from app.models.module_record import ModuleRecord
from app.models.patient import Patient
from app.models.patient_photo import PatientPhoto

settings = get_settings()
if settings.auto_create_tables:
    Base.metadata.create_all(bind=engine)

Path("uploads").mkdir(exist_ok=True)

app = FastAPI(title="Historia Clinica Digital", version="1.0.0")

PUBLIC_PATHS = {
    "/health",
    "/openapi.json",
    "/google-calendar/callback",
}
PUBLIC_PATH_PREFIXES = ("/docs", "/redoc")


@app.middleware("http")
async def require_api_key(request: Request, call_next):
    is_public_path = request.url.path in PUBLIC_PATHS or request.url.path.startswith(
        PUBLIC_PATH_PREFIXES
    )
    if settings.require_api_key and request.method != "OPTIONS" and not is_public_path:
        provided_key = request.headers.get("x-api-key", "")
        if not provided_key or not compare_digest(provided_key, settings.api_key):
            return JSONResponse(
                status_code=401,
                content={"detail": "API key invalida o ausente"},
            )

    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient.router)
app.include_router(patient_photo.router)
app.include_router(appointment.router)
app.include_router(consultation.router)
app.include_router(implant_area.router)
app.include_router(module_record.router)
app.include_router(clinical_note.router)
app.include_router(google_calendar.router)
app.include_router(stats.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
def health_check():
    return {"status": "ok"}
