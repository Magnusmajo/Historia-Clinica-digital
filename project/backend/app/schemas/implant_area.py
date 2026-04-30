from pydantic import BaseModel

class ImplantAreaCreate(BaseModel):
    consultation_id: int
    drawing_data: dict
    grafts: int