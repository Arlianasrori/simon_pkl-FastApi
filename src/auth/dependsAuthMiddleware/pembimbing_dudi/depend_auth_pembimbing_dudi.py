# Import necessary modules
from fastapi import Cookie, Request, Header
from ....models.pembimbingDudiModel import PembimbingDudi
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

# Get the secret key for JWT token verification from environment variables
SECRET_KEY = os.getenv("PEMBIMBING_DUDI_SECRET_ACCESS_TOKEN")

async def pembimbingDudiAuth(access_token: str | None = Cookie(None), Authorization: str = Header(default=None, example="jwt access token"), req: Request = None, Session: sessionDepedency = None):
    """
    Authenticate a pembimbing dudi (industry supervisor) using JWT token.

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
        token = None
        if access_token:
            token = access_token
        elif Authorization:
            token = Authorization.split(" ")[1]
        
        # Check if a token is present
        if not token:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        print(token)
        # Decode and verify the JWT token
        pemimbingDudi = jwt.decode(token, SECRET_KEY, algorithms="HS256")

        # Check if pembimbing dudi information exists in the decoded token
        if not pemimbingDudi:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Create a select query to find the pembimbing dudi in the database
        selectQuery = select(PembimbingDudi.id, PembimbingDudi.username, PembimbingDudi.token_FCM, PembimbingDudi.id_sekolah,PembimbingDudi.id_dudi,PembimbingDudi.id_tahun).where(PembimbingDudi.id == pemimbingDudi["id"])
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
