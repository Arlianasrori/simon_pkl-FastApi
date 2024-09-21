from fastapi import APIRouter,Depends, UploadFile

from ..domain.models_domain.pembimbing_dudi_model import PembimbingDudiBase,PembimbingDudiWithAlamatDudi
from ..domain.models_domain.siswa_model import MoreSiswa

# auth
from ..auth.dependsAuthMiddleware.pembimbing_dudi.depend_auth_pembimbing_dudi import pembimbingDudiAuth
from ..auth.dependsAuthMiddleware.pembimbing_dudi.get_pembimbing_dudi_auth import getPembimbingDudiAuth

# profile-auth
from ..domain.pembimbing_dudi.profile_auth import profileAuthService
from ..domain.pembimbing_dudi.profile_auth.profileAuthModel import UpdateProfileBody

# siswa-manage
from ..domain.pembimbing_dudi.siswa_manage import siswaManageService
from ..domain.pembimbing_dudi.siswa_manage.siswaManageModel import ResponseCountSiswa,ResponseSiswaPag
from ..domain.models_domain.siswa_model import JurusanBase

# kouta
from ..domain.pembimbing_dudi.kouta_dudi.koutaDudiService import AddKoutaDudiBody,UpdateKoutaDudiBody
from ..domain.models_domain.dudi_model import DudiWithKouta
from ..domain.pembimbing_dudi.kouta_dudi import koutaDudiService

# laporan pkl
from ..domain.pembimbing_dudi.laporan_pkl import laporanPklService
from ..domain.pembimbing_dudi.laporan_pkl.laporanPklModel import AddLaporanPklDudiBody,UpdateLaporanPklDudiBody
from ..domain.models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase,LaporanPklDudiWithOut

# pengajuan pkl
from ..domain.pembimbing_dudi.pengajuan_pkl import pengajuanPklService
from ..domain.pembimbing_dudi.pengajuan_pkl.pengajuanPklModel import AccDccPengajuanPkl as ACCPengajuan
from ..domain.models_domain.pengajuan_pkl_model import PengajuanPklWithSiswa

# pengajuan cancel pkl
from ..domain.pembimbing_dudi.pengajuan_cancel_pkl import pengajuanCancelPklService
from ..domain.pembimbing_dudi.pengajuan_cancel_pkl.pengajuanCancelPklModel import AccDccPengajuanPkl as ACCPengajuanCancel,ResponsePengajuanCancelPklPag
from ..domain.models_domain.pengajuan_cancel_pkl_model import PengajuanCancelPklWithSiswa

# common
from ..db.sessionDepedency import sessionDepedency
from ..models.responseModel import ResponseModel

pembimbingDudiRouter = APIRouter(prefix="/pembimbingDudi",dependencies=[Depends(pembimbingDudiAuth)])

# profile-auth
@pembimbingDudiRouter.get("/",response_model=ResponseModel[PembimbingDudiBase],tags=["PEMBIMBING-DUDI"])
async def getPembimbingDudi(pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await profileAuthService.getPembimbingDudi(pembimbing["id"],session)

@pembimbingDudiRouter.get("/profile",response_model=ResponseModel[PembimbingDudiWithAlamatDudi],tags=["PEMBIMBING-DUDI/PROFILE"])
async def getProfile(pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await profileAuthService.getProfile(pembimbing["id"],session)

@pembimbingDudiRouter.put("/profile",response_model=ResponseModel[PembimbingDudiBase],tags=["PEMBIMBING-DUDI/PROFILE"])
async def updateProfile(pembimbing : dict = Depends(getPembimbingDudiAuth),body : UpdateProfileBody = UpdateProfileBody(),session : sessionDepedency = None) :
    return await profileAuthService.updateProfile(pembimbing["id"],body,session)

@pembimbingDudiRouter.put("/profile/foto",response_model=ResponseModel[PembimbingDudiBase],tags=["PEMBIMBING-DUDI/PROFILE"])
async def updateFotoProfile(foto_profile : UploadFile,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await profileAuthService.updateFotoProfile(pembimbing["id"],foto_profile,session)

# siswa
@pembimbingDudiRouter.get("/siswa",response_model=ResponseModel[list[MoreSiswa] | ResponseSiswaPag],tags=["PEMBIMBING-DUDI/SISWA"])
async def getAllSiswa(page : int | None = None,pembimbingDudi : dict = Depends(getPembimbingDudiAuth), session : sessionDepedency = None) :
    print(pembimbingDudi)
    return await siswaManageService.getSiswa(pembimbingDudi["id"],page,session)


@pembimbingDudiRouter.get("/siswa/{id_siswa}",response_model=ResponseModel[MoreSiswa],tags=["PEMBIMBING-DUDI/SISWA"])
async def getSiswaById(id_siswa : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await siswaManageService.getSiswaById(pembimbing["id"],id_siswa,session)

@pembimbingDudiRouter.get("/siswa/count",response_model=ResponseModel[ResponseCountSiswa],tags=["PEMBIMBING-DUDI/SISWA"])
async def getCountSiswa(pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await siswaManageService.getCountSiswa(pembimbing["id"],session)

# jurusan
@pembimbingDudiRouter.get("/jurusan",response_model=ResponseModel[list[JurusanBase]],tags=["PEMBIMBING-DUDI/JURUSAn"])
async def getAllJurusan(pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await siswaManageService.getAllJurusan(pembimbing["id_sekolah"],session)

# kouta
@pembimbingDudiRouter.get("/kouta",response_model=ResponseModel[DudiWithKouta],tags=["PEMBIMBING-DUDI/KOUTA"])
async def getKoutaDudi(pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await koutaDudiService.getKoutaDudi(pembimbing["id_dudi"],session)

@pembimbingDudiRouter.post("/kouta",response_model=ResponseModel[DudiWithKouta],tags=["PEMBIMBING-DUDI/KOUTA"])
async def addKoutaDudi(kouta : AddKoutaDudiBody,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await koutaDudiService.addKoutaDudi(pembimbing["id_dudi"],kouta,session)

@pembimbingDudiRouter.put("/kouta",response_model=ResponseModel[DudiWithKouta],tags=["PEMBIMBING-DUDI/KOUTA"])
async def updateKoutaDudi(kouta : UpdateKoutaDudiBody,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await koutaDudiService.updateKoutaDudi(pembimbing["id_dudi"],kouta,session)

# laporan pkl
@pembimbingDudiRouter.post("/laporan-pkl",response_model=ResponseModel[LaporanPklDudiBase],tags=["PEMBIMBING-DUDI/LAPORAN-PKL"])
async def addLaporanPkl(laporan : AddLaporanPklDudiBody,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await laporanPklService.addLaporanPkl(pembimbing["id"],pembimbing["id_dudi"],laporan,session)

@pembimbingDudiRouter.get("/laporan-pkl",response_model=ResponseModel[list[LaporanPklDudiBase]],tags=["PEMBIMBING-DUDI/LAPORAN-PKL"])
async def getAllLaporanPkl(page : int | None = None,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await laporanPklService.getLaporanPkl(pembimbing["id"],page,session)

@pembimbingDudiRouter.get("/laporan-pkl/{id_laporan_pkl}",response_model=ResponseModel[LaporanPklDudiBase],tags=["PEMBIMBING-DUDI/LAPORAN-PKL"])
async def getLaporanPklById(id_laporan_pkl : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await laporanPklService.getLaporanPklById(id_laporan_pkl,pembimbing["id"],session)

@pembimbingDudiRouter.patch("/laporan-pkl/file/{id_laporan_pkl}",response_model=ResponseModel[LaporanPklDudiWithOut],tags=["PEMBIMBING-DUDI/LAPORAN-PKL"])
async def add_update_profile(id_laporan_pkl : int,file : UploadFile,session : sessionDepedency = None) :
    return await laporanPklService.addUpdateFileLaporanPkl(id_laporan_pkl,file,session)

@pembimbingDudiRouter.put("/laporan-pkl/{id_laporan}",response_model=ResponseModel[LaporanPklDudiBase],tags=["PEMBIMBING-DUDI/LAPORAN-PKL"])
async def updateLaporanPkl(id_laporan : int,laporan : UpdateLaporanPklDudiBody = UpdateLaporanPklDudiBody(),pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await laporanPklService.updateLaporanPkl(id_laporan,pembimbing["id"],laporan,session)

@pembimbingDudiRouter.delete("/laporan-pkl/{id_laporan}",response_model=ResponseModel[LaporanPklDudiBase],tags=["PEMBIMBING-DUDI/LAPORAN-PKL"])
async def deleteLaporanPkl(id_laporan : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await laporanPklService.deleteLaporanPkl(id_laporan,pembimbing["id"],session)

# pengajuan pkl
@pembimbingDudiRouter.get("/pengajuan-pkl",response_model=ResponseModel[list[PengajuanPklWithSiswa]],tags=["PEMBIMBING-DUDI/PENGJUAN-PKL"])
async def getAllPengajuanPkl(page : int | None = None,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await pengajuanPklService.getAllPengajuanPkl(pembimbing["id_dudi"],page,session)

@pembimbingDudiRouter.get("/pengajuan-pkl/{id_pengajuan_pkl}",response_model=ResponseModel[PengajuanPklWithSiswa],tags=["PEMBIMBING-DUDI/PENGJUAN-PKL"])
async def getPengajuanPklById(id_pengajuan_pkl : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await pengajuanPklService.getPengajuanPklById(id_pengajuan_pkl,pembimbing["id_dudi"],session)

@pembimbingDudiRouter.put("/pengajuan-pkl/{id_pengajuan_pkl}",response_model=ResponseModel[PengajuanPklWithSiswa],tags=["PEMBIMBING-DUDI/PENGJUAN-PKL"])
async def accDccPengajuanPkl(id_pengajuan_pkl : int,pengajuan_pkl : ACCPengajuan,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await pengajuanPklService.accDccPengajuanPkl(id_pengajuan_pkl,pembimbing["id"],pembimbing["id_dudi"],pengajuan_pkl,session)


# pengjuan cancel pkl
@pembimbingDudiRouter.get("/pengajuan-cancel-pkl",response_model=ResponseModel[list[PengajuanCancelPklWithSiswa]],tags=["PEMBIMBING-DUDI/PENGJUAN-CANCEL-PKL"])
async def getAllPengajuanCancelPkl(page : int | None = None,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await pengajuanCancelPklService.getAllPengajuancancelPkl(pembimbing["id_dudi"],page,session)

@pembimbingDudiRouter.get("/pengajuan-cancel-pkl/{id_pengajuan_cancel_pkl}",response_model=ResponseModel[PengajuanCancelPklWithSiswa],tags=["PEMBIMBING-DUDI/PENGJUAN-CANCEL-PKL"])
async def getPengajuanCancelPklById(id_pengajuan_cancel_pkl : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await pengajuanCancelPklService.getPengajuanCancelPklById(id_pengajuan_cancel_pkl,pembimbing["id_dudi"],session)

@pembimbingDudiRouter.put("/pengajuan-cancel-pkl/{id_pengajuan_cancel_pkl}",response_model=ResponseModel[PengajuanCancelPklWithSiswa],tags=["PEMBIMBING-DUDI/PENGJUAN-CANCEL-PKL"])
async def accDccPengajuanCancelPkl(id_pengajuan_cancel_pkl : int,pengajuan_cancel_pkl : ACCPengajuanCancel,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await pengajuanCancelPklService.accDccPengajuanPkl(id_pengajuan_cancel_pkl,pembimbing["id_dudi"],pengajuan_cancel_pkl,session)