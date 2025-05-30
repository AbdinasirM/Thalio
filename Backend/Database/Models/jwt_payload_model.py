from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime

class Payload(BaseModel):
    subject:  str 
    username:  str
    user_id: int 
    created_at: datetime
    expires_at:datetime 

    