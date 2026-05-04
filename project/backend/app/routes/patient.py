from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.consultation import Consultation
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientDetail, PatientRead, PatientUpdate
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
    prefix="/patients",
    tags=["patients"],
    dependencies=[Depends(require_roles(*READ_ROLES))],
)


@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(
    data: PatientCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(*WRITE_ROLES)),
):
    patient = Patient(**data.model_dump())
    db.add(patient)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un paciente con esa CI",
        ) from exc

    db.refresh(patient)
    return patient


@router.get("/", response_model=list[PatientRead])
def get_patients(search: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Patient).order_by(Patient.name.asc())

    if search:
        term = f"%{search.strip()}%"
        query = query.filter((Patient.name.ilike(term)) | (Patient.ci.ilike(term)))

    return query.all()


@router.get("/{patient_id}", response_model=PatientDetail)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = (
        db.query(Patient)
        .options(
            selectinload(Patient.consultations).selectinload(
                Consultation.implant_areas
            )
        )
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    return patient


@router.patch("/{patient_id}", response_model=PatientRead)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(*WRITE_ROLES)),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un paciente con esa CI",
        ) from exc

    db.refresh(patient)
    return patient
