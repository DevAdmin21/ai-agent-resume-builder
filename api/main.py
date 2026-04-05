import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.summarize import router as summarize_router
from application.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    logger.info("AI Summarizer service started | env=%s", settings.app_env)
    yield
    logger.info("AI Summarizer service shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="AI Text Summarizer",
        description="Summarize text and optionally generate PDF/DOCX documents using AI.",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ───────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request timing middleware ──────────────────────────────────────────
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Process-Time-Ms"] = str(elapsed)
        return response

    # ── Global exception handler ───────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."},
        )

    # ── Static file serving for generated documents ────────────────────────
    output_path = Path(settings.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(output_path)), name="static")

    @app.get("/files/{filename}", tags=["Files"], summary="Download generated document")
    async def download_file(filename: str):
        file_path = output_path / filename
        if not file_path.exists() or not file_path.is_file():
            return JSONResponse(status_code=404, content={"detail": "File not found."})
        # Security: ensure path stays within output_dir
        if not str(file_path.resolve()).startswith(str(output_path.resolve())):
            return JSONResponse(status_code=403, content={"detail": "Access denied."})
        return FileResponse(path=str(file_path), filename=filename)

    # ── Health check ───────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "service": "ai-summarizer"}

    # ── Routers ────────────────────────────────────────────────────────────
    app.include_router(summarize_router, prefix="/api/v1")

    return app