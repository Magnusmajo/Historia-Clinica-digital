from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import patient, consultation, implant_area

# importar modelos explícitamente
from app.models.patient import Patient
from app.models.consultation import Consultation
from app.models.implant_area import ImplantArea

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient.router)
app.include_router(consultation.router)
app.include_router(implant_area.router)