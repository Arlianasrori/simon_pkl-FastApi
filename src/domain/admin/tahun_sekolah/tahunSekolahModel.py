from pydantic import BaseModel

class AddTahunSekolahBody(BaseModel) :
    tahun : str

class UpdateTahunSekolahBody(BaseModel) :
    tahun : str | None = None