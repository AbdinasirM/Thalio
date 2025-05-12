from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime
from comment_model import Comment  # Be cautious: circular import?

class Post(BaseModel):
    id: UUID
    post_text: str
    post_image: str  # Required (could be a URL or path)
    created_at: datetime
    likes: int # Array of User IDs who liked
    comments: List[Comment] # Array of embedded Comment objects or Comment IDs
    created_user: UUID # User ID of the author



