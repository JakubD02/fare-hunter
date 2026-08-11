from fastapi import FastAPI

from app.routers import auth

app = FastAPI(
    title="Fare hunter - flight tracker API",
    description="lorem ipsum",
    version="0.1.0",
)


app.include_router(auth.router)


@app.get("/", tags=["default"])
def root():
    return {"service": "flight-tracker", "status": "ok"}


@app.get("/health")
def health():
    return {"status", "healthy"}
