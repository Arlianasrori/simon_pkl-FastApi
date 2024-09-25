# Import necessary modules
from fastapi import Cookie, Request, Header
from ....models.pembimbingDudiModel import PembimbingDudi
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

# Get the secret key for refresh token from environment variables
SECRET_KEY = os.getenv("PEMBIMBING_DUDI_SECRET_REFRESH_TOKEN")

async def pembimbingDudiRefreshAuth(refresh_token: str | None = Cookie(None), Authorization: str = Header(default=None, example="jwt access token"), req: Request = None, Session: sessionDepedency = None):
    """
    Authenticate a pembimbing dudi (industry supervisor) using refresh token.

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
        token = None
        if refresh_token:
            token = refresh_token
        elif Authorization:
            token = Authorization.split(" ")[1]

        # Check if a token is present
        if not token:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Decode and verify the JWT refresh token
        pemimbingDudi = jwt.decode(token, SECRET_KEY, algorithms="HS256")

        # Check if pembimbing dudi information exists in the decoded token
        if not pemimbingDudi:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Create a select query to find the pembimbing dudi in the database
        selectQuery = select(PembimbingDudi.id, PembimbingDudi.nama, PembimbingDudi.token_FCM, PembimbingDudi.id_sekolah).where(PembimbingDudi.id == pemimbingDudi["id"])
        exec = await Session.execute(selectQuery)
        findPembimbingDudi = exec.first()

        # Check if the pembimbing dudi exists in the database
        if not findPembimbingDudi:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Add pembimbing dudi information to the request object
        req.pembimbingDudi = findPembimbingDudi._asdict()
    except JWTError as error:
        # Handle JWT decoding errors
        raise HttpException(status=401, message=str(error.args[0]))
