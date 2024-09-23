from fastapi import Response
from ..auth.authModel import LoginBody
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# models
from ...models.developerModel import Developer
from ...models.sekolahModel import Admin
from ...models.siswaModel import Siswa
from ...models.guruPembimbingModel import GuruPembimbing
from ...models.pembimbingDudiModel import PembimbingDudi
from ..models_domain.auth_model import ResponseAuthToken, ResponseRefreshToken,RoleEnum

# common
from ...error.errorHandling import HttpException
from ...auth.bcrypt.bcrypt import verify_hash_password
from ...auth.token.create_token import create_token,CreateTokenEnum


# admin developer
async def adminDeveloperLogin(auth : LoginBody,Res : Response,session : AsyncSession) -> ResponseAuthToken :
    """
    Authenticate admin or developer login.

    Args:
        auth (LoginBody): Login credentials.
        Res (Response): FastAPI response object.
        session (AsyncSession): Database session.

    Returns:
        ResponseAuthToken: Authentication token and role.

    Raises:
        HttpException: If authentication fails.
    """
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
                "data" : {
                    **token,
                    "role" : RoleEnum.DEVELOPER
                }
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
                "data" : {
                    **token,
                    "role" : RoleEnum.ADMIN
                }
            }
            
    raise HttpException(status=400,message="username or password wrong")


async def allUserAuth(auth : LoginBody,Res : Response,session : AsyncSession) -> ResponseAuthToken :
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
                "data" : {
                    **token,
                    "role" : RoleEnum.DEVELOPER
                }
            }

    # find admin and check admin
    findAdmin = (await session.execute(select(Admin).where(Admin.username == auth.textBody))).scalar_one_or_none()

    if findAdmin :
        # isPassword = verify_hash_password(auth.password,findAdmin.password)
        isPassword = auth.password == findAdmin.password

        if isPassword :
            token_payload = {"id" : findAdmin.id}

            token = create_token(token_payload,CreateTokenEnum.ADMIN)
            Res.set_cookie("access_token",token["access_token"])
            Res.set_cookie("refresh_token",token["refresh_token"])

            return {
                "msg" : "login success",              
                "data" : {
                    **token,
                    "role" : RoleEnum.ADMIN
                }
            }

    # find siswa and check siswa
    findSiswa = (await session.execute(select(Siswa).where(Siswa.nis == auth.textBody))).scalar_one_or_none()

    if findSiswa :
        isPassword = verify_hash_password(auth.password,findSiswa.password)

        if isPassword :
            token_payload = {"id" : findSiswa.id}

            token = create_token(token_payload,CreateTokenEnum.SISWA)
            Res.set_cookie("access_token",token["access_token"])
            Res.set_cookie("refresh_token",token["refresh_token"])

            return {
                "msg" : "login success",              
                "data" : {
                    **token,
                    "role" : RoleEnum.SISWA
                }
            }
        
    # find guru and check guru
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.nip == auth.textBody))).scalar_one_or_none()

    if findGuruPembimbing :
        isPassword = verify_hash_password(auth.password,findGuruPembimbing.password)

        if isPassword :
            token_payload = {"id" : findGuruPembimbing.id}

            token = create_token(token_payload,CreateTokenEnum.GURU_PEMBIMBING)
            Res.set_cookie("access_token",token["access_token"])
            Res.set_cookie("refresh_token",token["refresh_token"])

            return {
                "msg" : "login success",              
                "data" : {
                    **token,
                    "role" : RoleEnum.GURU_PEMBIMBING
                }
            }
        
    # find pembimbing dudi and check pembimbing dudi
    findPembimbngDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.username == auth.textBody))).scalar_one_or_none()

    if findPembimbngDudi :
        isPassword = verify_hash_password(auth.password,findPembimbngDudi.password)

        if isPassword :
            token_payload = {"id" : findPembimbngDudi.id}

            token = create_token(token_payload,CreateTokenEnum.PEMBIMBING_DUDI)
            Res.set_cookie("access_token",token["access_token"])
            Res.set_cookie("refresh_token",token["refresh_token"])

            return {
                "msg" : "login success",              
                "data" : {
                    **token,
                    "role" : RoleEnum.PEMBIMBING_DUDI
                }
            }
    raise HttpException(status=400,message="username or password wrong")


async def refresh_token_admin(data,Res : Response) -> ResponseRefreshToken :
    """
    Refresh authentication token for admin.

    Args:
        data: User data.
        Res (Response): FastAPI response object.

    Returns:
        ResponseRefreshToken: New authentication token.
    """
    token_payload = {"id" : data["id"]}


    token = create_token(token_payload,CreateTokenEnum.ADMIN)
    Res.set_cookie("access_token",token["access_token"],httponly=True,max_age="24 * 60 * 60 * 60")
    Res.set_cookie("refresh_token",token["refresh_token"],httponly=True,max_age="24 * 60 * 60 * 60 * 60")
    return {
        "msg" : "succes",
        "data" : token
    }

async def refresh_token_developer(data,Res : Response) -> ResponseRefreshToken:
    """
    Refresh authentication token for developer.

    Args:
        data: User data.
        Res (Response): FastAPI response object.

    Returns:
        ResponseRefreshToken: New authentication token.
    """
    print(data)
    token_payload = {"id" : data["id"]}


    token = create_token(token_payload,CreateTokenEnum.DEVELOPER)
    Res.set_cookie("access_token",token["access_token"],httponly=True,max_age="24 * 60 * 60 * 60")
    Res.set_cookie("refresh_token",token["refresh_token"],httponly=True,max_age="24 * 60 * 60 * 60 * 60")
    return {
        "msg" : "succes",
        "data" : token
    }


# public login
async def publicLogin(auth : LoginBody,Res : Response,session : AsyncSession) -> ResponseAuthToken :
    """
    Authenticate public user login (student, teacher, or DUDI supervisor).

    Args:
        auth (LoginBody): Login credentials.
        Res (Response): FastAPI response object.
        session (AsyncSession): Database session.

    Returns:
        ResponseAuthToken: Authentication token and role.

    Raises:
        HttpException: If authentication fails.
    """
    # check siswa
    findSiswa = (await session.execute(select(Siswa).where(Siswa.nis == auth.textBody))).scalar_one_or_none()

    if findSiswa :
        isPassword = verify_hash_password(auth.password,findSiswa.password)

        if isPassword :
            token_payload = {"id" : findSiswa.id}

            token = create_token(token_payload,CreateTokenEnum.SISWA)
            Res.set_cookie("access_token",token["access_token"])
            Res.set_cookie("refresh_token",token["refresh_token"])

            return {
                "msg" : "login success",
                "data" : {
                    **token,
                    "role" : RoleEnum.SISWA
                }
            }

    # check guru pembimbing
    findGuru = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.nip == auth.textBody))).scalar_one_or_none()

    if findGuru :
        isPassword = verify_hash_password(auth.password,findGuru.password)

        if isPassword :
            token_payload = {"id" : findGuru.id}

            token = create_token(token_payload,CreateTokenEnum.GURU_PEMBIMBING)
            Res.set_cookie("access_token",token["access_token"])
            Res.set_cookie("refresh_token",token["refresh_token"])

            return {
                "msg" : "login success",
                "data" : {
                    **token,
                    "role" : RoleEnum.GURU_PEMBIMBING
                }
            }


    # check pembimbing dudi
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.username == auth.textBody))).scalar_one_or_none()

    if findPembimbingDudi :
        isPassword = verify_hash_password(auth.password,findPembimbingDudi.password)
        print(findPembimbingDudi.password)

        if isPassword :
            token_payload = {"id" : findPembimbingDudi.id}

            token = create_token(token_payload,CreateTokenEnum.PEMBIMBING_DUDI)
            Res.set_cookie("access_token",token["access_token"])
            Res.set_cookie("refresh_token",token["refresh_token"])

            return {
                "msg" : "login success",
                "data" : {
                    **token,
                    "role" : RoleEnum.PEMBIMBING_DUDI
                }
            } 
            
    raise HttpException(status=400,message="nis/username/password or password wrong")


# siswa
async def refresh_token_siswa(data,Res : Response) -> ResponseRefreshToken :
    """
    Refresh authentication token for student.

    Args:
        data: User data.
        Res (Response): FastAPI response object.

    Returns:
        ResponseRefreshToken: New authentication token.
    """
    token_payload = {"id" : data["id"]}


    token = create_token(token_payload,CreateTokenEnum.SISWA)
    Res.set_cookie("access_token",token["access_token"],httponly=True,max_age="24 * 60 * 60 * 60")
    Res.set_cookie("refresh_token",token["refresh_token"],httponly=True,max_age="24 * 60 * 60 * 60 * 60")
    return {
        "msg" : "succes",
        "data" : token
    }

# guru pembimbing
async def refresh_token_guru_pembimbing(data,Res : Response) -> ResponseRefreshToken :
    """
    Refresh authentication token for teacher.

    Args:
        data: User data.
        Res (Response): FastAPI response object.

    Returns:
        ResponseRefreshToken: New authentication token.
    """
    token_payload = {"id" : data["id"]}


    token = create_token(token_payload,CreateTokenEnum.GURU_PEMBIMBING)
    Res.set_cookie("access_token",token["access_token"],httponly=True,max_age="24 * 60 * 60 * 60")
    Res.set_cookie("refresh_token",token["refresh_token"],httponly=True,max_age="24 * 60 * 60 * 60 * 60")
    return {
        "msg" : "succes",
        "data" : token
    }

# pembimbing dudi
async def refresh_token_pembimbing_dudi(data,Res : Response) -> ResponseRefreshToken :
    """
    Refresh authentication token for DUDI supervisor.

    Args:
        data: User data.
        Res (Response): FastAPI response object.

    Returns:
        ResponseRefreshToken: New authentication token.
    """
    token_payload = {"id" : data["id"]}


    token = create_token(token_payload,CreateTokenEnum.PEMBIMBING_DUDI)
    Res.set_cookie("access_token",token["access_token"],httponly=True,max_age="24 * 60 * 60 * 60")
    Res.set_cookie("refresh_token",token["refresh_token"],httponly=True,max_age="24 * 60 * 60 * 60 * 60")
    return {
        "msg" : "succes",
        "data" : token
    }

#logout
async def logout(Res : Response) :
    """
    Log out user by deleting authentication cookies.

    Args:
        Res (Response): FastAPI response object.

    Returns:
        dict: Success message.
    """
    Res.delete_cookie("access_token")
    Res.delete_cookie("refresh_token")
    return {
        "msg" : "logout success"
    }