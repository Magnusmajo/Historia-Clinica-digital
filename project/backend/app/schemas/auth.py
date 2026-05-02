from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.security import ROLE_ADMIN, ROLE_DOCTOR, ROLE_STAFF, ROLE_VIEWER

UserRole = Literal["admin", "doctor", "staff", "viewer"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return str(value).strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserRead"


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=140)
    email: EmailStr
    role: UserRole = ROLE_DOCTOR
    is_active: bool = True

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Campo obligatorio")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_user_email(cls, value):
        return str(value).strip().lower()


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=140)
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value):
        if value is None:
            return None
        value = str(value).strip()
        if not value:
            raise ValueError("Campo obligatorio")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if value is None:
            return None
        return str(value).strip().lower()


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogRead(BaseModel):
    id: int
    user_id: int | None = None
    action: str
    resource: str
    resource_id: str | None = None
    method: str | None = None
    path: str | None = None
    status_code: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    details: dict | None = None
    created_at: datetime
    user: UserRead | None = None

    model_config = ConfigDict(from_attributes=True)


USER_ROLE_OPTIONS = [ROLE_ADMIN, ROLE_DOCTOR, ROLE_STAFF, ROLE_VIEWER]
