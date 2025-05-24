from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime

class Comment(BaseModel):
    comment_text: str
    created_at: datetime
    user_id: UUID  # just store the user's UUID
    post_id: UUID  # just store the post's UUID
    