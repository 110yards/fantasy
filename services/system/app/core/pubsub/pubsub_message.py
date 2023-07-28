from typing import Dict, Optional, Union

from pydantic import BaseModel


class PubSubMessage(BaseModel):
    attributes: Optional[Dict] = None
    data: Union[str, Dict]
    message_id: Optional[str] = None
    publish_time: Optional[str] = None
