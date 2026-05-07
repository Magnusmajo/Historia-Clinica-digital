import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TEST_DB = ROOT / "test_historia_clinica.db"
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["APP_API_KEY"] = "test-key"
os.environ["APP_REQUIRE_API_KEY"] = "true"
os.environ["SECRET_KEY"] = "test-secret-with-at-least-thirty-two-chars"
os.environ["DEFAULT_ADMIN_EMAIL"] = "admin@elara.com"
os.environ["DEFAULT_ADMIN_PASSWORD"] = "TestAdminPassword123!"
os.environ["AUTO_CREATE_TABLES"] = "true"
os.environ["GOOGLE_OAUTH_STATE_FILE"] = "test_google_oauth_state"

from fastapi.testclient import TestClient  # noqa: E402

from app.config import Settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.bootstrap import ensure_default_admin  # noqa: E402
from app.database import SessionLocal  # noqa: E402

HEADERS = {"X-API-Key": "test-key"}


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_default_admin(db)


def teardown_module():
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    TEST_DB.unlink(missing_ok=True)
    (ROOT / "test_google_oauth_state").unlink(missing_ok=True)


def test_api_key_is_required_for_private_routes():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/patients/").status_code == 401
        assert client.get("/uploads/missing.png").status_code == 401
        assert client.get("/patients/", headers=HEADERS).status_code == 401


def test_production_rejects_insecure_development_defaults(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_API_KEY", "short")
    monkeypatch.setenv("SECRET_KEY", "short")
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", "short")
    monkeypatch.setenv("AUTO_CREATE_TABLES", "true")

    with pytest.raises(RuntimeError, match="Configuracion insegura"):
        Settings().validate()


def authenticated_headers(client: TestClient):
    response = client.post(
        "/auth/login",
        headers=HEADERS,
        json={"email": "admin@elara.com", "password": "TestAdminPassword123!"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {**HEADERS, "Authorization": f"Bearer {token}"}


def authenticated_cookie_headers(client: TestClient):
    response = client.post(
        "/auth/login",
        headers=HEADERS,
        json={"email": "admin@elara.com", "password": "TestAdminPassword123!"},
    )
    assert response.status_code == 200
    csrf_token = client.cookies.get("hcd_csrf")
    assert csrf_token
    return {**HEADERS, "X-CSRF-Token": csrf_token}


def test_cookie_session_requires_csrf_for_writes_and_supports_refresh():
    with TestClient(app) as client:
        login_headers = authenticated_cookie_headers(client)

        missing_csrf = client.post(
            "/patients/",
            headers=HEADERS,
            json={"name": "Sin CSRF", "ci": "90000001"},
        )
        assert missing_csrf.status_code == 403

        created = client.post(
            "/patients/",
            headers=login_headers,
            json={"name": "Paciente Cookie", "ci": "90000002"},
        )
        assert created.status_code == 201

        current_user = client.get("/auth/me", headers=HEADERS)
        assert current_user.status_code == 200

        refreshed = client.post("/auth/refresh", headers=HEADERS)
        assert refreshed.status_code == 200
        assert refreshed.json()["csrf_token"]


def test_logout_revokes_existing_tokens():
    with TestClient(app) as client:
        auth_headers = authenticated_headers(client)
        assert client.get("/auth/me", headers=auth_headers).status_code == 200

        logout_response = client.post("/auth/logout", headers=auth_headers)
        assert logout_response.status_code == 204

        revoked = client.get("/auth/me", headers=auth_headers)
        assert revoked.status_code == 401


def test_security_headers_and_readiness_are_present():
    with TestClient(app) as client:
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert "frame-ancestors" in response.headers["content-security-policy"]


def test_patient_validation_and_duplicate_ci():
    with TestClient(app) as client:
        auth_headers = authenticated_headers(client)
        invalid = client.post(
            "/patients/",
            headers=auth_headers,
            json={"name": "Ana", "ci": "12345678", "age": -1},
        )
        assert invalid.status_code == 422

        invalid_email = client.post(
            "/patients/",
            headers=auth_headers,
            json={"name": "Ana", "ci": "12345678", "email": "correo-malo"},
        )
        assert invalid_email.status_code == 422

        created = client.post(
            "/patients/",
            headers=auth_headers,
            json={"name": "Ana Gomez", "ci": "12345678", "age": 34},
        )
        assert created.status_code == 201

        duplicate = client.post(
            "/patients/",
            headers=auth_headers,
            json={"name": "Otra persona", "ci": "12345678"},
        )
        assert duplicate.status_code == 409


def test_appointment_requires_valid_time_window():
    with TestClient(app) as client:
        auth_headers = authenticated_headers(client)
        patient = client.post(
            "/patients/",
            headers=auth_headers,
            json={"name": "Paciente Agenda", "ci": "87654321"},
        ).json()

        response = client.post(
            "/appointments/",
            headers=auth_headers,
            json={
                "patient_id": patient["id"],
                "title": "Consulta",
                "starts_at": "2026-05-01T10:00:00",
                "ends_at": "2026-05-01T09:30:00",
                "sync_google": False,
            },
        )

        assert response.status_code == 422


def test_appointment_patch_does_not_sync_google_by_default():
    with TestClient(app) as client:
        auth_headers = authenticated_headers(client)
        patient = client.post(
            "/patients/",
            headers=auth_headers,
            json={"name": "Paciente Sin Sync", "ci": "55667788"},
        ).json()
        appointment = client.post(
            "/appointments/",
            headers=auth_headers,
            json={
                "patient_id": patient["id"],
                "title": "Consulta inicial",
                "starts_at": "2026-05-01T10:00:00",
                "ends_at": "2026-05-01T10:45:00",
                "sync_google": False,
            },
        ).json()

        response = client.patch(
            f"/appointments/{appointment['id']}",
            headers=auth_headers,
            json={"title": "Consulta actualizada"},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Consulta actualizada"
        assert response.json()["sync_error"] is None


def test_photo_upload_rejects_spoofed_content_type():
    with TestClient(app) as client:
        auth_headers = authenticated_headers(client)
        patient = client.post(
            "/patients/",
            headers=auth_headers,
            json={"name": "Paciente Fotos", "ci": "11223344"},
        ).json()

        response = client.post(
            f"/patients/{patient['id']}/photos/",
            headers=auth_headers,
            data={"view": "Frontal"},
            files={"file": ("fake.png", b"not a real image", "image/png")},
        )

        assert response.status_code == 415


def test_photo_upload_rejects_invalid_extension_even_with_image_signature():
    with TestClient(app) as client:
        auth_headers = authenticated_headers(client)
        patient = client.post(
            "/patients/",
            headers=auth_headers,
            json={"name": "Paciente Extension", "ci": "44332211"},
        ).json()

        png_signature = b"\x89PNG\r\n\x1a\n" + b"0" * 32
        response = client.post(
            f"/patients/{patient['id']}/photos/",
            headers=auth_headers,
            data={"view": "Frontal"},
            files={"file": ("fake.txt", png_signature, "image/png")},
        )

        assert response.status_code == 415


def test_admin_can_manage_users_and_read_audit_logs():
    with TestClient(app) as client:
        auth_headers = authenticated_headers(client)
        created = client.post(
            "/auth/users",
            headers=auth_headers,
            json={
                "name": "Recepcion",
                "email": "recepcion@elara.com",
                "password": "Recepcion123",
                "role": "staff",
            },
        )
        assert created.status_code == 201

        users = client.get("/auth/users", headers=auth_headers)
        assert users.status_code == 200
        assert any(user["email"] == "recepcion@elara.com" for user in users.json())

        audit_logs = client.get("/audit-logs/", headers=auth_headers)
        assert audit_logs.status_code == 200
        assert len(audit_logs.json()) > 0
