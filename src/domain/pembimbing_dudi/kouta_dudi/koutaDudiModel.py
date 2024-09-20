from pydantic import BaseModel

class AddKoutaJurusanBody(BaseModel) :
    id_jurusan : int
    jumlah_pria : int
    jumlah_wanita : int

class UpdateKoutaJurusanBody(BaseModel) :
    id : int 
    jumlah_pria : int | None = None
    jumlah_wanita : int | None = None

class AddKoutaDudiBody(BaseModel) :
    jumlah_pria : int
    jumlah_wanita : int
    kouta_jurusan : list[AddKoutaJurusanBody] | None = None

class UpdateKoutaDudiBody(BaseModel) :
    jumlah_pria : int | None = None
    jumlah_wanita : int | None = None
    kouta_jurusan : list[UpdateKoutaJurusanBody] | None = None