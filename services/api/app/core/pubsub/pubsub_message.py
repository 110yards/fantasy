from typing import Dict, Optional, Union
from pydantic import BaseModel


class PubSubMessage(BaseModel):
    attributes: Optional[Dict]
    data: Union[str, Dict]
    message_id: Optional[str]
    publish_time: Optional[str]
