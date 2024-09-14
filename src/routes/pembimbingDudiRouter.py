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

# jadwal absen
from ..domain.pembimbing_dudi.absen.jadwal_absen import absenJadwalService
from ..domain.pembimbing_dudi.absen.jadwal_absen.absenJadwalModel import AddJadwalAbsenBody,UpdateJadwalAbsenBody
from ..domain.models_domain.absen_model import JadwalAbsenWithHari

# koordinat absen
from ..domain.pembimbing_dudi.absen.koordinat_absen import koordinatAbsenService
from ..domain.pembimbing_dudi.absen.koordinat_absen.koordinatAbsenModel import AddkoordinatAbsenBody,UpdatekoordinaatAbsenBody
from ..domain.models_domain.absen_model import koordinatAbsenBase

# get absen
from ..domain.pembimbing_dudi.absen.get_absen import getAbsenservice
from ..domain.pembimbing_dudi.absen.get_absen.getAbsenModel import FilterAbsen,AbsenResponse
from ..domain.models_domain.absen_model import MoreAbsen


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

# jadwal-absen
@pembimbingDudiRouter.post("/jadwal-absen",response_model=ResponseModel[JadwalAbsenWithHari],tags=["PEMBIMBING-DUDI/JADWAL-ABSEN"])
async def addJadwalAbsen(jadwal : AddJadwalAbsenBody,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await absenJadwalService.addJadwalAbsen(pembimbing["id_dudi"],jadwal,session)

@pembimbingDudiRouter.get("/jadwal-absen",response_model=ResponseModel[list[JadwalAbsenWithHari]],tags=["PEMBIMBING-DUDI/JADWAL-ABSEN"])
async def getAllJadwalAbsen(pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await absenJadwalService.getAllJadwalAbsen(pembimbing["id_dudi"],session)

@pembimbingDudiRouter.get("/jadwal-absen/{id_jadwal_absen}",response_model=ResponseModel[JadwalAbsenWithHari],tags=["PEMBIMBING-DUDI/JADWAL-ABSEN"])
async def getJadwalAbsenById(id_jadwal_absen : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await absenJadwalService.getJadwalById(id_jadwal_absen,pembimbing["id_dudi"],session)

@pembimbingDudiRouter.put("/jadwal-absen/{id_jadwal_absen}",response_model=ResponseModel[JadwalAbsenWithHari],tags=["PEMBIMBING-DUDI/JADWAL-ABSEN"])
async def updateJadwalAbsen(id_jadwal_absen : int,jadwal : UpdateJadwalAbsenBody = UpdateJadwalAbsenBody(),pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await absenJadwalService.UpdateJadwalAbsen(id_jadwal_absen,pembimbing["id_dudi"],jadwal,session)

@pembimbingDudiRouter.delete("/jadwal-absen/{id_jadwal_absen}",response_model=ResponseModel[JadwalAbsenWithHari],tags=["PEMBIMBING-DUDI/JADWAL-ABSEN"])
async def deleteJadwalAbsen(id_jadwal_absen : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await absenJadwalService.deleteJadwalAbsen(id_jadwal_absen,pembimbing["id_dudi"],session)

# koordinat-absen
@pembimbingDudiRouter.post("/koordinat-absen",response_model=ResponseModel[koordinatAbsenBase],tags=["PEMBIMBING-DUDI/KOORDINAT-ABSEN"])
async def addKoordinatAbsen(koordinat : AddkoordinatAbsenBody,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await koordinatAbsenService.addkoordinatAbsen(pembimbing["id_dudi"],koordinat,session)

@pembimbingDudiRouter.get("/koordinat-absen",response_model=ResponseModel[list[koordinatAbsenBase]],tags=["PEMBIMBING-DUDI/KOORDINAT-ABSEN"])
async def getAllKoordinatAbsen(pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await koordinatAbsenService.getAllkoordinatAbsen(pembimbing["id_dudi"],session)

@pembimbingDudiRouter.get("/koordinat-absen/{id_koordinat_absen}",response_model=ResponseModel[koordinatAbsenBase],tags=["PEMBIMBING-DUDI/KOORDINAT-ABSEN"])
async def getKoordinatAbsenById(id_koordinat_absen : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await koordinatAbsenService.getKoordinatById(pembimbing["id_dudi"],id_koordinat_absen,session)

@pembimbingDudiRouter.put("/koordinat-absen/{id_koordinat_absen}",response_model=ResponseModel[koordinatAbsenBase],tags=["PEMBIMBING-DUDI/KOORDINAT-ABSEN"])
async def updateKoordinatAbsen(id_koordinat_absen : int,koordinat : UpdatekoordinaatAbsenBody = UpdatekoordinaatAbsenBody(),pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await koordinatAbsenService.updatekoordinatAbsen(pembimbing["id_dudi"],id_koordinat_absen,koordinat,session)

@pembimbingDudiRouter.delete("/koordinat-absen/{id_koordinat_absen}",response_model=ResponseModel[koordinatAbsenBase],tags=["PEMBIMBING-DUDI/KOORDINAT-ABSEN"])
async def deleteKoordinatAbsen(id_koordinat_absen : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await koordinatAbsenService.deleteKoordinat(pembimbing["id_dudi"],id_koordinat_absen,session)

# get absen
@pembimbingDudiRouter.get("/absen",response_model=AbsenResponse,tags=["PEMBIMBING-DUDI/ABSEN"])
async def getAllAbsen(isSevenDayAgo : int | None = None,filter : FilterAbsen = Depends(),pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await getAbsenservice.getAllAbsen(pembimbing["id_dudi"],filter,isSevenDayAgo,session)

@pembimbingDudiRouter.get("/absen/{id_absen}",response_model=ResponseModel[MoreAbsen],tags=["PEMBIMBING-DUDI/ABSEN"])
async def getAbsenById(id_absen : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await getAbsenservice.getAbsenById(id_absen,pembimbing["id_dudi"],session)