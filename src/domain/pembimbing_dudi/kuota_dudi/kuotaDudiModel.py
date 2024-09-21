from pydantic import BaseModel

class AddKuotaJurusanBody(BaseModel) :
    id_jurusan : int
    jumlah_pria : int
    jumlah_wanita : int

class UpdateKuotaJurusanBody(BaseModel) :
    id : int 
    jumlah_pria : int | None = None
    jumlah_wanita : int | None = None

class AddKuotaDudiBody(BaseModel) :
    jumlah_pria : int
    jumlah_wanita : int
    kuota_jurusan : list[AddKuotaJurusanBody] | None = None

class UpdateKuotaDudiBody(BaseModel) :
    jumlah_pria : int | None = None
    jumlah_wanita : int | None = None
    kuota_jurusan : list[UpdateKuotaJurusanBody] | None = None