
from typing import Optional
from pydantic import BaseModel
from api.app.core.annotate_args import annotate_args


@annotate_args
class BaseEntity(BaseModel):
    id: Optional[str]
