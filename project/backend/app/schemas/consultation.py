from pydantic import BaseModel

class ConsultationCreate(BaseModel):
    patient_id: int