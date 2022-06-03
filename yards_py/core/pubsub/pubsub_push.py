from yards_py.core.logging import Logger
from yards_py.core.abort import abort_bad_request
from typing import Dict, Optional
from yards_py.core.pubsub.pubsub_message import PubSubMessage
from pydantic import BaseModel
import base64
import json


class PubSubPush(BaseModel):
    message: PubSubMessage
    subscription: Optional[str]

    def get_data(self) -> Dict:
        Logger.debug("Getting data from PubSubPush", extra=self.dict())
        data = self.message.data
        if not data:
            abort_bad_request()

        if isinstance(data, dict):
            return data
        else:
            data = base64.b64decode(data)
            return json.loads(data)
