from fastapi import FastAPI
from backend.app.routers import fields
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - "
           "[%(levelname)s] - "
           "%(name)s - "
           "(%(filename)s).%(funcName)s(%(lineno)d) - "
           "%(message)s",
)

app = FastAPI()

app.include_router(fields.router)
