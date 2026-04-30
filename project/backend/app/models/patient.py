from sqlalchemy import Column, Integer, String
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    ci = Column(String)
    age = Column(Integer)
    sex = Column(String)
    phone = Column(String)