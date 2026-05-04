<<<<<<< HEAD
from pydantic import BaseModel, ConfigDict, Field, field_validator
=======
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
>>>>>>> 8590154e1a428b6a387f3f56918abb8ed5f80ce0

from app.schemas.consultation import ConsultationRead


class PatientBase(BaseModel):
<<<<<<< HEAD
    name: str = Field(min_length=1, max_length=120)
    ci: str = Field(min_length=1, max_length=30)
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    phone: str | None = None
    email: str | None = None
    occupation: str | None = None
    city: str | None = None
=======
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
>>>>>>> 8590154e1a428b6a387f3f56918abb8ed5f80ce0

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
<<<<<<< HEAD
    name: str | None = Field(default=None, min_length=1, max_length=120)
    ci: str | None = Field(default=None, min_length=1, max_length=30)
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    phone: str | None = None
    email: str | None = None
    occupation: str | None = None
    city: str | None = None
=======
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
>>>>>>> 8590154e1a428b6a387f3f56918abb8ed5f80ce0

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
