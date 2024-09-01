from pydantic import BaseModel

class LoginBody(BaseModel) :
    textBody : str
    password : str