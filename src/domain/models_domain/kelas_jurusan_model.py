from pydantic import BaseModel

class JurusanBase(BaseModel):
    id : int
    nama : str  
    id_sekolah : int
    id_tahun : int

class KelasBase(BaseModel) :
    id : int
    nama : str
    tahun : str
    id_jurusan : int

class MoreJurusanBase(JurusanBase) :
    kelas : list[KelasBase] = []

class KelasWithJurusan(BaseModel) :
    id : int
    nama : str
    tahun : str
    id_jurusan : int
    jurusan : JurusanBase
