from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
<<<<<<< HEAD

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("location", "notes", mode="before")
    @classmethod
    def empty_text_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value
=======
>>>>>>> 8590154e1a428b6a387f3f56918abb8ed5f80ce0


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

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("location", "notes", mode="before")
    @classmethod
    def empty_text_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class AppointmentRead(AppointmentBase):
    id: int
    google_event_id: str | None = None
    google_synced: bool
    sync_error: str | None = None
    created_at: datetime
    updated_at: datetime
    patient: PatientRead

    model_config = ConfigDict(from_attributes=True)
