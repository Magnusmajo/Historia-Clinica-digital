from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.models.patient_photo import PatientPhoto
from app.schemas.patient_photo import PatientPhotoRead

router = APIRouter(prefix="/patients/{patient_id}/photos", tags=["patient-photos"])

UPLOAD_ROOT = Path("uploads") / "patients"
MAX_FILE_SIZE = 12 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def ensure_patient(patient_id: int, db: Session):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient


def parse_taken_at(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Fecha de foto invalida",
        ) from exc


@router.get("/", response_model=list[PatientPhotoRead])
def get_patient_photos(patient_id: int, db: Session = Depends(get_db)):
    ensure_patient(patient_id, db)
    return (
        db.query(PatientPhoto)
        .filter(PatientPhoto.patient_id == patient_id)
        .order_by(PatientPhoto.taken_at.desc().nullslast(), PatientPhoto.created_at.desc())
        .all()
    )


@router.post("/", response_model=PatientPhotoRead, status_code=status.HTTP_201_CREATED)
async def upload_patient_photo(
    patient_id: int,
    file: UploadFile = File(...),
    view: str | None = Form(default=None),
    notes: str | None = Form(default=None),
    taken_at: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    ensure_patient(patient_id, db)

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no permitido. Usa JPG, PNG o WebP.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="La foto supera el limite de 12 MB",
        )

    patient_dir = UPLOAD_ROOT / str(patient_id)
    patient_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename or "foto").suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        extension = ".jpg" if file.content_type == "image/jpeg" else ".png"

    filename = f"{uuid4().hex}{extension}"
    file_path = patient_dir / filename
    file_path.write_bytes(content)

    relative_path = file_path.as_posix()
    photo = PatientPhoto(
        patient_id=patient_id,
        filename=filename,
        original_filename=file.filename or filename,
        content_type=file.content_type,
        file_path=relative_path,
        url=f"/uploads/patients/{patient_id}/{filename}",
        view=view or None,
        notes=notes or None,
        taken_at=parse_taken_at(taken_at),
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_photo(
    patient_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
):
    photo = (
        db.query(PatientPhoto)
        .filter(PatientPhoto.patient_id == patient_id, PatientPhoto.id == photo_id)
        .first()
    )

    if not photo:
        raise HTTPException(status_code=404, detail="Foto no encontrada")

    path = Path(photo.file_path)
    if path.exists() and path.is_file():
        path.unlink()

    db.delete(photo)
    db.commit()
    return None
