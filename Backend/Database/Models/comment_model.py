from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime
from bson import ObjectId

class Comment(BaseModel):
    comment_id:UUID
    comment_text: str
    created_at: datetime
    user_id: str    # just store the user's UUID
    post_id: str    # just store the post's UUID
    