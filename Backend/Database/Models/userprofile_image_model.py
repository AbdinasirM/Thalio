from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime

class UserProfileImage(BaseModel):
    id: UUID
    file_name: str
    url: HttpUrl
    uploaded_at: datetime
    file_type: str  # e.g., 'image/jpeg'
    size_in_kb: int
