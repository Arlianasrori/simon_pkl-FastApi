from fastapi import APIRouter,Depends, Request,Response
from ..domain.auth import authService
from ..domain.auth.authModel import LoginBody
from ..domain.models_domain.auth_model import ResponseAuthToken,ResponseRefreshToken
from ..models.responseModel import ResponseModel
from ..db.sessionDepedency import sessionDepedency

# depends
from ..auth.dependsAuthMiddleware.developer.depend_refresh_auth_developer import developerRefreshAuth
from ..auth.dependsAuthMiddleware.admin.depend_refresh_auth_admin import adminrefreshAuth
from ..auth.dependsAuthMiddleware.siswa.depend_refresh_siswa_auth import siswaRefreshAuth
from ..auth.dependsAuthMiddleware.pembimbing_dudi.depend_refresh_auth_pembimbing_dudi import pembimbingDudiRefreshAuth
from ..auth.dependsAuthMiddleware.guru_pembimbing.depend_refresh_auth_guru_pembimbing import guruPembimbingRefreshAuth


authRouter = APIRouter(prefix="/auth")


# admin developer auth
@authRouter.post("/adminDeveloper/login",response_model=ResponseModel[ResponseAuthToken],tags=["AUTH/DEVELOPERADMIN"])
async def admin_developer_login(auth : LoginBody,Res : Response,session : sessionDepedency) :
    return await authService.adminDeveloperLogin(auth,Res,session)

@authRouter.post("/developer/refreshToken",dependencies=[Depends(developerRefreshAuth)],response_model=ResponseModel[ResponseRefreshToken],tags=["AUTH/DEVELOPERADMIN"])
async def developer_refresh_token(Req : Request,Res : Response) :
    return await authService.refresh_token_developer(Req.developer,Res)

@authRouter.post("/admin/refreshToken",dependencies=[Depends(adminrefreshAuth)],response_model=ResponseModel[ResponseRefreshToken],tags=["AUTH/DEVELOPERADMIN"])
async def admin_refresh_token(Req : Request,Res : Response) :
    return await authService.refresh_token_admin(Req.admin,Res)


# public login
@authRouter.post("/public/login",response_model=ResponseModel[ResponseAuthToken],tags=["AUTH/PUBLIC"])
async def public_login(auth : LoginBody,Res : Response,session : sessionDepedency) :
    return await authService.publicLogin(auth,Res,session)


# siswa
@authRouter.post("/siswa/refreshToken",dependencies=[Depends(siswaRefreshAuth)],response_model=ResponseModel[ResponseRefreshToken],tags=["AUTH/SISWA"])
async def siswa_refresh_token(Req : Request,Res : Response) :
    return await authService.refresh_token_siswa(Req.siswa,Res)

# guru pembimbing
@authRouter.post("/guruPembimbing/refreshToken",dependencies=[Depends(guruPembimbingRefreshAuth)],response_model=ResponseModel[ResponseRefreshToken],tags=["AUTH/GURUPEMBIMBING"])
async def guru_pembimbing_refresh_token(Req : Request,Res : Response) :
    return await authService.refresh_token_guru_pembimbing(Req.guruPembimbing,Res)

# pembimbing dudi
@authRouter.post("/pembimbingDudi/refreshToken",dependencies=[Depends(pembimbingDudiRefreshAuth)],response_model=ResponseModel[ResponseRefreshToken],tags=["AUTH/PEMBIMBINGDUDI"])
async def pembimbing_dudi_refresh_token(Req : Request,Res : Response) :
    return await authService.refresh_token_pembimbing_dudi(Req.pembimbingDudi,Res)


# all logout
@authRouter.post("/logout",responses={"200" : {"content": {
                "application/json": {
                    "example" : {
                        "msg" : "logout success"
                    }
                }
            }}},tags=["AUTH"])
async def logout(Res : Response) :
    return await authService.logout(Res)