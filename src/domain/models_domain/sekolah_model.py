from pydantic import BaseModel

from .alamat_model import AlamatBase

class AlamatSekolah(AlamatBase) :
    id_sekolah : int

class SekolahBase(BaseModel) :
    id : int
    npsn : str
    nama : str
    logo : str | None

class SekolahWithAlamat(SekolahBase) :
    alamat : AlamatSekolah

class AdminBase(BaseModel) :
    id : int
    username : str

class kepalaSekolahBase(BaseModel) :
    nama : str
    nip : str

class MoreSekolahBase(SekolahBase) :
    admin : list[AdminBase] = []
    alamat : AlamatSekolah | None = None
    kepala_sekolah : kepalaSekolahBase | None = None

class AdminWithSekolah(BaseModel) :
    id : int
    id_sekolah : int
    username : str
    sekolah : SekolahBase

class TahunSekolahBase(BaseModel) :
    id : int
    tahun : str
    id_sekolah : int

