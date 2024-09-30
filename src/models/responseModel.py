from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    msg : str
    data: T

class ResponseModelJustMsg(BaseModel) :
    msg : str
