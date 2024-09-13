from fastapi import APIRouter,Depends, UploadFile

from ..domain.models_domain.siswa_model import SiswaBase

# auth
from ..auth.dependsAuthMiddleware.siswa.depend_auth_siswa import siswaDependAuth
from ..auth.dependsAuthMiddleware.siswa.get_siswa_auth import getSiswaAuth

# profile-auth
from ..domain.siswa.profile_auth import profileAuthService
from ..domain.siswa.profile_auth.profileAuthModel import UpdateProfileBody
from ..domain.models_domain.siswa_model import SiswaBase,DetailSiswa,SiswaWithJurusanKelas

# get_dudi
from ..domain.siswa.get_dudi import getDudiService
from ..domain.siswa.get_dudi.getDudiModel import ResponseGetDudiPag,FilterGetDudiQuery
from ..domain.models_domain.dudi_model import DudiWithAlamat

# pengajuan pkl
from ..domain.siswa.pengajuan_pkl import pengajuanPklService
from ..domain.siswa.pengajuan_pkl.pengajuanPklModel import AddPengajuanPklBody
from ..domain.models_domain.pengajuan_pkl_model import PengajuanPklWithDudi

from ..models.pengajuanPklModel import StatusPengajuanENUM,StatusCancelPKLENUM

# pengjuan_cancel pkl
from ..domain.siswa.pengajuan_cancel_pkl import pengajuanCancelPklService
from ..domain.models_domain.pengajuan_cancel_pkl_model import PengajuanCancelPklWithDudi,PengajuanCancelPklBase

# laporan-siswa-pkl
from ..domain.siswa.laporan_pkl_siswa import laporanPklSiswaService
from ..domain.models_domain.laporan_pkl_siswa_model import LaporanPklSiswaBase,LaporanPklWithoutDudiAndSiswa
from ..domain.siswa.laporan_pkl_siswa.laporanPklSiswaModel import AddLaporanPklSiswaBody,UpdateLaporanPklSiswaBody,ResponseGetLaporanPklSiswaPag

# laporan-dudi-pkl
from ..domain.siswa.laporan_pkl_dudi import laporanPklDudiService
from ..domain.siswa.laporan_pkl_dudi.laporanPklDudiModel import ResponseGetLaporanPklDudiPag
from ..domain.models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase


# common
from ..db.sessionDepedency import sessionDepedency
from ..models.responseModel import ResponseModel

siswaRouter = APIRouter(prefix="/siswa",dependencies=[Depends(siswaDependAuth)])


# profile-auth
@siswaRouter.get("/",response_model=ResponseModel[SiswaBase],tags=["SISWA/PROFILE-AUTH"])
async def getSiswa(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await profileAuthService.getSiswa(siswa["id"],session)

@siswaRouter.get("/profile",response_model=ResponseModel[DetailSiswa],tags=["SISWA/PROFILE-AUTH"])
async def getProfile(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await profileAuthService.getProfileAuth(siswa["id"],session)

@siswaRouter.put("/profile/foto_profile",response_model=ResponseModel[SiswaBase],tags=["SISWA/PROFILE-AUTH"])
async def updateFotoProfile(foto_profile : UploadFile,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await profileAuthService.updateFotoProfile(siswa["id"],foto_profile,session)

@siswaRouter.put("/profile",response_model=ResponseModel[SiswaWithJurusanKelas],tags=["SISWA/PROFILE-AUTH"])
async def updateProfile(body : UpdateProfileBody = UpdateProfileBody(),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await profileAuthService.updateProfile(siswa["id"],body,session)

# get-dudi
@siswaRouter.get("/dudi",response_model=ResponseModel[ResponseGetDudiPag],tags=["SISWA/GET-DUDI"])
async def getAllDudi(page : int,query : FilterGetDudiQuery = Depends(),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await getDudiService.getDudi(siswa["id"],siswa["id_sekolah"],page,query,session)

@siswaRouter.get("/dudi/{id_dudi}",response_model=ResponseModel[DudiWithAlamat],tags=["SISWA/GET-DUDI"])
async def getDudiById(id_dudi : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await getDudiService.getDudiById(id_dudi,siswa["id_sekolah"],session)

# pengjuan pkl
@siswaRouter.post("/pengajuan_pkl",response_model=ResponseModel[PengajuanPklWithDudi],tags=["SISWA/PENGAJUAN-PKL"])
async def addPengajuanPkl(body : AddPengajuanPklBody,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanPklService.addPengajuanPkl(siswa["id"],siswa["id_sekolah"],body,session)

@siswaRouter.put("/pengajuan_pkl/cancel/{id_pengajuan}",response_model=ResponseModel[PengajuanPklWithDudi],tags=["SISWA/PENGAJUAN-PKL"])
async def cancelPengajuan(id_pengajuan : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanPklService.cancelPengajuanPkl(siswa["id"],id_pengajuan,session)

@siswaRouter.get("/pengajuan_pkl",response_model=ResponseModel[list[PengajuanPklWithDudi]],tags=["SISWA/PENGAJUAN-PKL"])      
async def getAllPengajuanPkl(status : StatusPengajuanENUM | None = None, siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanPklService.getAllPengajuanPkl(siswa["id"],status,session)

@siswaRouter.get("/pengajuan_pkl/{id_pengajuan_pkl}",response_model=ResponseModel[PengajuanPklWithDudi],tags=["SISWA/PENGAJUAN-PKL"])
async def getPengajuanPklById(id_pengajuan_pkl : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanPklService.getPengajuanPklById(siswa["id"],id_pengajuan_pkl,session)

@siswaRouter.get("/pengajuan_pkl/last/get",response_model=ResponseModel[PengajuanPklWithDudi],tags=["SISWA/PENGAJUAN-PKL"])
async def getLastPengajuan(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanPklService.getLastPengajuanPkl(siswa["id"],session)

# pengajuan_cancel pkl
@siswaRouter.post("/pengajuan_cancel_pkl",response_model=ResponseModel[PengajuanCancelPklBase],tags=["SISWA/PENGAJUAN-CANCEL-PKL"])
async def addPengajuanCancelPkl(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanCancelPklService.addPengajuanCancelPkl(siswa["id"],session)

@siswaRouter.get("/pengajuan_cancel_pkl",response_model=ResponseModel[list[PengajuanCancelPklWithDudi]],tags=["SISWA/PENGAJUAN-CANCEL-PKL"])
async def getAllPengajuanCancelPkl(status : StatusCancelPKLENUM | None = None,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanCancelPklService.getAllPengajuanCancelPkl(siswa["id"],status,session)

@siswaRouter.put("/pengajuan_cancel_pkl/cancel/{id_pengajuan}",response_model=ResponseModel[PengajuanCancelPklWithDudi],tags=["SISWA/PENGAJUAN-CANCEL-PKL"])
async def cancelPengajuan(id_pengajuan : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanCancelPklService.cancelPengjuan(siswa["id"],id_pengajuan,session)

@siswaRouter.get("/pengajuan_cancel_pkl/{id_pengajuan_cancel_pkl}",response_model=ResponseModel[PengajuanCancelPklWithDudi],tags=["SISWA/PENGAJUAN-CANCEL-PKL"])
async def getPengajuanCancelPklById(id_pengajuan_cancel_pkl : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanCancelPklService.getPengajuanCancelPklById(siswa["id"],id_pengajuan_cancel_pkl,session)

@siswaRouter.get("/pengajuan_cancel_pkl/last/get",response_model=ResponseModel[PengajuanCancelPklWithDudi],tags=["SISWA/PENGAJUAN-CANCEL-PKL"])
async def getLastPengajuanCancelPkl(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await pengajuanCancelPklService.getLastPengajuanCancelPkl(siswa["id"],session)


# laporan pkl siswa
@siswaRouter.post("/laporan_pkl_siswa",response_model=ResponseModel[LaporanPklWithoutDudiAndSiswa],tags=["SISWA/LAPORAN-PKL-SISWA"])
async def addLaporanPklSiswa(body : AddLaporanPklSiswaBody,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanPklSiswaService.addLaporanPklSiswa(siswa["id"],siswa["id_dudi"],body,session)

@siswaRouter.get("/laporan_pkl_siswa",response_model=ResponseModel[ResponseGetLaporanPklSiswaPag],tags=["SISWA/LAPORAN-PKL-SISWA"])
async def getAllLaporanPklSiswa(page : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanPklSiswaService.getAllLaporanPklSiswa(siswa["id"],page,session)

@siswaRouter.get("/laporan_pkl_siswa/{id_laporan_pkl_siswa}",response_model=ResponseModel[LaporanPklSiswaBase],tags=["SISWA/LAPORAN-PKL-SISWA"])
async def getLaporanPklSiswaById(id_laporan_pkl_siswa : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanPklSiswaService.getLaporanPklSiswaById(siswa["id"],id_laporan_pkl_siswa,session)

@siswaRouter.put("/laporan_pkl_siswa/{id_laporan_siswa}",response_model=ResponseModel[LaporanPklWithoutDudiAndSiswa],tags=["SISWA/LAPORAN-PKL-SISWA"])
async def updateLaporanPklSiswa(id_laporan_siswa : int,body : UpdateLaporanPklSiswaBody = UpdateLaporanPklSiswaBody(),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanPklSiswaService.updateLaporanPklSiswa(siswa["id"],id_laporan_siswa,body,session)

@siswaRouter.put("/laporan_pkl_siswa/file_laporan/{id_laporan_siswa}",response_model=ResponseModel[LaporanPklWithoutDudiAndSiswa],tags=["SISWA/LAPORAN-PKL-SISWA"])
async def uploadUpdateFileLaporanPklSiswa(id_laporan_siswa : int,file_laporan : UploadFile,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanPklSiswaService.addUpdateFileLaporanPkl(siswa["id"],id_laporan_siswa,file_laporan,session)

@siswaRouter.delete("/laporan_pkl_siswa/{id_laporan_siswa}",response_model=ResponseModel[LaporanPklWithoutDudiAndSiswa],tags=["SISWA/LAPORAN-PKL-SISWA"])
async def deleteLaporanPklSiswa(id_laporan_siswa : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanPklSiswaService.deleteLaporanPklSiswa(siswa["id"],id_laporan_siswa,session)

# laporan pkl dudi
@siswaRouter.get("/laporan_pkl_dudi",response_model=ResponseModel[ResponseGetLaporanPklDudiPag],tags=["SISWA/LAPORAN-PKL-DUDI"])
async def getAllLaporanPklDudi(page : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanPklDudiService.getAllLaporanPklDudi(siswa["id"],page,session)

@siswaRouter.get("/laporan_pkl_dudi/{id_laporan_pkl_dudi}",response_model=ResponseModel[LaporanPklDudiBase],tags=["SISWA/LAPORAN-PKL-DUDI"])
async def getLaporanPklDudiById(id_laporan_pkl_dudi : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanPklDudiService.getLaporanPklDudiById(id_laporan_pkl_dudi,siswa["id"],session)