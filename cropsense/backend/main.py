import logging
import time
from contextlib import asynccontextmanager

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from models.disease_model import DiseaseDetector
from models.yield_model import YieldPredictor
from routers import disease, yield_pred

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cropsense")

# Global model instances
disease_detector = DiseaseDetector()
yield_predictor = YieldPredictor()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models on startup, clean up on shutdown."""
    logger.info("CropSense API starting up - loading models...")
    disease_detector.load()
    yield_predictor.load()
    logger.info("All models loaded successfully.")
    yield
    logger.info("CropSense API shutting down.")


app = FastAPI(
    title="CropSense API",
    description=(
        "AI-powered crop disease detection and yield prediction API. "
        "Supports 41 disease classes across 15 crops with treatment recommendations, "
        "and stacking ensemble yield prediction with fertiliser guidance."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with timing for dashboard analytics."""
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)

    logger.info(
        "%s %s | Status: %d | Duration: %.2fms | Client: %s",
        request.method,
        request.url.path,
        response.status_code,
        duration,
        request.client.host if request.client else "unknown",
    )
    return response


# Include routers
app.include_router(disease.router, prefix="/api")
app.include_router(yield_pred.router, prefix="/api")

# Static files and SPA support
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR.parent / "frontend" / "dist"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR / "assets")), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs"):
            return None # Let FastAPI handles these
        
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/", tags=["Root"])
    def root():
        """Root endpoint with API information."""
        return {
            "name": "CropSense API",
            "version": "1.0.0",
            "description": "AI-powered crop disease detection and yield prediction",
            "docs": "/docs",
            "endpoints": {
                "health": "/health",
                "disease_predict": "/api/disease/predict",
                "disease_classes": "/api/disease/classes",
                "yield_predict": "/api/yield/predict",
                "yield_batch": "/api/yield/batch",
            },
        }


@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "models": {
            "disease": {
                "loaded": disease_detector.model is not None,
                "classes": len(disease_detector.class_names),
                "type": "MobileNetV2 CNN",
            },
            "yield": {
                "loaded": yield_predictor.model is not None,
                "type": "Stacking Ensemble (RF + GBM + XGB + Ridge)",
            },
        },
    }
