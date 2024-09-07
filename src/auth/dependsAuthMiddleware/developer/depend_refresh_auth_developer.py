# Import necessary modules
from fastapi import Cookie, Request
from ....models.developerModel import Developer
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

# Get the secret key for refresh token from environment variables
SECRET_KEY = os.getenv("DEVELOPER_SECRET_REFRESH_TOKEN")

async def developerRefreshAuth(refresh_token: str | None = Cookie(None), req: Request = None, Session: sessionDepedency = None):
    """
    Authenticate a developer using refresh token.

    Args:
        refresh_token (str | None): The JWT refresh token from cookies.
        req (Request): The FastAPI request object.
        Session (sessionDepedency): The database session dependency.

    Raises:
        HttpException: If authentication fails.

    Returns:
        None
    """
    print(refresh_token)
    # Check if refresh token exists
    if not refresh_token:
        raise HttpException(status=401, message="invalid token(unauthorized)")
    try:
        # Decode the JWT refresh token
        developer = jwt.decode(refresh_token, SECRET_KEY, algorithms="HS256")

        # Check if developer information exists in the decoded token
        if not developer:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Create a select query to find the developer in the database
        selectQuery = select(Developer.id, Developer.username).where(Developer.id == developer["id"])
        exec = await Session.execute(selectQuery)
        findeDeveloper = exec.first()

        # Check if the developer exists in the database
        if not findeDeveloper: 
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Add developer information to the request object
        req.developer = findeDeveloper._asdict()
    except JWTError as error:
        # Handle JWT decoding errors
        raise HttpException(status=401, message=str(error.args[0])) 
