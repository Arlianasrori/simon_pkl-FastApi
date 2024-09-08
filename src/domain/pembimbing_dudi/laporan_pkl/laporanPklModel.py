from pydantic import BaseModel
from datetime import date as Date
from fastapi import Form, UploadFile
from typing import Optional

class AddLaporanPklDudiBody(BaseModel):
    tanggal: Date
    keterangan: str
    id_siswa: int

class UpdateLaporanPklDudiBody(BaseModel):
    tanggal: Date | None = None
    keterangan: str | None = None
    id_siswa: int | None = None