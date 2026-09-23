from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import engine

from app.models.base import Base
from app.routers import alerts, auth, reference, routes, statistics


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Fare hunter - flight tracker API",
    description="lorem ipsum",
    version="0.1.0",
)


app.include_router(auth.router)
app.include_router(reference.router)
app.include_router(routes.router)
app.include_router(statistics.router)
app.include_router(alerts.router)


@app.get("/", tags=["default"])
def root():
    return {"service": "flight-tracker", "status": "ok"}


@app.get("/health")
def health():
    return {"status", "healthy"}
