"""FastAPI application factory."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.routes import router
from .config import Settings
from .services.provisioner import ResourceService
from .services.terraform import TerraformRunner
from .store import ResourceStore

STATIC_DIR = Path(__file__).parent / "static"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Cloud infrastructure automation API.",
    )

    store = ResourceStore(max_resources=settings.max_resources)
    app.state.settings = settings
    app.state.store = store
    app.state.service = ResourceService(store=store, runner=TerraformRunner(settings))

    app.include_router(router)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def dashboard() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    return app


app = create_app()
