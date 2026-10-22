from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.endpoints.routers import alerts, auth, currency, reference, routes, statistics
from app.core.database import engine
from app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield
    engine.dispose()


app = FastAPI(
    title="Fare hunter - flight tracker API",
    description="Backend API for automated flight price tracking and alerts.",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(auth.router)
app.include_router(reference.router)
app.include_router(routes.router)
app.include_router(statistics.router)
app.include_router(alerts.router)
app.include_router(currency.router)


@app.get("/", tags=["default"])
def root():
    return {"service": "flight-tracker", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
