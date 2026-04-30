from pydantic import BaseModel, ConfigDict

from app.schemas.consultation import ConsultationRead


class PatientBase(BaseModel):
    name: str
    ci: str
    age: int | None = None
    sex: str | None = None
    phone: str | None = None
    email: str | None = None
    occupation: str | None = None
    city: str | None = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: str | None = None
    ci: str | None = None
    age: int | None = None
    sex: str | None = None
    phone: str | None = None
    email: str | None = None
    occupation: str | None = None
    city: str | None = None


class PatientRead(PatientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PatientDetail(PatientRead):
    consultations: list[ConsultationRead] = []
