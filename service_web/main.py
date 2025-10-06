import sys

from starlette.staticfiles import StaticFiles

sys.path.append('.')
sys.path.append('service_web')

from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

import db
import handlers
import setup_logger


setup_logger.__init__('Service web')


class DatabaseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        async with db.base.Session() as session:
            request.state.db = session
            response = await call_next(request)
            await session.commit()

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.base.start()

    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(DatabaseMiddleware)
app.include_router(handlers.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
