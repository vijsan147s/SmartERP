from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.models import UserRole, UserStatus, AttendanceStatus, FeeStatus, PaymentMethod, Grade


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
    roles: List[str] = []


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric with optional _ or -")
        return v.lower()


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    roles: List[UserRole] = [UserRole.STUDENT]


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    status: Optional[UserStatus] = None
    roles: Optional[List[UserRole]] = None
    is_superuser: Optional[bool] = None


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hashed_password: str
    status: UserStatus
    last_login_at: Optional[datetime] = None
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    roles: List["RoleResponse"] = []


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: UserStatus
    last_login_at: Optional[datetime] = None
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    roles: List["RoleResponse"] = []


class RoleBase(BaseModel):
    name: UserRole
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    user: UserResponse
    tokens: Token


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List
    total: int
    page: int
    page_size: int
    total_pages: int