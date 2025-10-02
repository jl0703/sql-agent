from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import transaction

app = FastAPI()

app.include_router(transaction.router)