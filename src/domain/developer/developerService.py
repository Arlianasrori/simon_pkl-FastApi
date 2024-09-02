from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload,subqueryload
# model
from ...models.sekolahModel import Sekolah,AlamatSekolah,Admin
from ..models_domain.alamat_model import AlamatBase,UpdateAlamatBody
from ..models_domain.sekolah_model import SekolahBase,SekolahWithAlamat,MoreSekolahBase,AdminWithSekolah,AdminBase
from .developerModel import AddSekolahBody,AddAdminBody,UpdateAdminBody

# common
from python_random_strings import random_strings
from ...error.errorHandling import HttpException
import os
from copy import deepcopy
from ...utils.updateTable import updateTable
from ...auth.bcrypt import bcrypt


# sekolah
async def add_sekolah(sekolah : AddSekolahBody,alamat : AlamatBase,session : AsyncSession) -> SekolahWithAlamat :
    findSekolahByNpsn = (await session.execute(select(Sekolah).where(Sekolah.npsn == sekolah.npsn))).scalar_one_or_none()
    if findSekolahByNpsn :
        raise HttpException(400,f"sekolah dengan npsn {sekolah.npsn} stelah ditambahkan")

    # sekolah mapping
    sekolahMapping = sekolah.model_dump()
    sekolahMapping.update({"id" : random_strings.random_digits(6)})
    # alamat mapping
    alamatMapping = alamat.model_dump()
    alamatMapping.update({"id_sekolah" : sekolahMapping["id"]})

    # add sekolah
    session.add(Sekolah(**sekolahMapping,alamat = AlamatSekolah(**alamatMapping)))
    await session.commit()

    return {
        "msg" : "success",
        "data" : {
            **sekolahMapping,
            "logo" : None,
            "alamat" : alamatMapping
        }
    }
    

LOGO_SEKOLAH_STORE = os.getenv("DEV_LOGO_SEKOLAH_STORE")
LOGO_SEKOLAH_BASE_URL = os.getenv("DEV_LOGO_SEKOLAH_BASE_URL")

async def add_update_foto_profile_sekolah(id_sekolah : int,logo : UploadFile,session : AsyncSession) -> SekolahBase :
    findSekolah = (await session.execute(select(Sekolah).where(Sekolah.id == id_sekolah))).scalar_one_or_none()
    if not findSekolah :
        raise HttpException(404,f"sekolah tidak ditemukan")

    ext_file = logo.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{random_strings.random_digits(12)}-{logo.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{LOGO_SEKOLAH_STORE}{file_name}"
        
    logoSekolahBefore = findSekolah.logo

    with open(file_name_save, "wb") as f:
        f.write(logo.file.read())
        findSekolah.logo = f"{LOGO_SEKOLAH_BASE_URL}/{file_name}"
    
    if logoSekolahBefore :
        print(logoSekolahBefore)
        file_nama_db_split = logoSekolahBefore.split("/")
        file_name_db = file_nama_db_split[-1]
        os.remove(f"{LOGO_SEKOLAH_STORE}/{file_name_db}")
    
    sekolahMapping = deepcopy(findSekolah.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : sekolahMapping
    }

async def getAllsekolah(session : AsyncSession) -> SekolahWithAlamat :
    sekolah = (await session.execute(select(Sekolah).options(joinedload(Sekolah.alamat)))).scalars().all()

    return {
        "msg" : "success",
        "data" : sekolah
    }

async def getSekolahById(id_sekolah : int,session : AsyncSession) -> MoreSekolahBase :
    sekolah = (await session.execute(select(Sekolah).options(subqueryload(Sekolah.admin),joinedload(Sekolah.alamat),joinedload(Sekolah.kepala_sekolah),subqueryload(Sekolah.siswa),subqueryload(Sekolah.dudi),subqueryload(Sekolah.pembimbing_dudi),subqueryload(Sekolah.guru_pembimbing)).where(Sekolah.id == id_sekolah).options(joinedload(Sekolah.alamat)))).scalar_one_or_none()
    if not sekolah :
        raise HttpException(404,f"sekolah tidak ditemukan")

    return {
        "msg" : "success",
        "data" : sekolah
    }


async def updateSekolah(id_sekolah : int,sekolah : UpdateAlamatBody,alamat : AlamatBase,session : AsyncSession) -> SekolahWithAlamat :
    findSekolah = (await session.execute(select(Sekolah).options(joinedload(Sekolah.alamat)).where(Sekolah.id == id_sekolah))).scalar_one_or_none()
    if not findSekolah :
        raise HttpException(404,f"sekolah tidak ditemukan")

    if sekolah :
        updateTable(sekolah,findSekolah)
    
    if alamat :
        updateTable(alamat,findSekolah.alamat)

    sekolahDictCopy = deepcopy(findSekolah.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : sekolahDictCopy
    }

async def deleteSekolah(id_sekolah : int,session : AsyncSession) -> SekolahBase :
    findSekolah = (await session.execute(select(Sekolah).where(Sekolah.id == id_sekolah))).scalar_one_or_none()
    if not findSekolah :
        raise HttpException(404,f"sekolah tidak ditemukan")

    sekolahDictCopy = deepcopy(findSekolah.__dict__)
    await session.delete(findSekolah)
    await session.commit()      

    return {
        "msg" : "success",
        "data" : sekolahDictCopy
    }
    
# admin sekolah

async def add_admin_sekolah(admin : AddAdminBody,session : AsyncSession) -> AdminWithSekolah :
    findSekolah = (await session.execute(select(Sekolah).where(Sekolah.id == admin.id_sekolah))).scalar_one_or_none()

    if not findSekolah :
        raise HttpException(404,"sekolah tidak ditemukan")
    
    findAdminByUsername = (await session.execute(select(Admin).where(Admin.username == admin.username))).scalar_one_or_none()

    if findAdminByUsername :
        raise HttpException(400,f"admin dengan username {admin.username} telah digunakan")
    
    adminMApping = admin.model_dump()
    adminMApping.update({"id" : random_strings.random_digits(6),"password" : bcrypt.create_hash_password(admin.password)})

    sekolahDictCopy = deepcopy(findSekolah.__dict__)
    session.add(Admin(**adminMApping))
    await session.commit()

    return {
        "msg" : 'success',
        "data" : {
            **adminMApping,
            "sekolah" : sekolahDictCopy
        }
    }
async def get_all_admin_sekolah(session : AsyncSession) -> AdminWithSekolah :
    admin = (await session.execute(select(Admin).options(joinedload(Admin.sekolah)))).scalars().all()

    return {
        "msg" : "success",
        "data" : admin
    }

async def get_admin_sekolah_by_id(id_admin : int,session : AsyncSession) -> AdminWithSekolah :
    admin = (await session.execute(select(Admin).options(joinedload(Admin.sekolah)).where(Admin.id == id_admin))).scalar_one_or_none()
    if not admin :
        raise HttpException(404,f"admin tidak ditemukan")

    return {
        "msg" : "success",
        "data" : admin
    }

async def update_admin_sekolah(id_admin : int,admin : UpdateAdminBody,session : AsyncSession) -> AdminWithSekolah :
    findAdmin = (await session.execute(select(Admin).options(joinedload(Admin.sekolah)).where(Admin.id == id_admin))).scalar_one_or_none()
    if not findAdmin :
        raise HttpException(404,f"admin tidak ditemukan")

    if admin :
        updateTable(admin,findAdmin)

    adminDictCopy = deepcopy(findAdmin.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : adminDictCopy
    }
        

async def delete_admin_sekolah(id_admin : int,session : AsyncSession) -> AdminBase :
    findAdmin = (await session.execute(select(Admin).where(Admin.id == id_admin))).scalar_one_or_none()
    if not findAdmin :
        raise HttpException(404,f"admin tidak ditemukan")

    adminDictCopy = deepcopy(findAdmin.__dict__)
    await session.delete(findAdmin)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : adminDictCopy
    }
    

