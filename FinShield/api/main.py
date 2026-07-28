import time
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from loguru import logger

from .schemas import HealthResponse
from .dependencies import get_model_registry
from .routers import sms_check, upi_check, behavioral, voice_check, helplines

logger.add("logs/api.log", rotation="10 MB")
start_time = time.time()

def create_app() -> FastAPI:
    app = FastAPI(
        title="FinShield AI API",
        description="India's first multi-modal, privacy-preserving financial scam detection platform for rural India. (Hackathon Edition)",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Incoming request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": exc.body}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception occurred")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error due to model or system failure."}
        )

    @app.on_event("startup")
    async def startup_event():
        logger.info("Initializing FinShield AI Backend...")
        registry = get_model_registry()
        registry.load_all_models("models/")
        logger.info("Startup complete.")

    app.include_router(sms_check.router, prefix="/api/v1")
    app.include_router(upi_check.router, prefix="/api/v1")
    app.include_router(behavioral.router, prefix="/api/v1")
    app.include_router(voice_check.router, prefix="/api/v1")
    app.include_router(helplines.router, prefix="/api/v1")

    @app.get("/", tags=["System"])
    async def root():
        return {
            "name": "FinShield AI",
            "message": "Welcome to FinShield AI API",
            "docs_url": "/docs"
        }

    @app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
    async def health_check():
        registry = get_model_registry()
        uptime_seconds = int(time.time() - start_time)
        return HealthResponse(
            status="healthy",
            models_loaded=registry.is_loaded,
            version="1.0.0",
            uptime=f"{uptime_seconds} seconds"
        )

    return app

app = create_app()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
