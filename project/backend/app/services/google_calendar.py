import os
import secrets
from datetime import timezone
from pathlib import Path
from secrets import compare_digest
from urllib.parse import parse_qs, urlparse

from app.config import get_settings
from app.models.appointment import Appointment

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def _load_google_modules():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import Flow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Faltan dependencias de Google Calendar. Ejecuta pip install -r requirements.txt"
        ) from exc

    return Request, Credentials, Flow, build


def _settings():
    return get_settings()


def credentials_file_exists():
    return os.path.exists(_settings().google_credentials_file)


def _state_path():
    return Path(_settings().google_oauth_state_file)


def _save_oauth_state(state: str):
    _state_path().write_text(state, encoding="utf-8")


def _load_oauth_state():
    path = _state_path()
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def _clear_oauth_state():
    path = _state_path()
    if path.exists():
        path.unlink()


def _extract_oauth_state(authorization_response: str):
    query = parse_qs(urlparse(authorization_response).query)
    values = query.get("state") or []
    return values[0] if values else None


def get_credentials():
    Request, Credentials, _, _ = _load_google_modules()
    settings = _settings()

    if not os.path.exists(settings.google_token_file):
        return None

    credentials = Credentials.from_authorized_user_file(
        settings.google_token_file,
        SCOPES,
    )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        with open(settings.google_token_file, "w", encoding="utf-8") as token:
            token.write(credentials.to_json())

    return credentials if credentials and credentials.valid else None


def is_connected():
    return credentials_file_exists() and get_credentials() is not None


def build_auth_url():
    _, _, Flow, _ = _load_google_modules()
    settings = _settings()

    if not credentials_file_exists():
        raise RuntimeError(
            f"No se encontro {settings.google_credentials_file}. Descarga el OAuth client JSON de Google Cloud."
        )

    flow = Flow.from_client_secrets_file(
        settings.google_credentials_file,
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri,
    )
    state = secrets.token_urlsafe(32)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )
    _save_oauth_state(state)
    return auth_url


def save_callback_token(authorization_response: str):
    _, _, Flow, _ = _load_google_modules()
    settings = _settings()
    state = _extract_oauth_state(authorization_response)
    expected_state = _load_oauth_state()
    if not state or not expected_state or not compare_digest(state, expected_state):
        raise RuntimeError("Estado OAuth invalido. Inicia la conexion nuevamente.")

    flow = Flow.from_client_secrets_file(
        settings.google_credentials_file,
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri,
        state=state,
    )
    flow.fetch_token(authorization_response=authorization_response)

    with open(settings.google_token_file, "w", encoding="utf-8") as token:
        token.write(flow.credentials.to_json())
    _clear_oauth_state()


def _calendar_service():
    _, _, _, build = _load_google_modules()
    credentials = get_credentials()
    if not credentials:
        raise RuntimeError("Google Calendar no esta conectado")
    return build("calendar", "v3", credentials=credentials)


def _iso_with_timezone(value):
    if value.tzinfo is None:
        return value.isoformat()
    return value.astimezone(timezone.utc).isoformat()


def appointment_to_event(appointment: Appointment):
    settings = _settings()
    patient = appointment.patient
    attendees = []

    if patient.email:
        attendees.append({"email": patient.email, "displayName": patient.name})

    event = {
        "summary": appointment.title,
        "description": appointment.notes or "",
        "location": appointment.location or "",
        "start": {
            "dateTime": _iso_with_timezone(appointment.starts_at),
            "timeZone": settings.app_timezone,
        },
        "end": {
            "dateTime": _iso_with_timezone(appointment.ends_at),
            "timeZone": settings.app_timezone,
        },
        "attendees": attendees,
        "reminders": {
            "useDefault": False,
            "overrides": [
                {
                    "method": appointment.reminder_method,
                    "minutes": appointment.reminder_minutes,
                }
            ],
        },
    }
    return event


def sync_appointment(appointment: Appointment):
    settings = _settings()
    service = _calendar_service()
    event = appointment_to_event(appointment)

    try:
        if appointment.google_event_id:
            result = (
                service.events()
                .update(
                    calendarId=settings.google_calendar_id,
                    eventId=appointment.google_event_id,
                    body=event,
                    sendUpdates="all",
                )
                .execute()
            )
        else:
            result = (
                service.events()
                .insert(
                    calendarId=settings.google_calendar_id,
                    body=event,
                    sendUpdates="all",
                )
                .execute()
            )
    except Exception as exc:
        raise RuntimeError(f"No se pudo sincronizar con Google Calendar: {exc}") from exc

    return result["id"]


def delete_google_event(event_id: str):
    settings = _settings()
    service = _calendar_service()
    try:
        service.events().delete(
            calendarId=settings.google_calendar_id,
            eventId=event_id,
            sendUpdates="all",
        ).execute()
    except Exception as exc:
        raise RuntimeError(f"No se pudo eliminar el evento de Google Calendar: {exc}") from exc
