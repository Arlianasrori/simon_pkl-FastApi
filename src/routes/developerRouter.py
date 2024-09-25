from fastapi import APIRouter,Depends, Request, UploadFile

# model and service
from ..domain.developer.developerModel import Developer,AddSekolahBody,UpdateSekolahBody,AddAdminBody,UpdateAdminBody
from ..domain.developer import developerService

from ..domain.models_domain.sekolah_model import SekolahBase,SekolahWithAlamat,MoreSekolahBase,AdminWithSekolah,AdminBase
from ..domain.models_domain.alamat_model import AlamatBase,UpdateAlamatBody
from ..models.responseModel import ResponseModel

# depends
from ..auth.dependsAuthMiddleware.developer.depend_auth_developer import developerAuth
from ..db.sessionDepedency import sessionDepedency

developerRouter = APIRouter(prefix="/developer",dependencies=[Depends(developerAuth)])


# admin developer auth
@developerRouter.get("/",response_model=ResponseModel[Developer],tags=["DEVELOPER"])
async def getDeveloper(Req : Request) :
    return {
        "msg" : "success",
        "data" : Req.developer
    }

# sekolah
@developerRouter.post("/sekolah",response_model=ResponseModel[SekolahWithAlamat],tags=["DEVELOPER/SEKOLAH"])
async def add_sekolah(sekolah : AddSekolahBody,alamat : AlamatBase,session : sessionDepedency) :
    return await developerService.add_sekolah(sekolah,alamat,session)

@developerRouter.patch("/sekolah/logo/{id_sekolah}",response_model=ResponseModel[SekolahBase],tags=["DEVELOPER/SEKOLAH"])
async def update_logo_sekolah(id_sekolah : int,logo : UploadFile,session : sessionDepedency) :
    return await developerService.add_update_foto_profile_sekolah(id_sekolah,logo,session)

@developerRouter.get("/sekolah",response_model=ResponseModel[list[SekolahWithAlamat]],tags=["DEVELOPER/SEKOLAH"])
async def get_all_sekolah(session : sessionDepedency) :
    return await developerService.getAllsekolah(session)

@developerRouter.get("/sekolah/{id_sekolah}",response_model=ResponseModel[MoreSekolahBase],tags=["DEVELOPER/SEKOLAH"])
async def get_sekolah_by_id(id_sekolah : int,session : sessionDepedency) :
    return await developerService.getSekolahById(id_sekolah,session)

@developerRouter.put("/sekolah/{id_sekolah}",response_model=ResponseModel[SekolahWithAlamat],tags=["DEVELOPER/SEKOLAH"])
async def update_sekolah(id_sekolah : int,sekolah : UpdateSekolahBody | None = None,alamat : UpdateAlamatBody | None = None,session : sessionDepedency = None) :
    return await developerService.updateSekolah(id_sekolah,sekolah,alamat,session)

@developerRouter.delete("/sekolah/{id_sekolah}",response_model=ResponseModel[SekolahBase],tags=["DEVELOPER/SEKOLAH"])
async def delete_sekolah(id_sekolah : int,session : sessionDepedency) :
    return await developerService.deleteSekolah(id_sekolah,session)

# admin
@developerRouter.post("/admin",response_model=ResponseModel[AdminWithSekolah],tags=["DEVELOPER/ADMIN"])
async def add_admin(admin : AddAdminBody,session : sessionDepedency) :
    return await developerService.add_admin_sekolah(admin,session)

@developerRouter.get("/admin",response_model=ResponseModel[list[AdminWithSekolah]],tags=["DEVELOPER/ADMIN"])
async def get_all_admin(session : sessionDepedency) :
    return await developerService.get_all_admin_sekolah(session)

@developerRouter.get("/admin/{id_admin}",response_model=ResponseModel[AdminWithSekolah],tags=["DEVELOPER/ADMIN"])
async def get_admin_by_id(id_admin : int,session : sessionDepedency) :
    return await developerService.get_admin_sekolah_by_id(id_admin,session)
    
@developerRouter.put("/admin/{id_admin}",response_model=ResponseModel[AdminWithSekolah],tags=["DEVELOPER/ADMIN"])
async def update_admin(id_admin : int,admin : UpdateAdminBody | None = None,session : sessionDepedency = None) :
    return await developerService.update_admin_sekolah(id_admin,admin,session)

@developerRouter.delete("/admin/{id_admin}",response_model=ResponseModel[AdminBase],tags=["DEVELOPER/ADMIN"])
async def delete_admin(id_admin : int,session : sessionDepedency) :
    return await developerService.delete_admin_sekolah(id_admin,session)

