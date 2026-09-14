from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.database import SessionLocal
from app.core.security import decode_token, verify_token_type
from app.core.config import settings
from app.models import User, UserRole
from app.crud import crud_user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
http_bearer = HTTPBearer(auto_error=False)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or not verify_token_type(payload, "access"):
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    user = crud_user.get(db, id=int(user_id))
    if not user:
        raise credentials_exception
    
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.status != "ACTIVE":
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


def require_roles(*allowed_roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_roles = [r.name for r in current_user.roles]
        if UserRole.ADMIN in user_roles or current_user.is_superuser:
            return current_user
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


require_admin = require_roles(UserRole.ADMIN)
require_manager = require_roles(UserRole.ADMIN, UserRole.MANAGER)
require_employee = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE)
require_student = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.STUDENT)

require_any = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE, UserRole.STUDENT)