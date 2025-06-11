from pydantic import BaseModel

class LikeAPostRequestModel(BaseModel):
    post_id:str
    token: str


