from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class User(BaseModel):
    id: UUID
    name: str
    last_name: str
    email: str
    password: str
    profile_image: str
    online_status: bool
    friend_requests: List[UUID]
    friends: List[UUID]
    posts: List[UUID]
