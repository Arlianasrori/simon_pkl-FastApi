from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload

# models
from .siswaModel import AddSiswaBody,UpdateSiswaBody,ResponseSiswaPag
from ...models_domain.siswa_model import SiswaBase,MoreSiswa,DetailSiswa
from ...models_domain.alamat_model import AlamatBase,UpdateAlamatBody
from ....models.siswaModel import Siswa,AlamatSiswa,Jurusan,Kelas,StatusPKLEnum
from ....models.guruPembimbingModel import GuruPembimbing
from ....models.sekolahModel import TahunSekolah

# common
from copy import deepcopy
import math
import os
from python_random_strings import random_strings
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable
from ....auth.bcrypt import bcrypt

async def addSiswa(id_sekolah : int,siswa : AddSiswaBody,alamat : AlamatBase,session : AsyncSession) -> MoreSiswa :
    """
    Add a new student to the database.

    Args:
        id_sekolah (int): The school ID.
        siswa (AddSiswaBody): The student data to be added.
        alamat (AlamatBase): The address data for the student.
        session (AsyncSession): The database session.

    Returns:
        MoreSiswa: The newly added student with additional information.

    Raises:
        HttpException: If the specified school year, student NIS, jurusan, kelas, or guru pembimbing is not found or already exists.
    """
    findTahun = (await session.execute(select(TahunSekolah).where(TahunSekolah.id == siswa.id_tahun))).scalar_one_or_none()
    if not findTahun :
        raise HttpException(400,f"Tahun Sekolah dengan id {siswa.id_tahun} tidak ditemukan")
    
    findSiswa = (await session.execute(select(Siswa).where(Siswa.nis == siswa.nis))).scalar_one_or_none()
    if findSiswa :
        raise HttpException(400,f"Siswa dengan NIS {siswa.nis} sudah ada")
    
    findJurusan = (await session.execute(select(Jurusan).where(Jurusan.id == siswa.id_jurusan))).scalar_one_or_none()
    if not findJurusan :
        raise HttpException(400,f"Jurusan dengan id {siswa.id_jurusan} tidak ditemukan")
    
    findKelas = (await session.execute(select(Kelas).where(Kelas.id == siswa.id_kelas))).scalar_one_or_none()
    if not findKelas :
        raise HttpException(400,f"Kelas dengan id {siswa.id_kelas} tidak ditemukan")
    
    if siswa.id_guru_pembimbing :
        findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == siswa.id_guru_pembimbing))).scalar_one_or_none()
        if not findGuruPembimbing :
            raise HttpException(400,f"Guru Pembimbing dengan id {siswa.id_guru_pembimbing} tidak ditemukan")
    
    siswaMapping = siswa.model_dump()
    siswaMapping.update({"id" : random_strings.random_digits(6),"id_sekolah" : id_sekolah,"status" : StatusPKLEnum.belum_pkl.value,"password" : bcrypt.create_hash_password(siswa.password)})
    alamatMapping = alamat.model_dump()
    alamatMapping.update({"id_siswa" : siswaMapping["id"]})
    
    session.add(Siswa(**siswaMapping,alamat = AlamatSiswa(**alamatMapping)))
    await session.commit()
    findSiswa = (await session.execute(select(Siswa).options(joinedload(Siswa.alamat),joinedload(Siswa.kelas),joinedload(Siswa.jurusan),joinedload(Siswa.guru_pembimbing)).where(Siswa.id == siswaMapping["id"]))).scalar_one_or_none()
    
    return {
        "msg" : "success",
        "data" : findSiswa
    }

PROFILE_STORE = os.getenv("DEV_FOTO_PROFILE_SISWA_STORE")
PROFILE_BASE_URL = os.getenv("DEV_FOTO_PROFILE_SISWA_BASE_URL")

async def add_update_foto_profile(id : int,id_sekolah : int,foto_profile : UploadFile,session : AsyncSession) -> SiswaBase :
    """
    Add or update the profile photo of a student.

    Args:
        id (int): The student ID.
        id_sekolah (int): The school ID.
        foto_profile (UploadFile): The profile photo file to be uploaded.
        session (AsyncSession): The database session.

    Returns:
        SiswaBase: The updated student information.

    Raises:
        HttpException: If the student is not found or if the file is not an image.
    """
    findSiswa = (await session.execute(select(Siswa).where(and_(Siswa.id == id,Siswa.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findSiswa :
        raise HttpException(404,f"siswa tidak ditemukan")

    ext_file = foto_profile.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{random_strings.random_digits(12)}-{foto_profile.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{PROFILE_STORE}{file_name}"
        
    fotoProfileBefore = findSiswa.foto_profile

    with open(file_name_save, "wb") as f:
        f.write(foto_profile.file.read())
        print(PROFILE_BASE_URL)
        findSiswa.foto_profile = f"{PROFILE_BASE_URL}/{file_name}"
    
    if fotoProfileBefore :
        print(fotoProfileBefore)
        file_nama_db_split = fotoProfileBefore.split("/")
        file_name_db = file_nama_db_split[-1]
        os.remove(f"{PROFILE_STORE}/{file_name_db}")
    
    siswaDictCopy = deepcopy(findSiswa.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : siswaDictCopy
    }

async def getAllSiswa(page : int | None,id_sekolah : int,id_tahun : int,session : AsyncSession) -> list[MoreSiswa] | ResponseSiswaPag :
    """
    Retrieve all students for a specific school and year.

    Args:
        page (int | None): The page number for pagination (optional).
        id_sekolah (int): The school ID.
        id_tahun (int): The year ID.
        session (AsyncSession): The database session.

    Returns:
        list[MoreSiswa] | ResponseSiswaPag: A list of students or a paginated response.
    """
    statementSelectSiswa = select(Siswa).options(joinedload(Siswa.alamat),joinedload(Siswa.kelas),joinedload(Siswa.jurusan),joinedload(Siswa.guru_pembimbing)).where(and_(Siswa.id_sekolah == id_sekolah,Siswa.id_tahun == id_tahun))

    if page :
        findSiswa = (await session.execute(statementSelectSiswa.limit(10).offset(10 * (page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(Siswa.id))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "data" : findSiswa,
                "count_data" : len(findSiswa),
                "count_page" : countPage
            }
        }
    else :
        findSiswa = (await session.execute(statementSelectSiswa)).scalars().all()
        return {
            "msg" : "success",
            "data" : findSiswa
        }

async def getSiswaById(id_siswa : int,id_sekolah : int,session : AsyncSession) -> DetailSiswa :
    """
    Retrieve a specific student by ID.

    Args:
        id_siswa (int): The student ID.
        id_sekolah (int): The school ID.
        session (AsyncSession): The database session.

    Returns:
        DetailSiswa: Detailed information about the student.

    Raises:
        HttpException: If the student is not found.
    """
    findSiswa = (await session.execute(select(Siswa).options(joinedload(Siswa.alamat),joinedload(Siswa.kelas),joinedload(Siswa.jurusan),joinedload(Siswa.guru_pembimbing),joinedload(Siswa.dudi),joinedload(Siswa.pembimbing_dudi)).where(and_(Siswa.id == id_siswa,Siswa.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findSiswa :
        raise HttpException(400,f"Siswa dengan id {id_siswa} tidak ditemukan")
    return {
        "msg" : "success",
        "data" : findSiswa
    }

async def updateSiswa(id_siswa : int,id_sekolah : int,siswa : UpdateSiswaBody,alamat : UpdateAlamatBody,session : AsyncSession) -> MoreSiswa :
    """
    Update a student's information.

    Args:
        id_siswa (int): The student ID.
        id_sekolah (int): The school ID.
        siswa (UpdateSiswaBody): The updated student data.
        alamat (UpdateAlamatBody): The updated address data.
        session (AsyncSession): The database session.

    Returns:
        MoreSiswa: The updated student information.

    Raises:
        HttpException: If the student, NIS, jurusan, kelas, or guru pembimbing is not found or already exists.
    """
    findSiswa = (await session.execute(select(Siswa).options(joinedload(Siswa.alamat),joinedload(Siswa.kelas),joinedload(Siswa.jurusan),joinedload(Siswa.guru_pembimbing)).where(and_(Siswa.id == id_siswa,Siswa.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findSiswa :
        raise HttpException(400,f"Siswa dengan id {id_siswa} tidak ditemukan")
    
    if siswa.nis :
        findSiswaByNis = (await session.execute(select(Siswa).where(and_(Siswa.nis == siswa.nis,Siswa.id != id_siswa)))).scalar_one_or_none()
        if findSiswaByNis :
            raise HttpException(400,f"Siswa dengan NIS {siswa.nis} sudah ada")
    if siswa.id_jurusan :
        findJurusan = (await session.execute(select(Jurusan).where(Jurusan.id == siswa.id_jurusan))).scalar_one_or_none()
        if not findJurusan :
            raise HttpException(400,f"Jurusan dengan id {siswa.id_jurusan} tidak ditemukan")
    if siswa.id_kelas :
        findKelas = (await session.execute(select(Kelas).where(Kelas.id == siswa.id_kelas))).scalar_one_or_none()
        if not findKelas :
            raise HttpException(400,f"Kelas dengan id {siswa.id_kelas} tidak ditemukan")
    print(siswa.__dict__)
    if siswa.id_guru_pembimbing :
        findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == siswa.id_guru_pembimbing))).scalar_one_or_none()
        print(findGuruPembimbing)

        if not findGuruPembimbing :
            raise HttpException(400,f"Guru Pembimbing dengan id {siswa.id_guru_pembimbing} tidak ditemukan")
    if siswa.model_dump(exclude_unset=True) :
        updateTable(siswa,findSiswa)
    
    if alamat.model_dump(exclude_unset=True) :
        updateTable(alamat,findSiswa.alamat)
    
    siswaDictCopy = deepcopy(findSiswa.__dict__)
    await session.commit()
    return {
        "msg" : "success",
        "data" : siswaDictCopy
    }
     

async def deleteSiswa(id_siswa : int,id_sekolah : int,session : AsyncSession) -> SiswaBase :
    """
    Delete a student from the database.

    Args:
        id_siswa (int): The student ID.
        id_sekolah (int): The school ID.
        session (AsyncSession): The database session.

    Returns:
        SiswaBase: The deleted student information.

    Raises:
        HttpException: If the student is not found.
    """
    findSiswa = (await session.execute(select(Siswa).where(and_(Siswa.id == id_siswa,Siswa.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findSiswa :
        raise HttpException(400,f"Siswa dengan id {id_siswa} tidak ditemukan")
    siswaDictCopy = deepcopy(findSiswa.__dict__)
    await session.delete(findSiswa)
    await session.commit()
    return {
        "msg" : "success",
        "data" : siswaDictCopy
    }