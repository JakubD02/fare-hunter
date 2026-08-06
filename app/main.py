from fastapi import FastAPI

app = FastAPI(
    title="Fare hunter - flight tracker API",
    description="lorem ipsum",
    version="0.1.0",
)


@app.get("/", tags=["default"])
def root():
    return {"service": "flight-tracker", "status": "ok"}
