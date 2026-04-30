from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.consultation import Consultation
from app.schemas.consultation import ConsultationCreate

router = APIRouter(prefix="/consultations", tags=["consultations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_consultation(data: ConsultationCreate, db: Session = Depends(get_db)):
    consultation = Consultation(**data.dict())
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation