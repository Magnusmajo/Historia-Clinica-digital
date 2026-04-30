from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class ImplantArea(Base):
    __tablename__ = "implant_areas"

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    drawing_data = Column(JSON)
    grafts = Column(Integer)

    consultation = relationship("Consultation", backref="implant_areas")