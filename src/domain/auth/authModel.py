from pydantic import BaseModel
from ..models_domain.auth_model import RoleEnum

class LoginBody(BaseModel) :
    textBody : str
    password : str

class ResponseForgotPassword(BaseModel) :
    id : int
    role : RoleEnum
    email : str
