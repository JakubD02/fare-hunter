from fastapi import FastAPI

from app.api.v1.endpoints.routers import alerts, auth, currency, featured, reference, routes, statistics
from app.core.config import Settings, settings
from app.core.logging import configure_logging
from app.core.rate_limit import setup_rate_limiting

configure_logging()


def create_app(config: Settings = settings) -> FastAPI:
    app = FastAPI(
        title="Fare hunter - flight tracker API",
        description="Backend API for automated flight price tracking and alerts.",
        version="0.1.0",
    )
    setup_rate_limiting(app)

    app.include_router(reference.router)
    app.include_router(currency.router)

    if config.DEMO_MODE:
        app.include_router(featured.router)
    else:
        app.include_router(auth.router)
        app.include_router(routes.router)
        app.include_router(statistics.router)
        app.include_router(alerts.router)

    @app.get("/", tags=["default"])
    def root():
        return {"service": "flight-tracker", "status": "ok"}

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    return app


app = create_app()
