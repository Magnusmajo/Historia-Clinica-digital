from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="consultations")
    implant_areas = relationship(
        "ImplantArea",
        back_populates="consultation",
        cascade="all, delete-orphan",
    )
