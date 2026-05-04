from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.consultation import ConsultationRead


class PatientBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    ci: str = Field(min_length=1, max_length=30)
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    phone: str | None = None
    email: str | None = None
    occupation: str | None = None
    city: str | None = None

    @field_validator("name", "ci", mode="before")
    @classmethod
    def strip_required_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("sex", "phone", "email", "occupation", "city", mode="before")
    @classmethod
    def empty_text_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    ci: str | None = Field(default=None, min_length=1, max_length=30)
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    phone: str | None = None
    email: str | None = None
    occupation: str | None = None
    city: str | None = None

    @field_validator("name", "ci", mode="before")
    @classmethod
    def strip_required_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("sex", "phone", "email", "occupation", "city", mode="before")
    @classmethod
    def empty_text_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class PatientRead(PatientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PatientDetail(PatientRead):
    consultations: list[ConsultationRead] = Field(default_factory=list)
