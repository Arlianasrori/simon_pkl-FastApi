from pydantic import BaseModel

class ResponseAuthToken(BaseModel) :
    access_token : str
    refresh_token : str
