

from pydantic import BaseModel


class RTDBEntity(BaseModel):
    key: str
    data: BaseModel
