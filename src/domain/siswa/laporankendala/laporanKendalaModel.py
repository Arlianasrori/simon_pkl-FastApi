from pydantic import BaseModel
from datetime import date as Date

class AddLaporanKendalaBody(BaseModel):
    tanggal : Date | None = None
    kendala : str
    deskripsi : str | None = None

class UpdateLaporanKendalaBody(BaseModel):
    tanggal : Date | None = None
    kendala : str | None = None
    deskripsi : str | None = None