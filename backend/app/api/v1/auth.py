from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.api.deps import get_db, get_current_user, require_admin
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.config import settings
from app.crud import crud_user, crud_role
from app.schemas.auth import (
    LoginRequest, LoginResponse, Token, UserCreate, UserResponse,
    PasswordChange, RoleCreate, RoleResponse
)
from app.models import User, UserRole

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = crud_user.get_by_email_or_username(db, login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "roles": [r.name.value for r in user.roles]},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "roles": [r.name.value for r in user.roles]}
    )
    
    user.last_login_at = func.now()
    db.commit()
    
    return LoginResponse(
        user=UserResponse.model_validate(user),
        tokens=Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    from app.core.security import decode_token, verify_token_type
    
    payload = decode_token(refresh_token)
    if not payload or not verify_token_type(payload, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = crud_user.get(db, id=int(user_id))
    if not user or user.status != "ACTIVE":
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "roles": [r.name.value for r in user.roles]},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id), "roles": [r.name.value for r in user.roles]}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.post("/logout")
def logout():
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/roles", response_model=RoleResponse, dependencies=[Depends(require_admin)])
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    existing = crud_role.get_by_name(db, role.name)
    if existing:
        raise HTTPException(status_code=409, detail="Role already exists")
    return crud_role.create(db, obj_in=role)


@router.get("/roles", response_model=list[RoleResponse], dependencies=[Depends(require_admin)])
def get_roles(db: Session = Depends(get_db)):
    return crud_role.get_all_active(db)


@router.post("/seed-roles", dependencies=[Depends(require_admin)])
def seed_roles(db: Session = Depends(get_db)):
    for role in UserRole:
        existing = crud_role.get_by_name(db, role)
        if not existing:
            crud_role.create(db, obj_in=RoleCreate(name=role, description=f"{role.value} role"))
    return {"message": "Roles seeded successfully"}