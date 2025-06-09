from pydantic import BaseModel,Field
from typing import List
from uuid import UUID
from datetime import datetime
from database.Models.comment_model import Comment  

class Post(BaseModel):
    post_text: str
    post_image: str  # id 
    created_at: datetime
    likes: List[UUID] = Field(default_factory=list) # Array of User IDs who liked
    comments: List[Comment] = Field(default_factory=list) # Array of embedded Comment objects or Comment IDs
    created_user: str # User ID of the author



