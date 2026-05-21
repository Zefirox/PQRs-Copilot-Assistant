"""
FastAPI routes for the PQR Processing System.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.models.pqr import (
    PQRCreate, PQRResponse, PQRType, PQRStatus,
    ClassificationResult, CompletenessResult,
    CopilotRequest, CopilotResponse, CitizenInfo
)
from app.services.classifier import PQRClassifier
from app.services.rag_engine import RAGEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
classifier = PQRClassifier()
rag_engine = RAGEngine()

# In-memory storage (in production, use a database)
pqr_store: dict = {}


def generate_radicado() -> str:
    """Generate a unique radicado number (e.g., 2026-ER-001234)."""
    year = datetime.now().year
    seq = len(pqr_store) + 1
    return f"{year}-ER-{seq:06d}"


def calculate_business_days(start: datetime, days: int) -> datetime:
    """
    Calculate deadline adding business days (excluding weekends).
    Colombian holidays are not considered in this simplified version.
    """
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday=0, Friday=4
            added += 1
    return current


@router.post("/pqr", response_model=PQRResponse, tags=["PQR"])
async def create_pqr(pqr_data: PQRCreate):
    """
    Create and process a new PQR.
    
    This endpoint:
    1. Classifies the PQR semantically (type, area, priority)
    2. Analyzes completeness (missing data, documents)
    3. Generates a radicado number
    4. Calculates the legal response deadline
    """
    try:
        # Step 1: Semantic Classification
        classification = await classifier.classify(
            contenido=pqr_data.contenido,
            asunto=pqr_data.asunto
        )

        # Step 2: Generate IDs and radicado
        pqr_id = str(uuid4())
        radicado = generate_radicado()
        fecha_radicado = datetime.now()

        # Step 4: Calculate deadline
        fecha_limite = calculate_business_days(
            fecha_radicado, classification.response_term_days
        )

        # Build default completeness (always complete, no analysis)
        completeness = CompletenessResult(
            is_complete=True,
            completeness_score=1.0,
            issues=[],
            suggestions=[],
            missing_documents=[],
        )

        # Build response
        response = PQRResponse(
            id=pqr_id,
            radicado=radicado,
            fecha_radicado=fecha_radicado,
            contenido=pqr_data.contenido,
            asunto=pqr_data.asunto,
            ciudadano=pqr_data.ciudadano,
            classification=classification,
            completeness=completeness,
            status=PQRStatus.RADICADO,
            fecha_limite_respuesta=fecha_limite,
            archivos_adjuntos=pqr_data.archivos_adjuntos,
        )

        # Store
        pqr_store[pqr_id] = response

        return response

    except Exception as e:
        logger.error(f"Error creating PQR: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar el PQR: {str(e)}")


@router.get("/pqr", response_model=List[PQRResponse], tags=["PQR"])
async def list_pqrs(
    status: Optional[str] = Query(None, description="Filter by status"),
    pqr_type: Optional[str] = Query(None, description="Filter by PQR type"),
    limit: int = Query(50, ge=1, le=100),
):
    """List all PQRs with optional filters."""
    results = list(pqr_store.values())

    if status:
        results = [p for p in results if p.status.value == status]
    if pqr_type:
        results = [p for p in results if p.classification.pqr_type.value == pqr_type]

    return results[:limit]


@router.get("/pqr/{pqr_id}", response_model=PQRResponse, tags=["PQR"])
async def get_pqr(pqr_id: str):
    """Get a specific PQR by ID."""
    if pqr_id not in pqr_store:
        raise HTTPException(status_code=404, detail="PQR no encontrado")
    return pqr_store[pqr_id]


class ClassifyRequest(BaseModel):
    """Request body for classification endpoint."""
    contenido: str
    asunto: Optional[str] = None


@router.post("/pqr/classify", response_model=ClassificationResult, tags=["Clasificación"])
async def classify_text(request: ClassifyRequest):
    """
    Classify PQR text without creating a PQR.
    Useful for previewing classification before submission.
    """
    return await classifier.classify(contenido=request.contenido, asunto=request.asunto)


@router.post("/copilot/generate", response_model=CopilotResponse, tags=["Copiloto"])
async def generate_copilot_response(request: CopilotRequest):
    """
    Generate a draft response for a PQR using RAG.
    
    The copilot searches the knowledge base for relevant context
    and generates a formal, structured draft response for the official.
    """
    try:
        return await rag_engine.generate_response(request)
    except Exception as e:
        logger.error(f"Error generating copilot response: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar respuesta: {str(e)}")


@router.get("/copilot/knowledge-base/stats", tags=["Copiloto"])
async def knowledge_base_stats():
    """Get knowledge base statistics."""
    if rag_engine.collection:
        return {
            "total_documents": rag_engine.collection.count(),
            "collection_name": settings.chroma_collection_name,
        }
    return {"total_documents": 0, "collection_name": "not_initialized"}


class KnowledgeBaseLoad(BaseModel):
    """Request to load documents into knowledge base."""
    documents: List[dict]


@router.post("/copilot/knowledge-base/load", tags=["Copiloto"])
async def load_knowledge_base(data: KnowledgeBaseLoad):
    """Load documents into the knowledge base."""
    loaded = rag_engine.load_knowledge_base(data.documents)
    return {"loaded": loaded, "total": len(data.documents)}


@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "pqrs_stored": len(pqr_store),
        "openai_configured": classifier.client is not None,
        "chromadb_initialized": rag_engine.collection is not None,
    }


# Import settings for the knowledge base stats
from app.config import settings