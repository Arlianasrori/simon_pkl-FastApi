from pydantic import BaseModel
from datetime import date as Date
from fastapi import Form, UploadFile
from typing import Optional

class AddLaporanPklDudiBody(BaseModel):
    tanggal: Date
    topik_pekerjaan : str
    rujukan_kompetensi_dasar : str

class UpdateLaporanPklDudiBody(BaseModel):
    tanggal: Date | None = None
    topik_pekerjaan : str | None = None
    rujukan_kompetensi_dasar : str | None = None