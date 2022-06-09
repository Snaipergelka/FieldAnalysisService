import logging

import uvicorn
from fastapi import FastAPI

from backend.app.database.database_config import init_tables
from backend.app.routers import fields

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


@app.on_event("startup")
def startup_event():
    """
    Creating tables before FatAPI apps start.
    :return:
    """
    init_tables()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
