from fastapi import Cookie, Request

from ....models.sekolahModel import Admin
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

# Secret key for JWT token verification
SECRET_KEY = os.getenv("ADMIN_SECRET_ACCESS_TOKEN")

async def adminAuth(access_token: str | None = Cookie(None), req: Request = None, Session: sessionDepedency = None):
    """
    Authenticate admin user based on access token.

    Args:
        access_token (str | None): JWT access token from cookie
        req (Request): FastAPI request object
        Session (sessionDepedency): Database session dependency

    Raises:
        HttpException: If authentication fails

    Returns:
        None
    """
    print(access_token)
    if not access_token:
        raise HttpException(status=401, message="invalid token(unauthorized)")
    try:
        # Decode and verify JWT token
        admin = jwt.decode(access_token, SECRET_KEY, algorithms="HS256")

        if not admin:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Query database for admin user
        selectQuery = select(Admin.id, Admin.username, Admin.id_sekolah).where(Admin.id == admin["id"])
        exec = await Session.execute(selectQuery)
        findAdmin = exec.first()

        if not findAdmin:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Attach admin info to request object
        req.admin = findAdmin._asdict()
    except JWTError as error:
        # Handle JWT decoding errors
        raise HttpException(status=401, message=str(error.args[0]))
