import sys

sys.path.append('.')
sys.path.append('service_web')

from contextlib import asynccontextmanager

import db

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.base.start()

    yield


app = FastAPI(lifespan=lifespan)


