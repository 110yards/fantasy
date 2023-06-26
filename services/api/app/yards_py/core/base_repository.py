from abc import abstractmethod
from typing import Callable, Generic, List, TypeVar, Union

from app.yards_py.core.base_entity import BaseEntity
from firebase_admin import firestore
from google.cloud.firestore_v1.transaction import Transaction

T = TypeVar("T", bound=BaseEntity)

# DEPRECATED


class Query:
    def __init__(self, field_path: str, op_string: str, value):
        """Create a "where" query to be used on a firestore collection.
           See
           :meth:`~google.cloud.firestore_v1.query.Query.where` for
           more information on the underlying method.
           Args:
               field_path (str): A field path (``.``-delimited list of
                   field names) for the field to filter on.
               op_string (str): A comparison operation in the form of a string.
                   Acceptable values are ``<``, ``<=``, ``==``, ``>=``
                   and ``>``.
               value (Any): The value to compare the field against in the filter.
                   If ``value`` is :data:`None` or a NaN, then ``==`` is the only
                   allowed operation.
           """
        self.field_path = field_path
        self.op_string = op_string
        self.value = value


class BaseRepository(Generic[T]):
    def __init__(self, path, construct: Callable):
        self.path = path
        self.client = firestore.client()  # type: BaseClient
        self.construct = construct

    def create_transaction(self, **kwargs) -> Transaction:
        return self.client.transaction(**kwargs)

    def get(self, id, transaction: Transaction = None) -> T:
        collection_ref = self.client.collection(self.path)
        document_ref = collection_ref.document(id)

        if transaction:
            doc = document_ref.get(transaction=transaction)
        else:
            doc = document_ref.get()

        if doc.exists:
            return self.construct(dict(doc.to_dict()))
        else:
            return None

    def get_all(self) -> List[T]:
        collection_ref = self.client.collection(self.path)
        docs = collection_ref.get()

        entities = []
        for doc in docs:
            entities.append(self.construct(doc.to_dict()))

        return entities

    def where(self, queries: Union[Query, List[Query]]):
        collection_ref = self.client.collection(self.path)
        collection_query = collection_ref

        if not isinstance(queries, list):
            queries = [queries]

        for query in queries:
            collection_query = collection_query.where(query.field_path, query.op_string, query.value)

        docs = collection_query.get()

        entities = []
        for doc in docs:
            entities.append(self.construct(doc.to_dict()))

        return entities

    @abstractmethod
    def create(self, entity: T, transaction: Transaction = None) -> T:
        collection_ref = self.client.collection(self.path)

        if entity.id is not None:
            document_ref = collection_ref.document(entity.id)
        else:
            document_ref = collection_ref.document()

        entity.id = document_ref.id

        if transaction:
            transaction.create(document_ref, entity.dict(exclude_none=True))
        else:
            document_ref.create(entity.dict(exclude_none=True))

        return entity

    @abstractmethod
    def update(self, entity: T, transaction: Transaction = None) -> T:
        collection_ref = self.client.collection(self.path)
        document_ref = collection_ref.document(entity.id)

        if transaction:
            transaction.update(document_ref, entity.dict(exclude_none=True))
        else:
            document_ref.update(entity.dict(exclude_none=True))

        return entity

    @abstractmethod
    def set(self, entity: T, transaction: Transaction = None) -> T:
        collection_ref = self.client.collection(self.path)
        document_ref = collection_ref.document(entity.id)

        if transaction:
            transaction.set(document_ref, entity.dict(exclude_none=True))
        else:
            document_ref.set(entity.dict(exclude_none=True))

        return entity

    @abstractmethod
    def delete(self, entity: T, transaction: Transaction = None):
        collection_ref = self.client.collection(self.path)
        document_ref = collection_ref.document(entity.id)

        if transaction:
            transaction.delete(document_ref)
        else:
            document_ref.delete()
