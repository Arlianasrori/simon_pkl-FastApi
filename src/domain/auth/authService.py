from fastapi import Response
from ..auth.authModel import LoginBody
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...models.developerModel import Developer
from ...models.sekolahModel import Admin
from ...error.errorHandling import HttpException
from ...auth.bcrypt.bcrypt import verify_hash_password
from ...auth.token.create_token import create_token,CreateTokenEnum
from ..models_domain.auth_model import ResponseAuthToken


async def adminDeveloperLogin(auth : LoginBody,Res : Response,session : AsyncSession) -> ResponseAuthToken :
    # find developer and check developer
    findDeveloper = (await session.execute(select(Developer).where(Developer.username == auth.textBody))).scalar_one_or_none()

    if findDeveloper :
        isPassword = auth.password == findDeveloper.password

        if isPassword :
            token_payload = {"id" : findDeveloper.id}

            token = create_token(token_payload,CreateTokenEnum.DEVELOPER)
            Res.set_cookie("access_token",token["access_token"])
            Res.set_cookie("refresh_token",token["refresh_token"])

            return {
                "msg" : "login success",
                "data" : token
            }

    # find admin and check admin
    findAdmin = (await session.execute(select(Admin).where(Admin.username == auth.textBody))).scalar_one_or_none()

    if findAdmin :
        isPassword = verify_hash_password(auth.password,findAdmin.password)

        if isPassword :
            token_payload = {"id" : findAdmin.id}

            token = create_token(token_payload,CreateTokenEnum.ADMIN)
            Res.set_cookie("access_token",token["access_token"])
            Res.set_cookie("refresh_token",token["refresh_token"])

            return {
                "msg" : "login success",
                "data" : token
            }
            
    raise HttpException(status=401,message="username or password wrong")

async def refresh_token_admin(data,Res : Response) :
    token_payload = {"id" : data["id"]}


    token = create_token(token_payload,CreateTokenEnum.ADMIN)
    Res.set_cookie("access_token",token["access_token"],httponly=True,max_age="24 * 60 * 60 * 60")
    Res.set_cookie("refresh_token",token["refresh_token"],httponly=True,max_age="24 * 60 * 60 * 60 * 60")
    return {
        "msg" : "succes",
        "data" : token
    }

async def refresh_token_developer(data,Res : Response) :
    print(data)
    token_payload = {"id" : data["id"]}


    token = create_token(token_payload,CreateTokenEnum.DEVELOPER)
    Res.set_cookie("access_token",token["access_token"],httponly=True,max_age="24 * 60 * 60 * 60")
    Res.set_cookie("refresh_token",token["refresh_token"],httponly=True,max_age="24 * 60 * 60 * 60 * 60")
    return {
        "msg" : "succes",
        "data" : token
    }


#logout
async def logout(Res : Response) :
    Res.delete_cookie("access_token")
    Res.delete_cookie("refresh_token")
    return {
        "msg" : "logout success"
    }