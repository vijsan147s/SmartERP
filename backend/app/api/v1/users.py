from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db, require_admin
from app.crud import crud_user
from app.schemas.auth import UserCreate, UserUpdate, UserResponse, PaginatedResponse
from app.models import User, UserRole

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if crud_user.get_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if crud_user.get_by_username(db, user.username):
        raise HTTPException(status_code=409, detail="Username already taken")
    
    from app.core.security import get_password_hash
    user_data = user.model_dump(exclude={"password", "roles"})
    user_data["hashed_password"] = get_password_hash(user.password)
    user_data["status"] = "ACTIVE"
    
    user_obj = User(**user_data)
    db.add(user_obj)
    db.flush()
    
    roles = db.query(crud_user.crud_role.model).filter(
        crud_user.crud_role.model.name.in_(user.roles)
    ).all()
    user_obj.roles = roles
    
    db.commit()
    db.refresh(user_obj)
    return user_obj


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_admin)])
def get_users(
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    users = crud_user.get_multi_with_roles(db, skip=(page-1)*page_size, limit=page_size, search=search, status=status)
    total = crud_user.get_count_with_filters(db, search=search, status=status)
    
    items = [UserResponse.model_validate(u) for u in users]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = crud_user.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    if "roles" in update_data:
        roles = db.query(crud_user.crud_role.model).filter(
            crud_user.crud_role.model.name.in_(update_data.pop("roles"))
        ).all()
        user.roles = roles
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    crud_user.remove(db, id=user_id)
    return {"message": "User deleted successfully"}