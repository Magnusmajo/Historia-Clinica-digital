from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.models.patient_photo import PatientPhoto
from app.schemas.patient_photo import PatientPhotoRead
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
    prefix="/patients/{patient_id}/photos",
    tags=["patient-photos"],
    dependencies=[Depends(require_roles(*READ_ROLES))],
)

UPLOAD_ROOT = Path("uploads") / "patients"
MAX_FILE_SIZE = 12 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
IMAGE_SIGNATURES = (
    ("image/jpeg", ".jpg", lambda content: content.startswith(b"\xff\xd8\xff")),
    ("image/png", ".png", lambda content: content.startswith(b"\x89PNG\r\n\x1a\n")),
    (
        "image/webp",
        ".webp",
        lambda content: len(content) >= 12
        and content[:4] == b"RIFF"
        and content[8:12] == b"WEBP",
    ),
)


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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Fecha de foto invalida",
        ) from exc


def detect_image(content: bytes):
    for content_type, extension, matches in IMAGE_SIGNATURES:
        if matches(content):
            return content_type, extension
    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="El archivo no parece ser una imagen JPG, PNG o WebP valida.",
    )


async def read_limited_file(file: UploadFile):
    chunks = []
    size = 0

    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break

        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="La foto supera el limite de 12 MB",
            )
        chunks.append(chunk)

    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="La foto esta vacia",
        )

    return b"".join(chunks)


def safe_upload_path(path_value: str):
    root = UPLOAD_ROOT.resolve()
    path = Path(path_value).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ruta de archivo invalida",
        ) from exc
    return path


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
    _user=Depends(require_roles(*WRITE_ROLES)),
):
    ensure_patient(patient_id, db)

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no permitido. Usa JPG, PNG o WebP.",
        )

    content = await read_limited_file(file)
    detected_content_type, extension = detect_image(content)
    if detected_content_type != file.content_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El contenido de la imagen no coincide con el formato declarado.",
        )

    patient_dir = UPLOAD_ROOT / str(patient_id)
    patient_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{extension}"
    file_path = patient_dir / filename
    file_path.write_bytes(content)

    relative_path = file_path.as_posix()
    photo = PatientPhoto(
        patient_id=patient_id,
        filename=filename,
        original_filename=Path(file.filename or filename).name[:255],
        content_type=detected_content_type,
        file_path=relative_path,
        url=f"/uploads/patients/{patient_id}/{filename}",
        view=view or None,
        notes=notes or None,
        taken_at=parse_taken_at(taken_at),
    )
    db.add(photo)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise

    db.refresh(photo)
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_photo(
    patient_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(*WRITE_ROLES)),
):
    photo = (
        db.query(PatientPhoto)
        .filter(PatientPhoto.patient_id == patient_id, PatientPhoto.id == photo_id)
        .first()
    )

    if not photo:
        raise HTTPException(status_code=404, detail="Foto no encontrada")

    path = safe_upload_path(photo.file_path)
    if path.exists() and path.is_file():
        path.unlink()

    db.delete(photo)
    db.commit()
    return None
