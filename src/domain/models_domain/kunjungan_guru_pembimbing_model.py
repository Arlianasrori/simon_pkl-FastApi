from pydantic import BaseModel
from .dudi_model import DudiBase
from .guru_pembimbing_model import GuruPembimbingBase

class KunjunganGuruPembimbingBase(BaseModel):
    id : int
    tanggal_kunjungan : str
    catatan : str

class KunjunganGuruPembimbingWithDudi(KunjunganGuruPembimbingBase):
    dudi : DudiBase

class KunjunganGuruPembimbingWithGuruPembimbing(KunjunganGuruPembimbingBase):
    guru_pembimbing : GuruPembimbingBase

class KunjunganGuruPembimbingWithDudiGuruPembimbing(KunjunganGuruPembimbingBase):
    dudi : DudiBase
    guru_pembimbing : GuruPembimbingBase