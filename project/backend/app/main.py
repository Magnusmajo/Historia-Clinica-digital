from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routes import consultation, implant_area, patient, stats

# Importar modelos explicitamente para crear tablas en desarrollo.
from app.models.consultation import Consultation
from app.models.implant_area import ImplantArea
from app.models.patient import Patient

Base.metadata.create_all(bind=engine)
settings = get_settings()

app = FastAPI(title="Historia Clinica Digital", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient.router)
app.include_router(consultation.router)
app.include_router(implant_area.router)
app.include_router(stats.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
