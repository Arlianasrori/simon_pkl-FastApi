from typing import Annotated
from fastapi import APIRouter, Body, Depends, Query, UploadFile
# models
# jurusan dan kelas
from ..domain.admin.jurusan_kelas.jurusanKelasModel import AddJurusanBody, UpdateJurusanBody, AddKelasBody, UpdateKelasBody
from ..domain.models_domain.kelas_jurusan_model import JurusanBase,MoreJurusanBase,KelasBase,KelasWithJurusan
from ..domain.admin.jurusan_kelas import jurusanKelasService

# tahun sekolah
from ..domain.admin.tahun_sekolah.tahunSekolahModel import AddTahunSekolahBody,UpdateTahunSekolahBody
from ..domain.admin.tahun_sekolah import tahunSekolahService
from ..domain.models_domain.sekolah_model import TahunSekolahBase

# alamat
from ..domain.models_domain.alamat_model import AlamatBase,UpdateAlamatBody
# guru pembimbing
from ..domain.admin.guru_pembimbing.guruPembimbingModel import AddGuruPembimbingBody,UpdateGuruPembimbingBody,ResponseGuruPembimbingPag
from ..domain.admin.guru_pembimbing import guruPembimbingService
from ..domain.models_domain.guru_pembimbing_model import GuruPembimbingBase,GuruPembimbingWithAlamat

# siswa
from ..domain.admin.siswa.siswaModel import AddSiswaBody,UpdateSiswaBody,ResponseSiswaPag
from ..domain.admin.siswa import siswaService
from ..domain.models_domain.siswa_model import SiswaBase,MoreSiswa

# dudi
from ..domain.admin.dudi.dudiModel import AddDudiBody,UpdateDudiBody,ResponseDudiPag
from ..domain.admin.dudi import dudiService
from ..domain.models_domain.dudi_model import DudiBase,DudiWithAlamat, DudiWithAlamatKuota

# pembimbing dudi
from ..domain.admin.pembimbing_dudi.pembimbingDudiModel import AddPembimbingDudiBody, ResponsePembimbingDudiPagination,UpdatePembimbingDudiBody
from ..domain.admin.pembimbing_dudi import pembimbingDudiService
from ..domain.models_domain.pembimbing_dudi_model import PembimbingDudiBase,PembimbingDudiWithAlamatDudi

# laporan pkl
from ..domain.admin.laporan_pkl_dudi.laporanPklDudiModel import ResponseLaporanPklDudiPag,FilterLaporanPklDudiQuery
from ..domain.admin.laporan_pkl_dudi import laporanPklDudiService
from ..domain.models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase

# laporan pkl siswa
from ..domain.admin.laporan_pkl_siswa.laporanPklSiswaModel import FilterLaporanPklSiswaQuery,ResponseLaporanPklSiswaPag
from ..domain.admin.laporan_pkl_siswa import laporanPklSiswaService
from ..domain.models_domain.laporan_pkl_siswa_model import LaporanPklSiswaBase

# absen
from ..domain.admin.absen.absenModel import FilterAbsenQuery,ResponseAbsenPag
from ..domain.models_domain.absen_model import MoreAbsen
from ..domain.admin.absen import absenService

# auth depends
from ..auth.dependsAuthMiddleware.admin.depend_auth_admin import adminAuth
from ..auth.dependsAuthMiddleware.admin.get_admin_auth import getAdminAuth

# common
from ..models.responseModel import ResponseModel
from ..db.sessionDepedency import sessionDepedency

adminRouter = APIRouter(prefix="/admin",dependencies=[Depends(adminAuth)])

# tahun sekolah
@adminRouter.post("/tahun-sekolah",response_model=ResponseModel[TahunSekolahBase],tags=["ADMIN/TAHUN SEKOLAH"])
async def addTahunSekolah(tahun : AddTahunSekolahBody,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await tahunSekolahService.addTahunSekolah(admin["id_sekolah"],tahun,session)

@adminRouter.get("/tahun-sekolah",response_model=ResponseModel[list[TahunSekolahBase]],tags=["ADMIN/TAHUN SEKOLAH"])
async def getAllTahunSekolah(admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await tahunSekolahService.getAllTahunSekolah(admin["id_sekolah"],session)

@adminRouter.put("/tahun-sekolah/{id_tahun}",response_model=ResponseModel[TahunSekolahBase],tags=["ADMIN/TAHUN SEKOLAH"])
async def updateTahunSekolah(id_tahun : int,tahun : UpdateTahunSekolahBody | None = UpdateTahunSekolahBody(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await tahunSekolahService.updateTahunSekolah(admin["id_sekolah"],id_tahun,tahun,session)

@adminRouter.delete("/tahun-sekolah/{id_tahun}",response_model=ResponseModel[TahunSekolahBase],tags=["ADMIN/TAHUN SEKOLAH"])
async def deleteTahunSekolah(id_tahun : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await tahunSekolahService.deleteTahunSekolah(admin["id_sekolah"],id_tahun,session)


# jurusan

@adminRouter.post("/jurusan",response_model=ResponseModel[JurusanBase],tags=["ADMIN/JURUSAN"])
async def addJurusan(jurusan : AddJurusanBody,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) -> JurusanBase :
    print("tes")
    return await jurusanKelasService.addJurusan(admin["id_sekolah"],jurusan,session)

@adminRouter.get("/jurusan",response_model=ResponseModel[list[JurusanBase]],tags=["ADMIN/JURUSAN"])
async def getAllJurusan(id_tahun : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.getAllJurusan(admin["id_sekolah"],id_tahun,session)

@adminRouter.get("/jurusan/{id}",response_model=ResponseModel[MoreJurusanBase],tags=["ADMIN/JURUSAN"])
async def getJurusanById(id : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.getJurusanById(id,admin["id_sekolah"],session)

@adminRouter.put("/jurusan/{id}",response_model=ResponseModel[JurusanBase],tags=["ADMIN/JURUSAN"])
async def updateJurusan(id : int,jurusan : UpdateJurusanBody | None = UpdateJurusanBody(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.updateJurusan(id,jurusan,admin["id_sekolah"],session)

@adminRouter.delete("/jurusan/{id}",response_model=ResponseModel[JurusanBase],tags=["ADMIN/JURUSAN"])
async def deleteJurusan(id : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.deleteJurusan(id,admin["id_sekolah"],session)

# kelas
@adminRouter.post("/kelas",response_model=ResponseModel[KelasBase],tags=["ADMIN/KELAS"])
async def addKelas(kelas : AddKelasBody,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.addKelas(admin["id_sekolah"],kelas,session)

@adminRouter.get("/kelas",response_model=ResponseModel[list[KelasBase]],tags=["ADMIN/KELAS"])
async def getAllKelas(id_tahun : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.getAllKelas(admin["id_sekolah"],id_tahun,session)

@adminRouter.get("/kelas/{id}",response_model=ResponseModel[KelasWithJurusan],tags=["ADMIN/KELAS"])
async def getKelasById(id : int,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await jurusanKelasService.getKelasById(id,admin["id_sekolah"],session)

@adminRouter.put("/kelas/{id}",response_model=ResponseModel[KelasBase],tags=["ADMIN/KELAS"])
async def updateKelas(id : int,kelas : UpdateKelasBody | None = UpdateKelasBody(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.updateKelas(id,admin["id_sekolah"],kelas,session)

@adminRouter.delete("/kelas/{id}",response_model=ResponseModel[KelasBase],tags=["ADMIN/KELAS"])
async def deleteKelas(id : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.deleteKelas(id,admin["id_sekolah"],session)


# guru pembimbing

@adminRouter.post("/guru-pembimbing",response_model=ResponseModel[GuruPembimbingWithAlamat],tags=["ADMIN/GURU PEMBIMBING"])
async def addGuruPembimbing(guruPembimbing : AddGuruPembimbingBody,alamat : AlamatBase,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await guruPembimbingService.addGuruPembimbing(admin["id_sekolah"],guruPembimbing,alamat,session)

@adminRouter.patch("/guru-pembimbing/foto_profile/{id_guru}",response_model=ResponseModel[GuruPembimbingBase],tags=["ADMIN/GURU PEMBIMBING"])
async def add_update_profile(id_guru : int,foto_profile : UploadFile,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await guruPembimbingService.add_update_foto_profile(id_guru,admin["id_sekolah"],foto_profile,session)

@adminRouter.get("/guru-pembimbing",response_model=ResponseModel[list[GuruPembimbingWithAlamat] | ResponseGuruPembimbingPag],tags=["ADMIN/GURU PEMBIMBING"])
async def getAllGuruPembimbing(id_tahun : int,page : int | None = None,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await guruPembimbingService.getAllGuruPembimbing(page,admin["id_sekolah"],id_tahun,session)

@adminRouter.get("/guru-pembimbing/{id}",response_model=ResponseModel[GuruPembimbingWithAlamat],tags=["ADMIN/GURU PEMBIMBING"])
async def getGuruPembimbingById(id : int,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await guruPembimbingService.getGuruPembimbingById(id,admin["id_sekolah"],session)

@adminRouter.put("/guru-pembimbing/{id}",response_model=ResponseModel[GuruPembimbingWithAlamat],tags=["ADMIN/GURU PEMBIMBING"])
async def updateGuruPembimbing(id : int,guruPembimbing : UpdateGuruPembimbingBody | None = UpdateGuruPembimbingBody(),alamat : UpdateAlamatBody | None = UpdateAlamatBody(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await guruPembimbingService.updateGuruPembimbing(id,admin["id_sekolah"],guruPembimbing,alamat,session)

@adminRouter.delete("/guru-pembimbing/{id}",response_model=ResponseModel[GuruPembimbingWithAlamat],tags=["ADMIN/GURU PEMBIMBING"])
async def deleteGuruPembimbing(id : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await guruPembimbingService.deleteGuruPembimbing(id,admin["id_sekolah"],session)


# siswa
@adminRouter.post("/siswa",response_model=ResponseModel[MoreSiswa],tags=["ADMIN/SISWA"])
async def addSiswa(siswa : AddSiswaBody,alamat : AlamatBase,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await siswaService.addSiswa(admin["id_sekolah"],siswa,alamat,session)

@adminRouter.patch("/siswa/foto_profile/{id_siswa}",response_model=ResponseModel[SiswaBase],tags=["ADMIN/SISWA"])
async def add_update_profile(id_siswa : int,foto_profile : UploadFile,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await siswaService.add_update_foto_profile(id_siswa,admin["id_sekolah"],foto_profile,session)

@adminRouter.get("/siswa",response_model=ResponseModel[list[MoreSiswa] | ResponseSiswaPag],tags=["ADMIN/SISWA"])
async def getAllSiswa(id_tahun : int,page : int | None = None,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await siswaService.getAllSiswa(page,admin["id_sekolah"],id_tahun,session)

# changhe later to Detail_siswa
@adminRouter.get("/siswa/{id_siswa}",response_model=ResponseModel[MoreSiswa],tags=["ADMIN/SISWA"])
async def getSiswaById(id_siswa : int,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await siswaService.getSiswaById(id_siswa,admin["id_sekolah"],session)

@adminRouter.put("/siswa/{id_siswa}",response_model=ResponseModel[MoreSiswa],tags=["ADMIN/SISWA"])
async def updateSiswa(id_siswa : int,siswa : UpdateSiswaBody | None = UpdateSiswaBody(),alamat : UpdateAlamatBody | None = UpdateAlamatBody(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await siswaService.updateSiswa(id_siswa,admin["id_sekolah"],siswa,alamat,session)

@adminRouter.delete("/siswa/{id_siswa}",response_model=ResponseModel[SiswaBase],tags=["ADMIN/SISWA"])
async def deleteSiswa(id_siswa : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await siswaService.deleteSiswa(id_siswa,admin["id_sekolah"],session)

# dudi

@adminRouter.post("/dudi",response_model=ResponseModel[DudiWithAlamat],tags=["ADMIN/DUDI"])
async def addDudi(dudi : AddDudiBody,alamat : AlamatBase,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await dudiService.addDudi(admin["id_sekolah"],dudi,alamat,session)

@adminRouter.get("/dudi",response_model=ResponseModel[list[DudiWithAlamat] | ResponseDudiPag],tags=["ADMIN/DUDI"])
async def getAllDudi(id_tahun : int,page : int | None = None,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await dudiService.getAllDudi(page,admin["id_sekolah"],id_tahun,session)

@adminRouter.get("/dudi/{id_dudi}",response_model=ResponseModel[DudiWithAlamatKuota],tags=["ADMIN/DUDI"])
async def getDudiById(id_dudi : int,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await dudiService.getDudiById(id_dudi,admin["id_sekolah"],session)

@adminRouter.put("/dudi/{id_dudi}",response_model=ResponseModel[DudiWithAlamat],tags=["ADMIN/DUDI"])
async def updateDudi(id_dudi : int,dudi : UpdateDudiBody | None = UpdateDudiBody(),alamat : UpdateAlamatBody | None = UpdateAlamatBody(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await dudiService.updateDudi(id_dudi,admin["id_sekolah"],dudi,alamat,session)

@adminRouter.delete("/dudi/{id_dudi}",response_model=ResponseModel[DudiBase],tags=["ADMIN/DUDI"])
async def deleteDudi(id_dudi : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await dudiService.deleteDudi(id_dudi,admin["id_sekolah"],session)


# pembimbing dudi
@adminRouter.post("/pembimbing-dudi",response_model=ResponseModel[PembimbingDudiWithAlamatDudi],tags=["ADMIN/PEMBIMBING DUDI"])
async def addPembimbingDudi(pembimbingDudi : AddPembimbingDudiBody,alamat : AlamatBase,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await pembimbingDudiService.addPembimbingDudi(admin["id_sekolah"],pembimbingDudi,alamat,session)

@adminRouter.patch("/pembimbing-dudi/foto_profile/{id_pembimbing_dudi}",response_model=ResponseModel[PembimbingDudiBase],tags=["ADMIN/PEMBIMBING DUDI"])
async def add_update_profile(id_pembimbing_dudi : int,foto_profile : UploadFile,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await pembimbingDudiService.add_update_foto_profile(id_pembimbing_dudi,admin["id_sekolah"],foto_profile,session)

@adminRouter.get("/pembimbing-dudi",response_model=ResponseModel[list[PembimbingDudiWithAlamatDudi] | ResponsePembimbingDudiPagination],tags=["ADMIN/PEMBIMBING DUDI"])
async def getAllPembimbingDudi(id_tahun : int,page : int | None = None,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await pembimbingDudiService.getAllPembimbingDudi(page,admin["id_sekolah"],id_tahun,session)

@adminRouter.get("/pembimbing-dudi/{id_pembimbing_dudi}",response_model=ResponseModel[PembimbingDudiWithAlamatDudi],tags=["ADMIN/PEMBIMBING DUDI"])
async def getPembimbingDudiById(id_pembimbing_dudi : int,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await pembimbingDudiService.getPembimbingDudiById(admin["id_sekolah"],id_pembimbing_dudi,session)

@adminRouter.put("/pembimbing-dudi/{id_pembimbing_dudi}",response_model=ResponseModel[PembimbingDudiWithAlamatDudi],tags=["ADMIN/PEMBIMBING DUDI"])
async def updatePembimbingDudi(id_pembimbing_dudi : int,pembimbingDudi : UpdatePembimbingDudiBody | None = UpdatePembimbingDudiBody(),alamat : UpdateAlamatBody | None = UpdateAlamatBody(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await pembimbingDudiService.updatePembimbingDudi(admin["id_sekolah"],id_pembimbing_dudi,pembimbingDudi,alamat,session)

@adminRouter.delete("/pembimbing-dudi/{id_pembimbing_dudi}",response_model=ResponseModel[PembimbingDudiBase],tags=["ADMIN/PEMBIMBING DUDI"])
async def deletePembimbingDudi(id_pembimbing_dudi : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await pembimbingDudiService.deletePembimbingDudi(admin["id_sekolah"],id_pembimbing_dudi,session)


# laporan pkl
@adminRouter.get("/laporan-pkl-dudi",response_model=ResponseModel[ResponseLaporanPklDudiPag],tags=["ADMIN/LAPORAN PKL DUDI"])
async def getAllLaporanPklDudi(id_tahun : int,page : int,filter : FilterLaporanPklDudiQuery = Depends(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await laporanPklDudiService.getAllLaporanPkl(page,admin["id_sekolah"],id_tahun,filter,session)

@adminRouter.get("/laporan-pkl-dudi/{id_laporan}",response_model=ResponseModel[LaporanPklDudiBase],tags=["ADMIN/LAPORAN PKL DUDI"])
async def getLaporanPklDudiById(id_laporan : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await laporanPklDudiService.getLaporanPkl(id_laporan,admin["id_sekolah"],session)

# laporan pkl siswa
@adminRouter.get("/laporan-pkl-siswa",response_model=ResponseModel[ResponseLaporanPklSiswaPag],tags=["ADMIN/LAPORAN PKL SISWA"])
async def getAllLaporanPklSiswa(id_tahun : int,page : int,filter : FilterLaporanPklSiswaQuery = Depends(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await laporanPklSiswaService.getAllLaporanPkl(page,admin["id_sekolah"],id_tahun,filter,session)

@adminRouter.get("/laporan-pkl-siswa/{id_laporan}",response_model=ResponseModel[LaporanPklSiswaBase],tags=["ADMIN/LAPORAN PKL SISWA"])
async def getAllLaporanPklSiswa(id_laporan : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await laporanPklSiswaService.getLaporanPkl(id_laporan,admin["id_sekolah"],session)

# absen
@adminRouter.get("/absen",response_model=ResponseModel[ResponseAbsenPag],tags=["ADMIN/ABSEN"])
async def getAllAbsen(id_tahun : int,page : int,filter : FilterAbsenQuery = Depends(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await absenService.getAllAbsen(page,admin["id_sekolah"],id_tahun,filter,session)

@adminRouter.get("/absen/{id_absen}",response_model=ResponseModel[MoreAbsen],tags=["ADMIN/ABSEN"])
async def getAbsenById(id_absen : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await absenService.getAbsenById(id_absen,admin["id_sekolah"],session)