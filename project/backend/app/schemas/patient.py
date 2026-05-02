from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.consultation import ConsultationRead


class PatientBase(BaseModel):
    name: str = Field(min_length=1, max_length=140)
    ci: str = Field(min_length=3, max_length=32)
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = Field(default=None, max_length=32)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    occupation: str | None = Field(default=None, max_length=140)
    city: str | None = Field(default=None, max_length=140)

    @field_validator("name", "ci", mode="before")
    @classmethod
    def strip_required(cls, value: str):
        value = str(value).strip()
        if not value:
            raise ValueError("Campo obligatorio")
        return value

    @field_validator("sex", "phone", "occupation", "city", mode="before")
    @classmethod
    def normalize_optional_text(cls, value):
        if value is None:
            return None
        value = str(value).strip()
        return value or None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if value is None:
            return None
        value = str(value).strip()
        return value or None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=140)
    ci: str | None = Field(default=None, min_length=3, max_length=32)
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = Field(default=None, max_length=32)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    occupation: str | None = Field(default=None, max_length=140)
    city: str | None = Field(default=None, max_length=140)

    @field_validator("name", "ci", mode="before")
    @classmethod
    def normalize_required_update(cls, value):
        if value is None:
            raise ValueError("Campo obligatorio")
        value = str(value).strip()
        if not value:
            raise ValueError("Campo obligatorio")
        return value

    @field_validator("sex", "phone", "occupation", "city", mode="before")
    @classmethod
    def normalize_text(cls, value):
        if value is None:
            return None
        value = str(value).strip()
        return value or None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if value is None:
            return None
        value = str(value).strip()
        return value or None


class PatientRead(PatientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PatientDetail(PatientRead):
    consultations: list[ConsultationRead] = Field(default_factory=list)
