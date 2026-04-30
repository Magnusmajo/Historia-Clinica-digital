from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.consultation import Consultation
from app.models.implant_area import ImplantArea
from app.schemas.implant_area import ImplantAreaCreate, ImplantAreaRead

router = APIRouter(prefix="/implant-areas", tags=["implant-areas"])


@router.post("/", response_model=ImplantAreaRead, status_code=status.HTTP_201_CREATED)
def create_implant_area(data: ImplantAreaCreate, db: Session = Depends(get_db)):
    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == data.consultation_id)
        .first()
    )

    if not consultation:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    area = ImplantArea(**data.model_dump())
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_implant_area(area_id: int, db: Session = Depends(get_db)):
    area = db.query(ImplantArea).filter(ImplantArea.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Area no encontrada")

    db.delete(area)
    db.commit()
    return None
