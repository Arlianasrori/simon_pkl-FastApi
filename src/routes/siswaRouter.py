from fastapi import APIRouter,Depends, UploadFile,Form,File

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
from ..domain.siswa.laporan_pkl_siswa.laporanPklSiswaModel import AddLaporanPklSiswaBody,UpdateLaporanPklSiswaBody,ResponseGetLaporanPklSiswaPag,FilterLaporan

# laporan-dudi-pkl
from ..domain.siswa.laporan_pkl_dudi import laporanPklDudiService
from ..domain.siswa.laporan_pkl_dudi.laporanPklDudiModel import ResponseGetLaporanPklDudiPag
from ..domain.models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase

# radius-absen
from ..domain.siswa.absen.radius_absen import radiusAbsenService
from ..domain.siswa.absen.radius_absen.radiusAbsenModel import CekRadiusAbsenBody,ResponseCekRadius
from ..domain.models_domain.absen_model import koordinatAbsenBase

# absen-jadwal
from ..domain.siswa.absen.absen_jadwal import absenJadwalService
from ..domain.siswa.absen.absen_jadwal.absenJadwalModel import RadiusBody,ResponseCekAbsen,ResponseJadwalAbsenToday
from ..domain.models_domain.absen_model import JadwalAbsenWithHari

# absen-event
from ..domain.siswa.absen.absen_event import absenEventService
from ..domain.siswa.absen.absen_event.absenEventModel import RadiusBody,IzinTelatAbsenEnum,ResponseAbsenIzinTelat
from ..domain.models_domain.absen_model import AbsenBase,AbsenWithKeteranganPulang,MoreAbsen

# get-absen
from ..domain.siswa.absen.get_absen import getAbsenService
from ..domain.siswa.absen.get_absen.getAbsenModel import FilterAbsen,AbsenResponse
from ..domain.models_domain.absen_model import MoreAbsen

# notification
from ..domain.siswa.notification import notificationService
from ..domain.models_domain.notification_model import NotificationModelBase,ResponseGetUnreadNotification

from ..db.sessionDepedency import sessionDepedency
from ..models.responseModel import ResponseModel

# laporan kendala
from ..domain.siswa.laporankendala import laporanKendalaService
from ..domain.siswa.laporankendala.laporanKendalaModel import AddLaporanKendalaBody,UpdateLaporanKendalaBody
from ..domain.models_domain.laporan_kendala_model import LaporankendalaBase,LaporanKendalaWithSiswa

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
async def getAllLaporanPklSiswa(page : int,filter : FilterLaporan = Depends(),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanPklSiswaService.getAllLaporanPklSiswa(siswa["id"],filter,page,session)

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

# radius-absen
@siswaRouter.get("/koordinat-absen",response_model=ResponseModel[list[koordinatAbsenBase]],description="used to view the list of coordinates permitted by dudi",tags=["SISWA/RADIUS-ABSEN"])
async def getKoordinatAbsen(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await radiusAbsenService.getAllkoordinatAbsen(siswa["id_dudi"],session)

@siswaRouter.post("/koordinat-absen/cek",response_model=ResponseModel[ResponseCekRadius],description="if the user is outside the radius and clicks the absent button outside the radius: call checkabsenschedule first, if the type of absence is home absence then it is permissible to be absent outside the radius and if other than that it is not permitted",tags=["SISWA/RADIUS-ABSEN"])
async def cekRadiusAbsen(koordinat : CekRadiusAbsenBody,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await radiusAbsenService.cekRadiusAbsen(siswa["id_dudi"],koordinat,session)

# absen-jadwal
@siswaRouter.get("/absen-jadwal",response_model=ResponseModel[list[JadwalAbsenWithHari]],tags=["SISWA/ABSEN-JADWAL"])
async def getAllAbsenJadwal(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await absenJadwalService.getAllJadwalAbsen(siswa["id_dudi"],session)

@siswaRouter.get("/absen-jadwal/{id_jadwal}",response_model=ResponseModel[JadwalAbsenWithHari],tags=["SISWA/ABSEN-JADWAL"])
async def getAbsenJadwalById(id_jadwal : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await absenJadwalService.getJadwalAbsenById(siswa["id_dudi"],id_jadwal,session)

@siswaRouter.post("/absen-jadwal/cek",response_model=ResponseModel[ResponseCekAbsen],description="""used to check what the user can do today.

flow : 
- check the type of absence first
- if absence_type == "pulang" continue to look at home_absence_type to determine the button
and vice versa.
                  
canAbsent: used to check whether students can be absent today or not""",tags=["SISWA/ABSEN-JADWAL"])
async def cekAbsenJadwal(koordinat : RadiusBody,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await absenJadwalService.cekAbsen(siswa["id"],siswa["id_dudi"],koordinat,session)

@siswaRouter.get("/absen-jadwal/cek/today",response_model=ResponseModel[list[JadwalAbsenWithHari]],tags=["SISWA/ABSEN-JADWAL"])
async def cekAbsenJadwalToday(koordinat : RadiusBody,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await absenJadwalService.getJadwalAbsenToday(siswa["id"],siswa["id_dudi"],koordinat,session)

# absen
@siswaRouter.post("/absen/absen-masuk",response_model=ResponseModel[AbsenBase],tags=["SISWA/ABSEN"])
async def absenMasuk(latitude: float = Form(...),longitude: float = Form(...),foto: UploadFile = File(...),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    radius = RadiusBody(latitude=latitude, longitude=longitude)
    return await absenEventService.absenMasuk(siswa["id"],siswa["id_dudi"],radius,foto,session)

@siswaRouter.post("/absen/absen-pulang",response_model=ResponseModel[AbsenBase],tags=["SISWA/ABSEN"])
async def absenPulang(latitude: float = Form(...),longitude: float = Form(...),foto: UploadFile = File(...),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    radius = RadiusBody(latitude=latitude, longitude=longitude)
    return await absenEventService.absenPulang(siswa["id"],siswa["id_dudi"],radius,foto,session)

@siswaRouter.post("/absen/absen-diluar-radius",response_model=ResponseModel[AbsenWithKeteranganPulang],tags=["SISWA/ABSEN"])
async def absenDiluarRadius(latitude: float = Form(...),longitude: float = Form(...),note : str = Form(...),foto: UploadFile = File(...),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    radius = RadiusBody(latitude=latitude, longitude=longitude)
    return await absenEventService.absenDiluarRadius(siswa["id"],siswa["id_dudi"],note,radius,foto,session)

@siswaRouter.post("/absen/absen-izin-telat",response_model=ResponseAbsenIzinTelat,description="statusIzinTelat containst between izin and telat",tags=["SISWA/ABSEN"])
async def absenizinTelat(latitude: float = Form(...),longitude: float = Form(...),note : str = Form(...),statusizinTelat : IzinTelatAbsenEnum = Form(...), foto: UploadFile = File(...),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    radius = RadiusBody(latitude=latitude, longitude=longitude)
    return await absenEventService.absenIzinTelat(siswa["id"],siswa["id_dudi"],note,statusizinTelat,radius,foto,session)

@siswaRouter.post("/absen/absen-sakit",response_model=ResponseModel[AbsenBase],tags=["SISWA/ABSEN"])
async def absenSakit(latitude: float = Form(...),longitude: float = Form(...),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    radius = RadiusBody(latitude=latitude, longitude=longitude)
    return await absenEventService.absenSakit(siswa["id"],radius,session)

# get-absen
@siswaRouter.get("/absen",response_model=ResponseModel[list[MoreAbsen]] | AbsenResponse,tags=["SISWA/GETABSEN"])
async def getAllAbsen(isSevenDayAgo : bool | None = None,isGrouping : bool | None = None,siswa : dict = Depends(getSiswaAuth),filter : FilterAbsen = Depends(),session : sessionDepedency = None):
    return await getAbsenService.getAllAbsen(siswa["id"],filter,isSevenDayAgo,isGrouping,session)

@siswaRouter.get("/absen/{id_absen}",response_model=ResponseModel[AbsenBase],tags=["SISWA/GETABSEN"])
async def getAbsenById(id_absen : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await getAbsenService.getAbsenById(id_absen,siswa["id"],session)

# notification
@siswaRouter.get("/notification",response_model=ResponseModel[list[NotificationModelBase]],tags=["SISWA/NOTIFICATION"])
async def getAllNotification(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await notificationService.getAllNotification(siswa["id"],siswa["id_dudi"],session)

@siswaRouter.get("/notification/{id_notification}",response_model=ResponseModel[NotificationModelBase],tags=["SISWA/NOTIFICATION"])
async def getNotificationById(id_notification : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await notificationService.getNotificationById(id_notification,siswa["id"],siswa["id_dudi"],session)

@siswaRouter.post("/notification/read/{id_notification}",response_model=ResponseModel[NotificationModelBase],tags=["SISWA/NOTIFICATION"])
async def readNotification(id_notification : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await notificationService.readNotification(id_notification,siswa["id"],siswa["id_dudi"],session)

@siswaRouter.get("/notification/unread/count",response_model=ResponseModel[ResponseGetUnreadNotification],tags=["SISWA/NOTIFICATION"])
async def getCountNotification(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await notificationService.getCountNotification(siswa["id"],siswa["id_dudi"],session)

# laporan kendala
@siswaRouter.post("/laporan-kendala",response_model=ResponseModel[LaporankendalaBase],tags=["SISWA/LAPORAN-KENDALA"])
async def addLaporanKendala(laporan : AddLaporanKendalaBody,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanKendalaService.addLaporanPKLKendalaSiswa(siswa["id"],laporan,session)

@siswaRouter.get("/laporan-kendala",response_model=ResponseModel[list[LaporankendalaBase]],tags=["SISWA/LAPORAN-KENDALA"])
async def getAllLaporanKendala(siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanKendalaService.getAllLaporanKendala(siswa["id"],session)

@siswaRouter.get("/laporan-kendala/{id_laporan_kendala}",response_model=ResponseModel[LaporanKendalaWithSiswa],tags=["SISWA/LAPORAN-KENDALA"])
async def getLaporanKendalaById(id_laporan_kendala : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanKendalaService.getLaporanKendalaById(siswa["id"],id_laporan_kendala,session)

@siswaRouter.put("/laporan-kendala/{id_laporan_kendala}",response_model=ResponseModel[LaporankendalaBase],tags=["SISWA/LAPORAN-KENDALA"])
async def updateLaporanKendala(id_laporan_kendala : int,laporan : UpdateLaporanKendalaBody = UpdateLaporanKendalaBody(),siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanKendalaService.updateLaporanKendala(siswa["id"],id_laporan_kendala,laporan,session)

@siswaRouter.put("/laporan-kendala/file_laporan/{id_laporan_kendala}",response_model=ResponseModel[LaporankendalaBase],tags=["SISWA/LAPORAN-KENDALA"])
async def uploadUpdateFileLaporanKendala(id_laporan_kendala : int,file_laporan : UploadFile,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanKendalaService.addUpdateFileLaporanKendala(siswa["id"],id_laporan_kendala,file_laporan,session)

@siswaRouter.delete("/laporan-kendala/{id_laporan_kendala}",response_model=ResponseModel[LaporankendalaBase],tags=["SISWA/LAPORAN-KENDALA"])
async def deleteLaporanKendala(id_laporan_kendala : int,siswa : dict = Depends(getSiswaAuth),session : sessionDepedency = None):
    return await laporanKendalaService.deleteLaporanPklKendala(siswa["id"],id_laporan_kendala,session)

