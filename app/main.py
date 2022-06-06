import os

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware


def create_app() -> FastAPI:
    application = FastAPI(docs_url='/swagger/',
                          redoc_url='/redoc/',
                          openapi_url='/openapi.json',
                          title="RockPaperScissors")
    application.add_middleware(
        DBSessionMiddleware, db_url=os.getenv("DB_URL", "sqlite:///sqlite.db"))
    from app.api import router
    application.include_router(router)
    return application
