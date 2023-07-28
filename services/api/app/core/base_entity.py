import hashlib
import json
from typing import Optional

from pydantic import BaseModel

from app.core.annotate_args import annotate_args


@annotate_args
class BaseEntity(BaseModel):
    id: Optional[str]
    hash: Optional[str]

    # Workaround for serializing properties with pydantic until
    # https://github.com/samuelcolvin/pydantic/issues/935
    # is solved
    @classmethod
    def get_properties(cls):
        return [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property) and prop not in ("__values__", "fields")]

    def dict(self, *args, **kwargs):
        self.__dict__.update({prop: getattr(self, prop) for prop in self.get_properties()})
        return super().dict(*args, **kwargs)

    def calculate_hash(self) -> str:
        self.hash = hashlib.md5(json.dumps(self.dict()).encode("utf-8")).hexdigest()
