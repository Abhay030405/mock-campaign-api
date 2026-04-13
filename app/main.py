import logging
import logging.handlers
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database.db_manager import DatabaseManager
from app.routers import campaigns, customers

load_dotenv()

API_TITLE = os.getenv("API_TITLE", "Mock Campaign API")
API_VERSION = os.getenv("API_VERSION", "1.0.0")

# ------------------------------------------------------------------ #
# Logging configuration
# ------------------------------------------------------------------ #
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Console handler — INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
root_logger.addHandler(console_handler)

# File handler — DEBUG (rotating, 5 MB max, 3 backups)
log_dir = Path(__file__).resolve().parent.parent / ".logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "app.log"
file_handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=(
        "Mock Campaign Management API for CampaignX Hackathon — "
        "Simulates email campaign execution and returns gamified performance metrics"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------ #
# CORS
# ------------------------------------------------------------------ #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------ #
# Routers
# ------------------------------------------------------------------ #
app.include_router(customers.router, prefix="/api", tags=["customers"])
app.include_router(campaigns.router, prefix="/api", tags=["campaigns"])

# ------------------------------------------------------------------ #
# Startup
# ------------------------------------------------------------------ #


@app.on_event("startup")
def startup() -> None:
    db_manager = DatabaseManager()
    db_manager.initialize_json_files()
    count = len(db_manager.load_customers())
    logger.info("Mock Campaign API started successfully")
    logger.info("Loaded %d customers", count)


# ------------------------------------------------------------------ #
# Root & health
# ------------------------------------------------------------------ #


@app.get("/", tags=["root"])
def root() -> dict:
    return {"message": "Mock Campaign API", "docs": "/docs"}


@app.get("/health", tags=["root"])
def health() -> dict:
    db_manager = DatabaseManager()
    count = len(db_manager.load_customers())
    return {"status": "healthy", "customers_loaded": count, "version": API_VERSION}


# ------------------------------------------------------------------ #
# Exception handlers
# ------------------------------------------------------------------ #


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    logger.error("HTTPException %d: %s", exc.status_code, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ------------------------------------------------------------------ #
# Entrypoint
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
