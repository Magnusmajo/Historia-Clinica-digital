from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModuleRecordCreate(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class ModuleRecordUpdate(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class ModuleRecordRead(BaseModel):
    id: int
    module: str
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
