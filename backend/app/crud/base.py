from typing import Generic, TypeVar, Type, Optional, List, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_count(self, db: Session) -> int:
        return db.query(func.count(self.model.id)).scalar()

    def create(self, db: Session, *, obj_in: CreateSchemaType | dict) -> ModelType:
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def exists(self, db: Session, **filters) -> bool:
        query = db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None