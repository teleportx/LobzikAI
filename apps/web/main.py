import sys

sys.path.append('..')

from contextlib import asynccontextmanager
import os.path

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.staticfiles import StaticFiles

from libs import db
import handlers
from libs import setup_logger
from libs import config


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
    db.base.start(config.db_url, config.debug, config.Constants.db_pool_max_size)

    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(DatabaseMiddleware)
app.include_router(handlers.router)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
