from pydantic import BaseModel

class AddJurusanBody(BaseModel) :
    nama : str
    id_tahun : int

class UpdateJurusanBody(BaseModel) :
    nama : str | None = None

class AddKelasBody(BaseModel) :
    nama : str
    tahun : str
    id_jurusan : int

class UpdateKelasBody(BaseModel) :
    nama : str | None = None
    tahun : str | None = None
    id_jurusan : int | None = None