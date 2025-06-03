from pydantic import BaseModel

class ForgetPasswordRequestModel(BaseModel):
    email: str
