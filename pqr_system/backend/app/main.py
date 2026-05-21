"""
PQR Processing System - Main FastAPI Application.

AI-powered system for processing PQRs (Peticiones, Quejas, Reclamos, Sugerencias)
with semantic classification, completeness analysis, and RAG-based copilot.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import settings
from app.routes import router, rag_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events."""
    logger.info(f"Starting {settings.app_name}...")
    
    # Load default knowledge base
    try:
        from app.data.knowledge_base import DEFAULT_KNOWLEDGE_BASE
        loaded = rag_engine.load_knowledge_base(DEFAULT_KNOWLEDGE_BASE)
        logger.info(f"Loaded {loaded} documents into knowledge base")
    except Exception as e:
        logger.warning(f"Could not load default knowledge base: {e}")
    
    yield
    
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="""
    ## Sistema de Procesamiento de PQRs con IA
    
    Sistema inteligente para el procesamiento de Peticiones, Quejas, Reclamos y Sugerencias (PQRs)
    en entidades públicas colombianas, basado en la Ley 1437 de 2011 (CPACA).
    
    ### Funcionalidades principales:
    
    1. **Clasificación y Enrutamiento Semántico**: Clasificación automática del PQR
       usando IA, con cálculo de términos legales según normativa colombiana.
    
    2. **Análisis de Completitud**: Validación en tiempo real que detecta datos
       faltantes y sugiere al ciudadano completarlos antes de radicar.
    
    3. **Copiloto de Respuestas (RAG)**: Generación de borradores de respuesta
       para funcionarios usando la base de conocimientos de la entidad.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the frontend application."""
    frontend_index = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {"message": f"Welcome to {settings.app_name} API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )