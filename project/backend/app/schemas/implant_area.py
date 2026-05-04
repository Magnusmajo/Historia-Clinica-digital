from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ImplantAreaBase(BaseModel):
    drawing_data: dict[str, Any] = Field(default_factory=dict)
    grafts: int = Field(default=0, ge=0)


class ImplantAreaCreate(ImplantAreaBase):
    consultation_id: int


class ImplantAreaRead(ImplantAreaBase):
    id: int
    consultation_id: int

    model_config = ConfigDict(from_attributes=True)
