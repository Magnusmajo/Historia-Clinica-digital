from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.implant_area import ImplantArea
from app.schemas.implant_area import ImplantAreaCreate

router = APIRouter(prefix="/implant-area", tags=["implant-area"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_implant_area(data: ImplantAreaCreate, db: Session = Depends(get_db)):
    area = ImplantArea(**data.dict())
    db.add(area)
    db.commit()
    db.refresh(area)
    return area