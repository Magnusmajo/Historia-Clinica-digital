from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def write_audit_log(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    resource: str,
    resource_id: str | None = None,
    request: Request | None = None,
    status_code: int | None = None,
    details: dict | None = None,
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        method=request.method if request else None,
        path=str(request.url.path) if request else None,
        status_code=status_code,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
        details=details,
    )
    db.add(log)
    db.commit()
    return log
