from fastapi import APIRouter,Depends

from ..domain.models_domain.pembimbing_dudi_model import PembimbingDudiBase,PembimbingDudiWithAlamatDudi
from ..domain.models_domain.siswa_model import MoreSiswa

# domain
from ..domain.pembimbing_dudi.profile_auth import profileAuthService
from ..domain.pembimbing_dudi.siswa_manage import siswaManageService
from ..domain.pembimbing_dudi.siswa_manage.siswaManageModel import ResponseSiswaPag

# auth
from ..auth.dependsAuthMiddleware.pembimbing_dudi.depend_auth_pembimbing_dudi import pembimbingDudiAuth
from ..auth.dependsAuthMiddleware.pembimbing_dudi.get_pembimbing_dudi_auth import getPembimbingDudiAuth

# kouta
from ..domain.pembimbing_dudi.kouta_dudi.koutaDudiService import getKoutaDudi,AddKoutaDudiBody,UpdateKoutaDudiBody
from ..domain.models_domain.dudi_model import DudiWithKouta
from ..domain.pembimbing_dudi.kouta_dudi import koutaDudiService
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

# siswa
@pembimbingDudiRouter.get("/siswa",response_model=ResponseModel[list[MoreSiswa] | ResponseSiswaPag],tags=["PEMBIMBING-DUDI/SISWA"])
async def getAllSiswa(page : int | None = None,pembimbingDudi : dict = Depends(getPembimbingDudiAuth), session : sessionDepedency = None) :
    print(pembimbingDudi)
    return await siswaManageService.getSiswa(pembimbingDudi["id"],page,session)


@pembimbingDudiRouter.get("/siswa/{id_siswa}",response_model=ResponseModel[MoreSiswa],tags=["PEMBIMBING-DUDI/SISWA"])
async def getSiswaById(id_siswa : int,pembimbing : dict = Depends(getPembimbingDudiAuth),session : sessionDepedency = None) :
    return await siswaManageService.getSiswaById(pembimbing["id"],id_siswa,session)

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