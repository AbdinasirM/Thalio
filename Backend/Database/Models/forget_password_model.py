from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime

class Forget_Password(BaseModel):
    email: str
    code: int
    created_at: datetime
    expires_at:datetime 

    