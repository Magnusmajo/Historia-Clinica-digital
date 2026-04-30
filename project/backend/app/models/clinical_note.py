from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class ClinicalNote(Base):
    __tablename__ = "clinical_notes"
    __table_args__ = (UniqueConstraint("patient_id", name="uq_clinical_notes_patient"),)

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    notes = Column(JSON, nullable=False, default=dict)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    patient = relationship("Patient")
