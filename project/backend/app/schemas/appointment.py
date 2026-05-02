from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.patient import PatientRead


class AppointmentBase(BaseModel):
    patient_id: int
    title: str = Field(default="Consulta capilar", min_length=1, max_length=160)
    starts_at: datetime
    ends_at: datetime
    location: str | None = Field(default=None, max_length=180)
    notes: str | None = Field(default=None, max_length=4000)
    reminder_minutes: int = Field(default=1440, ge=0)
    reminder_method: Literal["email", "popup"] = "email"


class AppointmentCreate(AppointmentBase):
    sync_google: bool = True


class AppointmentUpdate(BaseModel):
    patient_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=160)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    location: str | None = Field(default=None, max_length=180)
    notes: str | None = Field(default=None, max_length=4000)
    reminder_minutes: int | None = Field(default=None, ge=0)
    reminder_method: Literal["email", "popup"] | None = None
    sync_google: bool = True


class AppointmentRead(AppointmentBase):
    id: int
    google_event_id: str | None = None
    google_synced: bool
    sync_error: str | None = None
    created_at: datetime
    updated_at: datetime
    patient: PatientRead

    model_config = ConfigDict(from_attributes=True)
