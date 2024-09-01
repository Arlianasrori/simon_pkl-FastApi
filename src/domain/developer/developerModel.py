from pydantic import BaseModel

class Developer(BaseModel) :
    id : int
    username : str

class AddSekolahBody(BaseModel) :
    npsn : str
    nama : str

class UpdateSekolahBody(BaseModel) :
    npsn : str | None = None
    nama : str | None = None