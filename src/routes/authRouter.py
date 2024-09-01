from fastapi import APIRouter,Depends, Request,Response
from ..domain.auth import authService
from ..domain.auth.authModel import LoginBody
from ..domain.models_domain.auth_model import ResponseAuthToken
from ..models.responseModel import ResponseModel
from ..db.sessionDepedency import sessionDepedency

from ..auth.dependsAuthMiddleware.developer.depend_refresh_auth_developer import developerRefreshAuth
from ..auth.dependsAuthMiddleware.admin.depend_refresh_auth_admin import adminrefreshAuth

authRouter = APIRouter(prefix="/auth")


# admin developer auth
@authRouter.post("/adminDeveloper/login",response_model=ResponseModel[ResponseAuthToken],tags=["AUTH/DEVELOPERADMIN"])
async def admin_developer_login(auth : LoginBody,Res : Response,session : sessionDepedency) :
    return await authService.adminDeveloperLogin(auth,Res,session)

@authRouter.post("/developer/refreshToken",dependencies=[Depends(developerRefreshAuth)],response_model=ResponseModel[ResponseAuthToken],tags=["AUTH/DEVELOPERADMIN"])
async def developer_refresh_token(Req : Request,Res : Response) :
    return await authService.refresh_token_developer(Req.developer,Res)

@authRouter.post("/admin/refreshToken",dependencies=[Depends(adminrefreshAuth)],response_model=ResponseModel[ResponseAuthToken],tags=["AUTH/DEVELOPERADMIN"])
async def admin_refresh_token(Req : Request,Res : Response) :
    return await authService.refresh_token_admin(Req.admin,Res)

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