from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from datetime import datetime

class User(BaseModel):
    name: str = Field(...)
    last_name: str  = Field(default="")
    email: str =  Field(...)
    password: str = Field(...)
    profile_image: str   = Field(default="")
    online_status: bool  = Field(default=False)
    friend_requests: List[UUID] = Field(default_factory=list)
    friends: List[UUID] = Field(default_factory=list)
    posts: List[UUID] = Field(default_factory=list)
 