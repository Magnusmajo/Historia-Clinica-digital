from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String

from app.database import Base


class ModuleRecord(Base):
    __tablename__ = "module_records"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String, index=True, nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
