from pydantic import BaseModel
from typing import Any, Dict, List
from uuid import UUID
from datetime import datetime

class Payload(BaseModel):
    subject: str
    user_id: str
    email: str
    iat: datetime
    exp: datetime
