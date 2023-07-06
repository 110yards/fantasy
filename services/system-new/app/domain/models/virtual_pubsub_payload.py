import uuid
from datetime import datetime

from pydantic import BaseModel


class VirtualPubSubPayload(BaseModel):
    message_id: str = uuid.uuid4().hex
    topic: str
    data: dict
    timestamp: datetime
