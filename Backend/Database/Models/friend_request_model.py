from pydantic import BaseModel

class FriendRequestModel(BaseModel):
    current_user_id:str
    friend_id:str


