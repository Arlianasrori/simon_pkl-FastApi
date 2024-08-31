import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
load_dotenv("/.env")
from src.db.db import Base,engine
from src.models import *

App = FastAPI(title="API SPEC FOR SIMON PKL",description="This is the api spec for simon pkl, it can be your guide in consuming the api. Please pay attention to the required fields in the api spec ini",servers=[{"url": "http://localhost:2008","description" : "development server"}],contact={"name" : "Habil Arlian Asrori","email" : "arlianasrori@gmail.com"})

origins = [
    "http://localhost:2008",
]

App.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def runServer() :
    uvicorn.run(app="main:App",port=2008,reload=True)


if __name__ == "__main__" :
    asyncio.run(runServer())