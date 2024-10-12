from pydantic import BaseModel
from datetime import date as Date

class AddLaporanKendalaDudiBody(BaseModel):
    tanggal : Date | None = None
    id_siswa : int
    kendala : str
    deskripsi : str | None = None

class UpdateLaporanKendalaDudiBody(BaseModel):
    tanggal : Date | None = None
    kendala : str | None = None
    deskripsi : str | None = None
    id_siswa : int