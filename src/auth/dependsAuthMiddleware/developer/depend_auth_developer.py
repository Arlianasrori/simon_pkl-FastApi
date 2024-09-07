# Import necessary modules
from fastapi import Cookie, Request
from ....models.developerModel import Developer
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

# Get the secret key from environment variables
SECRET_KEY = os.getenv("DEVELOPER_SECRET_ACCESS_TOKEN")

async def developerAuth(access_token : str | None = Cookie(None), req : Request = None, Session : sessionDepedency = None):
    """
    Authenticate a developer using JWT token.

    Args:
        access_token (str | None): The JWT token from cookies.
        req (Request): The FastAPI request object.
        Session (sessionDepedency): The database session dependency.

    Raises:
        HttpException: If authentication fails.

    Returns:
        None
    """
    print(access_token)
    # Check if access token exists
    if not access_token:
        raise HttpException(status=401, message="invalid token(unauthorized)")
    try:
        # Decode the JWT token
        developer = jwt.decode(access_token, SECRET_KEY, algorithms="HS256")

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
