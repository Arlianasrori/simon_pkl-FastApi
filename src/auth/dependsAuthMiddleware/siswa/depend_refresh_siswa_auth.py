# Import necessary modules
from fastapi import Cookie, Request, Header
from ....models.siswaModel import Siswa
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

# Get the secret key for refresh token from environment variables
SECRET_KEY = os.getenv("SISWA_SECRET_REFRESH_TOKEN")

async def siswaRefreshAuth(refresh_token: str | None = Cookie(None), Authorization: str = Header(default=None, example="jwt access token"), req: Request = None, Session: sessionDepedency = None):
    """
    Authenticate a student (siswa) using refresh token.

    Args:
        refresh_token (str | None): The JWT refresh token from cookies.
        Authorization (str): The JWT refresh token from the Authorization header.
        req (Request): The FastAPI request object.
        Session (sessionDepedency): The database session dependency.

    Raises:
        HttpException: If authentication fails.

    Returns:
        None
    """
    try:
        # Determine the token source (cookie or Authorization header)
        if refresh_token:
            token = refresh_token
        elif Authorization:
            token = Authorization.split(" ")[1]
        
        # Check if a token is present
        if not token:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Decode and verify the JWT refresh token
        siswa = jwt.decode(token, SECRET_KEY, algorithms="HS256")

        # Check if student information exists in the decoded token
        if not siswa:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Create a select query to find the student in the database
        selectQuery = select(Siswa.id, Siswa.nama, Siswa.token_FCM, Siswa.jenis_kelamin, Siswa.id_sekolah).where(Siswa.id == siswa["id"])
        exec = await Session.execute(selectQuery)
        findSiswa = exec.first()

        # Check if the student exists in the database
        if not findSiswa:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Add student information to the request object
        req.siswa = findSiswa._asdict()
    except JWTError as error:
        # Handle JWT decoding errors
        raise HttpException(status=401, message=str(error.args[0]))
