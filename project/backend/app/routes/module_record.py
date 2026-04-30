from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.module_record import ModuleRecord
from app.schemas.module_record import (
    ModuleRecordCreate,
    ModuleRecordRead,
    ModuleRecordUpdate,
)

router = APIRouter(prefix="/modules", tags=["modules"])

ALLOWED_MODULES = {
    "agenda",
    "consultations",
    "procedures",
    "evolution",
    "reports",
    "settings",
}


def validate_module(module: str):
    if module not in ALLOWED_MODULES:
        raise HTTPException(status_code=404, detail="Modulo no encontrado")


@router.get("/{module}/records", response_model=list[ModuleRecordRead])
def get_module_records(module: str, db: Session = Depends(get_db)):
    validate_module(module)
    return (
        db.query(ModuleRecord)
        .filter(ModuleRecord.module == module)
        .order_by(ModuleRecord.created_at.desc())
        .all()
    )


@router.post(
    "/{module}/records",
    response_model=ModuleRecordRead,
    status_code=status.HTTP_201_CREATED,
)
def create_module_record(
    module: str,
    data: ModuleRecordCreate,
    db: Session = Depends(get_db),
):
    validate_module(module)
    record = ModuleRecord(module=module, payload=data.payload)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{module}/records/{record_id}", response_model=ModuleRecordRead)
def update_module_record(
    module: str,
    record_id: int,
    data: ModuleRecordUpdate,
    db: Session = Depends(get_db),
):
    validate_module(module)
    record = (
        db.query(ModuleRecord)
        .filter(ModuleRecord.id == record_id, ModuleRecord.module == module)
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    record.payload = data.payload
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{module}/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module_record(
    module: str,
    record_id: int,
    db: Session = Depends(get_db),
):
    validate_module(module)
    record = (
        db.query(ModuleRecord)
        .filter(ModuleRecord.id == record_id, ModuleRecord.module == module)
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    db.delete(record)
    db.commit()
    return None
