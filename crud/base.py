from typing import Generic, Type, TypeVar
from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.db import Base, get_db
from core.errors import MissingResource

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session = Depends(get_db)):
        self._db = db
        self.model = model

    def get_or_raise_execption(self, id: int) -> ModelType:
        query_result = self._db.query(self.model).filter(id == id).first()
        if not query_result:
            raise MissingResource("Item with ID doesn't exist")
        return query_result

    async def create(self, data_obj: CreateSchemaType) -> ModelType:
        data_dict = data_obj.model_dump(exclude_none=True)
        rsp_result = self.model(**data_dict)
        self._db.add(rsp_result)
        self._db.commit()
        self._db.refresh(rsp_result)
        return rsp_result
