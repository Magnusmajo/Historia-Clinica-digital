from pydantic import BaseModel

class PatientCreate(BaseModel):
    name: str
    ci: str
    age: int
    sex: str | None = None
    phone: str | None = None