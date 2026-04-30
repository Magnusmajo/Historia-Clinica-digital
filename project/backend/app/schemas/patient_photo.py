from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PatientPhotoRead(BaseModel):
    id: int
    patient_id: int
    filename: str
    original_filename: str
    content_type: str
    url: str
    view: str | None = None
    notes: str | None = None
    taken_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
