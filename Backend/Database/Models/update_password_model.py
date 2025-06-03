from pydantic import BaseModel

class UpdatePassword(BaseModel) :
    email: str
    new_password: str
    code :int

