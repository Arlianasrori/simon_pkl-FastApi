# Import required modules
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import CronTrigger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("/.env")

# Import models from src module
from src.models import *

# Import error handling function
from src.error.errorHandling import add_exception_server

# Import routers
from src.routes.authRouter import authRouter
from src.routes.developerRouter import developerRouter
from src.routes.adminRouter import adminRouter
from src.routes.pembimbingDudiRouter import pembimbingDudiRouter
from src.routes.guruPembimbingRouter import guruPembimbingRouter
from src.routes.siswaRouter import siswaRouter
from src.cron_job.addAbsenSiswaCron import addAbsenSiswaCron

# Initialize FastAPI application with configuration
App = FastAPI(
    title="API SPEC FOR SIMON PKL",
    description="This is the API specification for simon pkl, it can be your guide in consuming the API. Please pay attention to the required fields in this API specification",
    servers=[{"url": "http://localhost:2008", "description": "development server"}],
    contact={"name": "Habil Arlian Asrori", "email": "arlianasrori@gmail.com"}
)

# Add routers to the application
routes = [authRouter, developerRouter, adminRouter,pembimbingDudiRouter,guruPembimbingRouter,siswaRouter]
for router in routes:
    App.include_router(router)

# add middleware
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

# Mount static directory for public files
App.mount("/public", StaticFiles(directory="src/public"), name="public")

# Configure CORS middleware
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

# Add error handling to the application
add_exception_server(App)

# Inisialisasi scheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(addAbsenSiswaCron, CronTrigger(hour=0, minute=0))

# Function to run the server
async def runServer():
    scheduler.start()
    config = uvicorn.Config("main:App", port=2008, reload=True)  # Matikan mode reload
    server = uvicorn.Server(config)
    await server.serve()
# Run the server if the script is executed directly
if __name__ == "__main__":
    asyncio.run(runServer())