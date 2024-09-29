# Import necessary modules
from fastapi import Cookie, Request, Header

from ....models.guruPembimbingModel import GuruPembimbing
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

# Get the secret key for JWT token verification from environment variables
SECRET_KEY = os.getenv("GURU_PEMBIMBING_SECRET_ACCESS_TOKEN")

async def guruPembimbingAuth(access_token: str | None = Cookie(None), Authorization: str = Header(default=None, example="jwt access token"), req: Request = None, Session: sessionDepedency = None):
    """
    Authenticate a guru pembimbing (supervising teacher) using JWT token.

    Args:
        access_token (str | None): The JWT token from cookies.
        Authorization (str): The JWT token from the Authorization header.
        req (Request): The FastAPI request object.
        Session (sessionDepedency): The database session dependency.

    Raises:
        HttpException: If authentication fails.

    Returns:
        None
    """
    try:
        # Determine the token source (cookie or Authorization header)
        print(access_token)
        token = None
        if access_token:
            token = access_token
        elif Authorization:
            token = Authorization.split(" ")[1]
        
        # Check if a token is present
        if not token:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Decode and verify the JWT token
        guruPembimbing = jwt.decode(token, SECRET_KEY, algorithms="HS256")

        # Check if guru pembimbing information exists in the decoded token
        if not guruPembimbing:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Create a select query to find the guru pembimbing in the database
        selectQuery = select(GuruPembimbing.id, GuruPembimbing.nama, GuruPembimbing.token_FCM, GuruPembimbing.id_sekolah).where(GuruPembimbing.id == guruPembimbing["id"])
        exec = await Session.execute(selectQuery)
        findGuruPembimbing = exec.first()

        # Check if the guru pembimbing exists in the database
        if not findGuruPembimbing:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Add guru pembimbing information to the request object
        print("masuk")
        req.guruPembimbing = findGuruPembimbing._asdict()
    except JWTError as error:
        # Handle JWT decoding errors
        raise HttpException(status=401, message=str(error.args[0]))
