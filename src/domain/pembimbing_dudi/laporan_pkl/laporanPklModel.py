from pydantic import BaseModel
from datetime import date as Date
from fastapi import Form, UploadFile
from typing import Optional

class LaporanPklDudiBase(BaseModel):
    id: int
    tanggal: Date
    keterangan: str
    id_siswa: int
    file_laporan: str

    @classmethod
    def as_form(
        cls,
        id: int = Form(...),
        tanggal: Date = Form(...),
        keterangan: str = Form(...),
        id_siswa: int = Form(...),
        file_laporan: UploadFile = Form(...)
    ):
        return cls(
            id=id,
            tanggal=tanggal,
            keterangan=keterangan,
            id_siswa=id_siswa,
            file_laporan=file_laporan.filename
        ), file_laporan
