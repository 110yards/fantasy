from google.cloud.firestore_v1.base_document import BaseDocumentReference
from api.app.core.firestore_proxy import Query
from typing import Any, Dict, Generic, List, TypeVar, Union
import uuid

from api.app.core.base_entity import BaseEntity
from google.cloud.firestore_v1.transaction import Transaction

T = TypeVar("T", bound=BaseEntity)


class MockFirestoreProxy(Generic[T]):
    _max_attempts = 1
    _id = 0

    def __init__(self, entities: List[BaseEntity] = None):
        self.entities = {}

        entities = entities or []
        for entity in entities:
            self.entities[entity.id] = entity

    # mock transaction handlers
    def _clean_up(self):
        pass

    def _begin(self, retry_id=None):
        pass

    def _rollback(self):
        pass

    def _commit(self):
        pass

    def create_transaction(self, **kwargs) -> Transaction:
        return self

    def document(self, path) -> BaseDocumentReference:
        return None

    def get(self, collection_path: str, id, transaction: Transaction = None) -> T:
        return self.entities.get(id, None)

    def get_all(self, collection_path: str, transaction: Transaction = None) -> List[T]:
        return list(self.entities.values())

    def where(self, collection_path: str, queries: Union[Query, List[Query]]):
        raise NotImplementedError()

    def create(self, collection_path: str, entity: T, transaction: Transaction = None) -> T:
        entity.id = str(uuid.uuid4())
        self.entities[entity.id] = entity
        return entity

    def update(self, collection_path: str, entity: T, transaction: Transaction = None) -> T:
        if entity.id not in self.entities:
            raise IndexError()

        self.entities[entity.id] = entity
        return entity

    def set(self, collection_path: str, entity: T, transaction: Transaction = None) -> T:
        self.entities[entity.id] = entity
        return entity

    def delete(self, collection_path: str, entity_id: T, transaction: Transaction = None):
        self.entities.pop(entity_id, None)

    def partial_update(self, collection_path: str, entity_id: str, updates: Dict[str, Any], transaction: Transaction = None):
        entity: BaseEntity = self.entities[entity_id]

        for key in updates:
            value = updates[key]
            if "." in key:
                parts = key.split(".")
                last_key = parts[-1]
                prop = entity
                for parent_key in parts[:-1]:
                    prop = getattr(prop, parent_key)

                setattr(prop, last_key, value)
            else:
                setattr(entity, key, value)
