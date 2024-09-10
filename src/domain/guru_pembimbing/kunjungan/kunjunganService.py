from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from .kunjunganModel import AddKunjunganBody,UpdateKunjunganBody,ResponseLaporanPklDudiPag
from ...models_domain.kunjungan_guru_pembimbing_model import KunjunganGuruPembimbingWithDudi
from ....models.guruPembimbingModel import GuruPembimbing,KunjunganGuruPembimbingPKL
from ....models.dudiModel import Dudi

# common
from ....error.errorHandling import HttpException
import math
from python_random_strings import random_strings

async def addKunjungan(id_guru : int,kunjungan : AddKunjunganBody,session : AsyncSession) -> KunjunganGuruPembimbingWithDudi :
    getDudi = (await session.execute(select(Dudi).where(Dudi.id == kunjungan.id_dudi))).scalar_one_or_none()
    if getDudi is None :
        raise HttpException(404,"dudi tidak ditemukan")
    
    
    kunjunganMapping = kunjungan.model_dump()
    kunjunganMapping.update({"id" : random_strings.random_digits(6),"id_guru_pembimbing" : id_guru})
    
    # nanti lanjut lagi add ke dataabase
