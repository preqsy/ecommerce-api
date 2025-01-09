from datetime import datetime
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.db import Base
from core.errors import MissingResources

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self._db = db
        self.model = model

    def get_or_raise_exception(self, id: int) -> ModelType:
        query_result = self._db.query(self.model).filter(self.model.id == id).first()
        if not query_result:
            raise MissingResources
        return query_result

    def get(self, id: int) -> Optional[ModelType]:
        query_result = self._db.query(self.model).filter(self.model.id == id).first()

        return query_result if query_result else None

    def get_multi(
        self, id: int, skip: int = 0, limit: int = 20
    ) -> Optional[list[ModelType]]:
        query_result = (
            self._db.query(self.model)
            .filter(self.model.id == id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return query_result if query_result else None

    def get_by_auth_id(self, auth_id) -> Optional[ModelType]:
        query_result = (
            self._db.query(self.model).filter(self.model.auth_id == auth_id).first()
        )
        return query_result if query_result else None

    def _get_query_by_id(self, id):
        query_result = self._db.query(self.model).filter(self.model.id == id)
        if not query_result.first():
            raise MissingResources("Item with ID doesn't exist")
        return query_result

    async def create(self, data_obj: Union[CreateSchemaType, dict]) -> ModelType:
        if isinstance(data_obj, dict):
            rsp_result = self.model(**data_obj)
            self._db.add(rsp_result)
            self._db.commit()
            self._db.refresh(rsp_result)
            return rsp_result

        data_dict = data_obj.model_dump(exclude_none=True)
        rsp_result = self.model(**data_dict)
        self._db.add(rsp_result)
        self._db.commit()
        self._db.refresh(rsp_result)

        return rsp_result

    async def delete(self, id) -> bool:
        query = self._get_query_by_id(id)
        query.delete(synchronize_session=False)
        self._db.commit()
        return True

    async def update(
        self, id, data_obj: Union[UpdateSchemaType, dict]
    ) -> Dict[str, Any]:
        query = self._get_query_by_id(id)
        if isinstance(data_obj, dict):
            data_obj["updated_timestamp"] = datetime.utcnow()
            query.update(data_obj, synchronize_session=False)
            self._db.commit()
            return data_obj
        data_dict = data_obj.model_dump(exclude_unset=True)
        data_dict["updated_timestamp"] = datetime.utcnow()
        query.update(data_dict, synchronize_session=False)
        self._db.commit()
        return data_dict

    def get_by_username(self, username: str) -> bool:
        username_query = (
            self._db.query(self.model).filter(self.model.username == username).first()
        )
        if not username_query:
            return False
        return True

    async def delete_by_auth_id(self, auth_id):
        query = (
            self._db.query(self.model)
            .filter(self.model.auth_id == auth_id)
            .delete(synchronize_session=False)
        )
        self._db.commit()
        return

    async def bulk_insert(self, data_objs: Union[CreateSchemaType]):
        data_list = [self.model(**data_obj.model_dump()) for data_obj in data_objs]
        datas = self._db.bulk_save_objects(data_list)
        self._db.commit()
        return datas
