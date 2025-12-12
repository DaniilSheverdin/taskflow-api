from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.core.logger import setup_logger
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.LOGS_DIR.mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="TaskFlow-API",
    description="Async Task Manager with JWT and Roles",
    lifespan=lifespan,
)

setup_logger()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


routers = [auth]
for router in routers:
    app.include_router(router.router, prefix=settings.api_config.prefix, tags=["api"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
