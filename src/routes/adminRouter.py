from fastapi import APIRouter, Depends

# models
# jurusan dan kelas
from ..domain.admin.jurusan_kelas.jurusanKelasModel import AddJurusanBody, UpdateJurusanBody, AddKelasBody, UpdateKelasBody
from ..domain.models_domain.kelas_jurusan_model import JurusanBase,MoreJurusanBase,KelasBase,KelasWithJurusan
from ..domain.admin.jurusan_kelas import jurusanKelasService

# tahun sekolah
from ..domain.admin.tahun_sekolah.tahunSekolahModel import AddTahunSekolahBody,UpdateTahunSekolahBody
from ..domain.admin.tahun_sekolah import tahunSekolahService
from ..domain.models_domain.sekolah_model import TahunSekolahBase

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
async def getJurusanById(id : int, session : sessionDepedency = None) :
    return await jurusanKelasService.getJurusanById(id,session)

@adminRouter.put("/jurusan/{id}",response_model=ResponseModel[JurusanBase],tags=["ADMIN/JURUSAN"])
async def updateJurusan(id : int,jurusan : UpdateJurusanBody | None = UpdateJurusanBody(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.updateJurusan(id,jurusan,admin["id_sekolah"],session)

@adminRouter.delete("/jurusan/{id}",response_model=ResponseModel[JurusanBase],tags=["ADMIN/JURUSAN"])
async def deleteJurusan(id : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.deleteJurusan(id,admin["id_sekolah"],session)

# kelas
@adminRouter.post("/kelas",response_model=ResponseModel[KelasBase],tags=["ADMIN/KElas"])
async def addKelas(kelas : AddKelasBody,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.addKelas(admin["id_sekolah"],kelas,session)

@adminRouter.get("/kelas",response_model=ResponseModel[list[KelasBase]],tags=["ADMIN/KElas"])
async def getAllKelas(id_tahun : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.getAllKelas(admin["id_sekolah"],id_tahun,session)

@adminRouter.get("/kelas/{id}",response_model=ResponseModel[KelasWithJurusan],tags=["ADMIN/KElas"])
async def getKelasById(id : int,session : sessionDepedency = None) :
    return await jurusanKelasService.getKelasById(id,session)

@adminRouter.put("/kelas/{id}",response_model=ResponseModel[KelasBase],tags=["ADMIN/KElas"])
async def updateKelas(id : int,kelas : UpdateKelasBody | None = UpdateKelasBody(),admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.updateKelas(id,admin["id_sekolah"],kelas,session)

@adminRouter.delete("/kelas/{id}",response_model=ResponseModel[KelasBase],tags=["ADMIN/KElas"])
async def deleteKelas(id : int,admin : dict = Depends(getAdminAuth), session : sessionDepedency = None) :
    return await jurusanKelasService.deleteKelas(id,admin["id_sekolah"],session)

