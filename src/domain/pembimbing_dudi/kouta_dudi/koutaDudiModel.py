from pydantic import BaseModel

class AddKoutaDudiBody(BaseModel) :
    jumlah_pria : int
    jumlah_wanita : int

class UpdateKoutaDudiBody(BaseModel) :
    jumlah_pria : int | None
    jumlah_wanita : int | None