from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ClinicalNoteUpdate(BaseModel):
    notes: dict[str, Any] = Field(default_factory=dict)


class ClinicalNoteRead(BaseModel):
    id: int
    patient_id: int
    notes: dict[str, Any]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
