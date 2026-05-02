from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.implant_area import ImplantAreaRead


class ConsultationCreate(BaseModel):
    patient_id: int


class ConsultationRead(BaseModel):
    id: int
    patient_id: int
    date: datetime
    implant_areas: list[ImplantAreaRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
