from fastapi import APIRouter,Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

# auth
from ..auth.dependsAuthMiddleware.guru_pembimbing.depend_auth_guru_pembimbing import guruPembimbingAuth
from ..auth.dependsAuthMiddleware.guru_pembimbing.get_guru_pembimbing_auth import getGuruPembimbingAuth

# profile-auth
from ..domain.models_domain.guru_pembimbing_model import GuruPembimbingBase,GuruPembimbingWithSekolahAlamat
from ..domain.guru_pembimbing.profile_auth import profileAuthService
from ..domain.guru_pembimbing.profile_auth.profileAuthModel import UpdateProfileBody

# siswa-manage
from ..domain.guru_pembimbing.siswa_manage import siswaManageService
from ..domain.guru_pembimbing.siswa_manage.siswaManageModel import ResponseCountSiswa, ResponseSiswaPag
from ..domain.models_domain.siswa_model import DetailSiswa, SiswaWithDudi

# laporan-pkl-siswa
from ..domain.guru_pembimbing.laporan_pkl_siswa import laporanPklSiswaService
from ..domain.guru_pembimbing.laporan_pkl_siswa.laporanPklSiswaModel import FilterBySiswa,ResponselaporanPklSiswaPag
from ..domain.guru_pembimbing.laporan_pkl_siswa.laporanPklSiswaModel import LaporanPklSiswaBase

# laporan-pkl-dudi
from ..domain.guru_pembimbing.laporan_pkl_dudi import laporanPklDudiService
from ..domain.guru_pembimbing.laporan_pkl_dudi.laporanPklDudiModel import Filter,ResponseLaporanPklDudiPag
from ..domain.guru_pembimbing.laporan_pkl_dudi.laporanPklDudiModel import LaporanPklDudiBase

# get-dudi
from ..domain.guru_pembimbing.get_dudi import getDudiService
from ..domain.models_domain.dudi_model import DudiWithAlamat

# kunjungan-dudi
from ..domain.guru_pembimbing.kunjungan import kunjunganService
from ..domain.guru_pembimbing.kunjungan.kunjunganModel import AddKunjunganBody,UpdateKunjunganBody,ResponseKunjunganDudiPag
from ..domain.models_domain.kunjungan_guru_pembimbing_model import KunjunganGuruPembimbingWithDudi

# get absen
from ..domain.guru_pembimbing.absen import absenService
from ..domain.guru_pembimbing.absen.absenModel import FilterAbsen,AbsenResponse
from ..domain.models_domain.absen_model import MoreAbsen


# common
from ..db.sessionDepedency import sessionDepedency
from ..models.responseModel import ResponseModel

guruPembimbingRouter = APIRouter(prefix="/guru-pembimbing",dependencies=[Depends(guruPembimbingAuth)])

# profile-auth
@guruPembimbingRouter.get("/",response_model=ResponseModel[GuruPembimbingBase],tags=["GURU-PEMBIMBING/PROFILE-AUTH"])
async def getGuruPembimbing(guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await profileAuthService.getGuruPembimbing(guru["id"],session)

@guruPembimbingRouter.get("/profile",response_model=ResponseModel[GuruPembimbingWithSekolahAlamat],tags=["GURU-PEMBIMBING/PROFILE-AUTH"])
async def getGuruPembimbingProfile(guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await profileAuthService.getProfileAuth(guru["id"],session)

@guruPembimbingRouter.put("/profile",response_model=ResponseModel[GuruPembimbingBase],tags=["GURU-PEMBIMBING/PROFILE-AUTH"])
async def updateGuruPembimbing(guru : dict = Depends(getGuruPembimbingAuth),body : UpdateProfileBody = UpdateProfileBody(),session : sessionDepedency = None):
    return await profileAuthService.updateProfile(guru["id"],body,session)

@guruPembimbingRouter.put("/profile/foto",response_model=ResponseModel[GuruPembimbingBase],tags=["GURU-PEMBIMBING/PROFILE-AUTH"])
async def updateGuruPembimbing(foto_profile : UploadFile,guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await profileAuthService.updateFotoProfile(guru["id"],foto_profile,session)

# siswa-manage
@guruPembimbingRouter.get("/siswa",response_model=ResponseModel[ResponseSiswaPag | list[SiswaWithDudi]],tags=["GURU-PEMBIMBING/SISWA-MANAGE"])
async def getSiswa(page : int | None = None, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await siswaManageService.getAllSiswa(guru["id"],guru["id_sekolah"],page,session)

@guruPembimbingRouter.get("/siswa/count",response_model=ResponseModel[ResponseCountSiswa],tags=["GURU-PEMBIMBING/SISWA-MANAGE"])
async def getCountSiswa(guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await siswaManageService.getCountSiswa(guru["id"],guru["id_sekolah"],session)

@guruPembimbingRouter.get("/siswaByDudi",response_model=ResponseModel[list[SiswaWithDudi]],tags=["GURU-PEMBIMBING/SISWA-MANAGE"])
async def getSiswaByDudi(id_dudi : int, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await siswaManageService.getSiswaByDudi(id_dudi,guru["id"],session)

@guruPembimbingRouter.get("/siswa/{Id_siswa}",response_model=ResponseModel[DetailSiswa],tags=["GURU-PEMBIMBING/SISWA-MANAGE"])
async def getSiswaById(Id_siswa : int, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await siswaManageService.getSiswaById(Id_siswa,guru["id"],session)

# laporan-pkl-siswa
@guruPembimbingRouter.get("/laporan-pkl-siswa",response_model=ResponseModel[ResponselaporanPklSiswaPag | list[LaporanPklSiswaBase]],tags=["GURU-PEMBIMBING/LAPORAN-PKL-SISWA"])
async def getAllLaporanPklSiswa(filter : FilterBySiswa = Depends(),page : int | None = None, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await laporanPklSiswaService.getAllLaporanPklSiswa(guru["id"],guru["id_sekolah"],filter,page,session)

@guruPembimbingRouter.get("/laporan-pkl-siswa/{id_laporan}",response_model=ResponseModel[LaporanPklSiswaBase],tags=["GURU-PEMBIMBING/LAPORAN-PKL-SISWA"])
async def getLaporanPklById(id_laporan : int, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await laporanPklSiswaService.getLaporanPklSiswaById(id_laporan,guru["id"],session)

# laporan-pkl-dudi
@guruPembimbingRouter.get("/laporan-pkl-dudi",response_model=ResponseModel[ResponseLaporanPklDudiPag | list[LaporanPklDudiBase]],tags=["GURU-PEMBIMBING/LAPORAN-PKL-DUDI"])
async def getAllLaporanPklDudi(filter : Filter = Depends(),page : int | None = None, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await laporanPklDudiService.getAllLaporanPklDudi(guru["id"],guru["id_sekolah"],page,filter,session)

@guruPembimbingRouter.get("/laporan-pkl-dudi/{id_laporan}",response_model=ResponseModel[LaporanPklDudiBase],tags=["GURU-PEMBIMBING/LAPORAN-PKL-DUDI"])
async def getLaporanPklDudiById(id_laporan : int, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await laporanPklDudiService.getLaporanPklDudiById(id_laporan,guru["id"],session)

# get-dudi
@guruPembimbingRouter.get("/dudi",response_model=ResponseModel[list[DudiWithAlamat]],tags=["GURU-PEMBIMBING/GET-DUDI"])
async def getDudiByGuru(guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await getDudiService.getDudiByGuru(guru["id"],session)

# kunjungan
@guruPembimbingRouter.post("/kunjungan",response_model=ResponseModel[KunjunganGuruPembimbingWithDudi],tags=["GURU-PEMBIMBING/KUNJUNGAN"])
async def addKunjungan(kunjungan : AddKunjunganBody,guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await kunjunganService.addKunjungan(guru["id"],kunjungan,session)

@guruPembimbingRouter.get("/kunjungan",response_model=ResponseModel[ResponseKunjunganDudiPag | list[KunjunganGuruPembimbingWithDudi]],tags=["GURU-PEMBIMBING/KUNJUNGAN"])
async def getAllKunjungan(page : int | None = None, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await kunjunganService.getAllKunjungan(guru["id"],page,session)

@guruPembimbingRouter.get("/kunjungan/{id_kunjungan}",response_model=ResponseModel[KunjunganGuruPembimbingWithDudi],tags=["GURU-PEMBIMBING/KUNJUNGAN"])
async def getKunjunganById(id_kunjungan : int, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await kunjunganService.getKunjunganById(guru["id"],id_kunjungan,session)

@guruPembimbingRouter.put("/kunjungan/{id_kunjungan}",response_model=ResponseModel[KunjunganGuruPembimbingWithDudi],tags=["GURU-PEMBIMBING/KUNJUNGAN"])
async def updateKunjungan(id_kunjungan : int, kunjungan : UpdateKunjunganBody = UpdateKunjunganBody(),guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await kunjunganService.updateKunjungan(id_kunjungan,guru["id"],kunjungan,session)

@guruPembimbingRouter.delete("/kunjungan/{id_kunjungan}",response_model=ResponseModel[KunjunganGuruPembimbingWithDudi],tags=["GURU-PEMBIMBING/KUNJUNGAN"])
async def deleteKunjungan(id_kunjungan : int, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await kunjunganService.deleteKunjungan(guru["id"],id_kunjungan,session)

# get absen
@guruPembimbingRouter.get("/absen",response_model=AbsenResponse,tags=["GURU-PEMBIMBING/GET-ABSEN"])
async def getAllAbsen(filter : FilterAbsen = Depends(),isSevenDay : bool = False,guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await absenService.getAllAbsen(guru["id"],filter,isSevenDay,session)

@guruPembimbingRouter.get("/absen/{id_absen}",response_model=ResponseModel[MoreAbsen],tags=["GURU-PEMBIMBING/GET-ABSEN"])
async def getAbsenById(id_absen : int, guru : dict = Depends(getGuruPembimbingAuth),session : sessionDepedency = None):
    return await absenService.getAbsenById(id_absen,guru["id"],session)