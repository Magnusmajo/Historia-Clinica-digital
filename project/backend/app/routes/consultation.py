from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.consultation import Consultation
from app.models.patient import Patient
from app.schemas.consultation import ConsultationCreate, ConsultationRead
from app.security import (
    ROLE_ADMIN,
    ROLE_DOCTOR,
    ROLE_STAFF,
    ROLE_VIEWER,
    require_roles,
)

READ_ROLES = (ROLE_ADMIN, ROLE_DOCTOR, ROLE_STAFF, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_DOCTOR, ROLE_STAFF)

router = APIRouter(
    prefix="/consultations",
    tags=["consultations"],
    dependencies=[Depends(require_roles(*READ_ROLES))],
)


@router.post("/", response_model=ConsultationRead, status_code=status.HTTP_201_CREATED)
def create_consultation(
    data: ConsultationCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(*WRITE_ROLES)),
):
    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    consultation = Consultation(**data.model_dump())
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


@router.get("/{consultation_id}", response_model=ConsultationRead)
def get_consultation(consultation_id: int, db: Session = Depends(get_db)):
    consultation = (
        db.query(Consultation)
        .options(selectinload(Consultation.implant_areas))
        .filter(Consultation.id == consultation_id)
        .first()
    )

    if not consultation:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    return consultation
