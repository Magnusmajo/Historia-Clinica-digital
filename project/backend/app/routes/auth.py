from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.security import (
    ROLE_ADMIN,
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)
from app.services.audit import write_audit_log

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        write_audit_log(
            db,
            user_id=user.id if user else None,
            action="login_failed",
            resource="auth",
            request=request,
            status_code=401,
            details={"email": data.email},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena invalidos",
        )

    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    write_audit_log(
        db,
        user_id=user.id,
        action="login_success",
        resource="auth",
        request=request,
        status_code=200,
    )
    return {"access_token": create_access_token(user), "user": user}


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserRead])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
):
    return db.query(User).order_by(User.name.asc()).all()


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
):
    user = User(
        name=data.name,
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=data.is_active,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        ) from exc
    db.refresh(user)
    write_audit_log(
        db,
        user_id=current_user.id,
        action="create_user",
        resource="users",
        resource_id=str(user.id),
        request=request,
        status_code=201,
    )
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"] is not None:
        update_data["email"] = str(update_data["email"]).lower()
    if "password" in update_data:
        user.password_hash = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(user, key, value)

    if user.id == current_user.id and user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No puedes quitarte tu propio rol administrador",
        )
    if user.id == current_user.id and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No puedes desactivar tu propio usuario",
        )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        ) from exc
    db.refresh(user)
    write_audit_log(
        db,
        user_id=current_user.id,
        action="update_user",
        resource="users",
        resource_id=str(user.id),
        request=request,
        status_code=200,
    )
    return user
