from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ci = Column(String, unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String)
    phone = Column(String)
    email = Column(String)
    occupation = Column(String)
    city = Column(String)

    consultations = relationship(
        "Consultation",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
