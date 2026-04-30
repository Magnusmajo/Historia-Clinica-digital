from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.clinical_note import ClinicalNote
from app.models.patient import Patient
from app.schemas.clinical_note import ClinicalNoteRead, ClinicalNoteUpdate

router = APIRouter(prefix="/patients/{patient_id}/clinical-notes", tags=["clinical-notes"])


def ensure_patient(patient_id: int, db: Session):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")


@router.get("/", response_model=ClinicalNoteRead | None)
def get_clinical_notes(patient_id: int, db: Session = Depends(get_db)):
    ensure_patient(patient_id, db)
    return db.query(ClinicalNote).filter(ClinicalNote.patient_id == patient_id).first()


@router.put("/", response_model=ClinicalNoteRead)
def upsert_clinical_notes(
    patient_id: int,
    data: ClinicalNoteUpdate,
    db: Session = Depends(get_db),
):
    ensure_patient(patient_id, db)
    note = db.query(ClinicalNote).filter(ClinicalNote.patient_id == patient_id).first()

    if note:
        note.notes = data.notes
    else:
        note = ClinicalNote(patient_id=patient_id, notes=data.notes)
        db.add(note)

    db.commit()
    db.refresh(note)
    return note
