import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VirtualPubSubPayload(BaseModel):
    id: str = uuid.uuid4().hex
    topic: str
    data: Optional[dict] = None
    timestamp: datetime
