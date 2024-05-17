from datetime import datetime
from typing import Generic, Type, TypeVar
from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.db import Base, get_db
from core.errors import MissingResources

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session = Depends(get_db)):
        self._db = db
        self.model = model

    def get_or_raise_exception(self, id: int) -> ModelType:
        query_result = self._db.query(self.model).filter(self.model.id == id).first()
        if not query_result:
            raise MissingResources("ID not found")
        return query_result

    def get_by_auth_id(self, auth_id) -> ModelType:
        query_result = self._db.query(self.model).filter(self.model.auth_id == auth_id)
        if not query_result:
            return None
        return query_result, query_result.first()

    def _get_query_by_id(self, id):
        query_result = self._db.query(self.model).filter(self.model.id == id)
        if not query_result.first():
            raise MissingResources("Item with ID doesn't exist")
        return query_result

    async def create(self, data_obj: CreateSchemaType) -> ModelType:
        data_dict = data_obj.model_dump(exclude_none=True)
        rsp_result = self.model(**data_dict)
        self._db.add(rsp_result)
        self._db.commit()
        self._db.refresh(rsp_result)

        return rsp_result

    async def get_username(self, id: str) -> bool:
        query_result = self._db.query(self.model).filter(self.model.id == id).first()
        if not query_result:
            return None
        return True

    async def delete(self, id) -> bool:
        query = self._get_query_by_id(id)
        query.delete(synchronize_session=False)
        self._db.commit()
        return True

    async def update(self, id, data_obj: UpdateSchemaType) -> UpdateSchemaType:
        query = self._get_query_by_id(id)
        data_obj["updated_timestamp"] = datetime.utcnow()
        query.update(data_obj, synchronize_session=False)
        self._db.commit()
        return data_obj

    def get_by_username(self, username: str) -> str:
        username = (
            self._db.query(self.model).filter(self.model.username == username).first()
        )
        if not username:
            return None
        return username.username
