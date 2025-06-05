from pydantic import BaseModel

class UserSearchRequestModel(BaseModel):
    username:str

 