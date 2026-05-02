from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from zoneinfo import ZoneInfo

from app.config import get_settings
from app.database import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentUpdate
from app.services import google_calendar

router = APIRouter(prefix="/appointments", tags=["appointments"])


def get_appointment_or_404(appointment_id: int, db: Session):
    appointment = (
        db.query(Appointment)
        .options(joinedload(Appointment.patient))
        .filter(Appointment.id == appointment_id)
        .first()
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return appointment


def ensure_patient(patient_id: int, db: Session):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient


def validate_times(starts_at, ends_at):
    if ends_at <= starts_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="La hora de fin debe ser posterior al inicio",
        )


def normalize_datetime(value):
    if value.tzinfo is None:
        return value

    return value.astimezone(ZoneInfo(get_settings().app_timezone)).replace(tzinfo=None)


def validate_reminder_method(method: str):
    if method not in {"email", "popup"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El metodo de recordatorio debe ser email o popup",
        )


def try_sync_google(appointment: Appointment):
    event_id = google_calendar.sync_appointment(appointment)
    appointment.google_event_id = event_id
    appointment.google_synced = True


@router.get("/", response_model=list[AppointmentRead])
def get_appointments(db: Session = Depends(get_db)):
    return (
        db.query(Appointment)
        .options(joinedload(Appointment.patient))
        .order_by(Appointment.starts_at.asc())
        .all()
    )


@router.post("/", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    ensure_patient(data.patient_id, db)
    starts_at = normalize_datetime(data.starts_at)
    ends_at = normalize_datetime(data.ends_at)
    validate_times(starts_at, ends_at)
    validate_reminder_method(data.reminder_method)

    appointment = Appointment(
        patient_id=data.patient_id,
        title=data.title,
        starts_at=starts_at,
        ends_at=ends_at,
        location=data.location,
        notes=data.notes,
        reminder_minutes=data.reminder_minutes,
        reminder_method=data.reminder_method,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    appointment = get_appointment_or_404(appointment.id, db)

    if data.sync_google:
        try:
            try_sync_google(appointment)
            db.commit()
            db.refresh(appointment)
        except RuntimeError as exc:
            appointment.google_synced = False
            db.commit()
            appointment.sync_error = str(exc)

    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    appointment = get_appointment_or_404(appointment_id, db)
    update_data = data.model_dump(exclude_unset=True, exclude={"sync_google"})

    if "patient_id" in update_data:
        ensure_patient(update_data["patient_id"], db)

    if "starts_at" in update_data:
        update_data["starts_at"] = normalize_datetime(update_data["starts_at"])
    if "ends_at" in update_data:
        update_data["ends_at"] = normalize_datetime(update_data["ends_at"])

    for key, value in update_data.items():
        setattr(appointment, key, value)

    validate_times(appointment.starts_at, appointment.ends_at)
    validate_reminder_method(appointment.reminder_method)
    db.commit()
    db.refresh(appointment)
    appointment = get_appointment_or_404(appointment.id, db)

    if data.sync_google:
        try:
            try_sync_google(appointment)
            db.commit()
            db.refresh(appointment)
        except RuntimeError as exc:
            appointment.google_synced = False
            db.commit()
            appointment.sync_error = str(exc)

    return appointment


@router.post("/{appointment_id}/sync", response_model=AppointmentRead)
def sync_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = get_appointment_or_404(appointment_id, db)
    try:
        try_sync_google(appointment)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = get_appointment_or_404(appointment_id, db)
    google_event_id = appointment.google_event_id

    db.delete(appointment)
    db.commit()

    if google_event_id:
        try:
            if google_calendar.is_connected():
                google_calendar.delete_google_event(google_event_id)
        except RuntimeError:
            pass

    return None
