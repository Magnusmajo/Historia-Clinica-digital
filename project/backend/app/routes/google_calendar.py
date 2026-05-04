from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.security import ROLE_ADMIN, ROLE_DOCTOR, require_roles
from app.services import google_calendar

router = APIRouter(prefix="/google-calendar", tags=["google-calendar"])


@router.get("/status")
def get_google_calendar_status(_user=Depends(require_roles(ROLE_ADMIN, ROLE_DOCTOR))):
    try:
        return {
            "credentials_file": google_calendar.credentials_file_exists(),
            "connected": google_calendar.is_connected(),
            "calendar_id": get_settings().google_calendar_id,
            "redirect_uri": get_settings().google_redirect_uri,
        }
    except RuntimeError as exc:
        return {
            "credentials_file": google_calendar.credentials_file_exists(),
            "connected": False,
            "error": str(exc),
            "calendar_id": get_settings().google_calendar_id,
            "redirect_uri": get_settings().google_redirect_uri,
        }


@router.get("/auth-url")
def get_auth_url(_user=Depends(require_roles(ROLE_ADMIN, ROLE_DOCTOR))):
    try:
        return {"auth_url": google_calendar.build_auth_url()}
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/callback", response_class=HTMLResponse)
def google_calendar_callback(request: Request):
    try:
        google_calendar.save_callback_token(str(request.url))
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return """
    <html>
      <body style="font-family: system-ui; padding: 32px;">
        <h2>Google Calendar conectado</h2>
        <p>Ya puedes cerrar esta ventana y volver a Historia Clinica Digital.</p>
      </body>
    </html>
    """
