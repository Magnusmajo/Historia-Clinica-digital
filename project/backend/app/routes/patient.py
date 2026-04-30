from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.patient import Patient
from app.schemas.patient import PatientCreate

router = APIRouter(prefix="/patients", tags=["patients"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**data.dict())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/")
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()


@router.get("/{id}")
def get_patient(id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    return patient