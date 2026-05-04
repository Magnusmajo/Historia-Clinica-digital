from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.auth import AuditLogRead
from app.security import ROLE_ADMIN, require_roles

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit-logs"],
    dependencies=[Depends(require_roles(ROLE_ADMIN))],
)


@router.get("/", response_model=list[AuditLogRead])
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    safe_limit = min(max(limit, 1), 500)
    return (
        db.query(AuditLog)
        .options(joinedload(AuditLog.user))
        .order_by(AuditLog.created_at.desc())
        .limit(safe_limit)
        .all()
    )
