import base64
import binascii
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.user import User

ROLE_ADMIN = "admin"
ROLE_DOCTOR = "doctor"
ROLE_STAFF = "staff"
ROLE_VIEWER = "viewer"
USER_ROLES = {ROLE_ADMIN, ROLE_DOCTOR, ROLE_STAFF, ROLE_VIEWER}

WRITE_ROLES = {ROLE_ADMIN, ROLE_DOCTOR, ROLE_STAFF}
CLINICAL_ROLES = {ROLE_ADMIN, ROLE_DOCTOR}

HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 390000
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def _b64url_encode(value: bytes):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str):
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str):
    salt = secrets.token_urlsafe(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ITERATIONS,
    )
    return f"{HASH_ALGORITHM}${HASH_ITERATIONS}${salt}${_b64url_encode(digest)}"


def verify_password(password: str, password_hash: str):
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
        if algorithm != HASH_ALGORITHM:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )
        return hmac.compare_digest(_b64url_encode(digest), expected)
    except (ValueError, TypeError):
        return False


def _create_token(user: User, token_type: str, expires_delta: timedelta):
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "ver": user.token_version,
        "type": token_type,
        "jti": secrets.token_urlsafe(24),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def create_access_token(user: User):
    return _create_token(
        user,
        ACCESS_TOKEN_TYPE,
        timedelta(minutes=get_settings().access_token_minutes),
    )


def create_refresh_token(user: User):
    return _create_token(
        user,
        REFRESH_TOKEN_TYPE,
        timedelta(days=get_settings().refresh_token_days),
    )


def _decode_token(token: str, expected_type: str):
    try:
        header_value, payload_value, signature_value = token.split(".", 2)
        header = json.loads(_b64url_decode(header_value))
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            return None

        signing_input = f"{header_value}.{payload_value}"
        expected_signature = hmac.new(
            get_settings().secret_key.encode("utf-8"),
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(
            _b64url_encode(expected_signature),
            signature_value,
        ):
            return None

        payload = json.loads(_b64url_decode(payload_value))
        if payload.get("type") != expected_type:
            return None
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return payload
    except (binascii.Error, ValueError, TypeError, json.JSONDecodeError):
        return None


def decode_access_token(token: str):
    return _decode_token(token, ACCESS_TOKEN_TYPE)


def decode_refresh_token(token: str):
    return _decode_token(token, REFRESH_TOKEN_TYPE)


def extract_bearer_token(request: Request):
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def extract_access_token(request: Request):
    return extract_bearer_token(request) or request.cookies.get(
        get_settings().access_cookie_name
    )


def generate_csrf_token():
    return secrets.token_urlsafe(32)


def _cookie_options(max_age: int, *, http_only: bool):
    settings = get_settings()
    return {
        "max_age": max_age,
        "httponly": http_only,
        "secure": settings.cookie_secure,
        "samesite": settings.cookie_samesite,
        "domain": settings.cookie_domain,
        "path": "/",
    }


def set_auth_cookies(response: Response, user: User):
    settings = get_settings()
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    csrf_token = generate_csrf_token()
    response.set_cookie(
        settings.access_cookie_name,
        access_token,
        **_cookie_options(settings.access_token_minutes * 60, http_only=True),
    )
    response.set_cookie(
        settings.refresh_cookie_name,
        refresh_token,
        **_cookie_options(settings.refresh_token_days * 24 * 60 * 60, http_only=True),
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        **_cookie_options(settings.refresh_token_days * 24 * 60 * 60, http_only=False),
    )
    return access_token, csrf_token


def clear_auth_cookies(response: Response):
    settings = get_settings()
    for name in (
        settings.access_cookie_name,
        settings.refresh_cookie_name,
        settings.csrf_cookie_name,
    ):
        response.delete_cookie(
            name,
            path="/",
            domain=settings.cookie_domain,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
        )


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = extract_access_token(request)
    payload = decode_access_token(token or "")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesion invalida o expirada",
        )

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesion invalida o expirada",
        ) from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo o no encontrado",
        )
    if int(payload.get("ver", -1)) != user.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesion revocada",
        )
    return user


def require_roles(*roles: str):
    allowed_roles = set(roles)

    def dependency(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta accion",
            )
        return user

    return dependency
