from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime
from bson import ObjectId

class CommentRequestModel(BaseModel):
    comment_text: str
    post_id: str
    token: str
