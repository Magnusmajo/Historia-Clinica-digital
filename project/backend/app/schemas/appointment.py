from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.patient import PatientRead


class AppointmentBase(BaseModel):
    patient_id: int
    title: str = "Consulta capilar"
    starts_at: datetime
    ends_at: datetime
    location: str | None = None
    notes: str | None = None
    reminder_minutes: int = Field(default=1440, ge=0)
    reminder_method: str = "email"


class AppointmentCreate(AppointmentBase):
    sync_google: bool = True


class AppointmentUpdate(BaseModel):
    patient_id: int | None = None
    title: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    location: str | None = None
    notes: str | None = None
    reminder_minutes: int | None = Field(default=None, ge=0)
    reminder_method: str | None = None
    sync_google: bool = True


class AppointmentRead(AppointmentBase):
    id: int
    google_event_id: str | None = None
    google_synced: bool
    created_at: datetime
    updated_at: datetime
    patient: PatientRead

    model_config = ConfigDict(from_attributes=True)
