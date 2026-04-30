from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.appointment import Appointment
from app.models.consultation import Consultation
from app.models.implant_area import ImplantArea
from app.models.module_record import ModuleRecord
from app.models.patient import Patient

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return {
        "patients": db.query(Patient).count(),
        "appointments": db.query(Appointment).count(),
        "consultations": db.query(Consultation).count(),
        "implant_areas": db.query(ImplantArea).count(),
        "module_records": db.query(ModuleRecord).count(),
    }
