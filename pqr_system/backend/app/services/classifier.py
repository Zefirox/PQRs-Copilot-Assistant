"""
Semantic Classification & Routing Service for PQRs.

Uses LLM (OpenAI) to classify PQRs into Petición, Queja, Reclamo or Sugerencia,
determine the competent area, calculate legal response terms per Colombian law,
and assign priority. Falls back to keyword-based classification when LLM is unavailable.
"""
import json
import logging
from typing import Optional

from openai import OpenAI

from app.config import settings
from app.models.pqr import (
    PQRType, PQRSubType, PQRPriority, ClassificationResult
)
from app.models.classification import (
    PQR_LEGAL_TERMS, AREA_KEYWORDS_MAPPING, PQR_TYPE_PATTERNS
)

logger = logging.getLogger(__name__)


class PQRClassifier:
    """Service for semantic classification and routing of PQRs."""

    def __init__(self):
        self.client = None
        self._init_openai()

    def _init_openai(self):
        """Initialize OpenAI-compatible client (Huawei Cloud MaaS) if API key is available."""
        try:
            if settings.openai_api_key and settings.openai_api_key != "sk-placeholder":
                self.client = OpenAI(
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_base_url,
                )
                logger.info(
                    f"LLM client initialized successfully "
                    f"(Classification: {settings.openai_classification_model}, "
                    f"General: {settings.openai_model}, "
                    f"Base URL: {settings.openai_base_url})"
                )
            else:
                logger.warning("API key not configured, using keyword-based fallback")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM client: {e}")

    async def classify(self, contenido: str, asunto: Optional[str] = None) -> ClassificationResult:
        """
        Classify a PQR using LLM with keyword-based fallback.
        
        Args:
            contenido: The free-text content of the PQR
            asunto: Optional subject/title
            
        Returns:
            ClassificationResult with type, area, legal terms, priority
        """
        full_text = f"{asunto or ''} {contenido}".strip()

        if self.client:
            try:
                result = await self._classify_with_llm(full_text)
                if result:
                    return result
            except Exception as e:
                logger.error(f"LLM classification failed, falling back to keywords: {e}")

        return self._classify_with_keywords(full_text)

    async def _classify_with_llm(self, text: str) -> Optional[ClassificationResult]:
        """Classify using OpenAI LLM."""
        prompt = f"""Eres un experto en derecho administrativo colombiano especializado en la clasificación de PQRs (Peticiones, Quejas, Reclamos y Sugerencias) según la Ley 1437 de 2011 (CPACA) y la Ley 1755 de 2015.

Analiza el siguiente texto de un PQR y clasifícalo respondiendo ÚNICAMENTE con un JSON válido:

TEXTO DEL PQR:
\"\"\"{text}\"\"\"

Responde con el siguiente formato JSON:
{{
    "pqr_type": "Petición|Queja|Reclamo|Sugerencia",
    "sub_type": "Petición de Información|Petición de Documentos|Petición de Consulta|Petición de Copia|Petición General|null",
    "confidence": 0.0-1.0,
    "assigned_area": "nombre del área competente",
    "priority": "Baja|Media|Alta|Urgente",
    "keywords": ["palabra1", "palabra2"],
    "summary": "resumen breve en una línea"
}}

REGLAS DE CLASIFICACIÓN:
1. PETICIÓN: Cuando el ciudadano solicita información, documentos, copias o hace una consulta.
   - "Petición de Información": solicita datos o información
   - "Petición de Documentos": solicita expedición de documentos
   - "Petición de Consulta": consulta sobre trámites o procedimientos
   - "Petición de Copia": solicita copias de documentos
   - "Petición General": cualquier otra petición
2. QUEJA: Expresión de insatisfacción sobre servicio, atención o funcionamiento.
3. RECLAMO: Cuando hay un perjuicio económico, cobro indebido, error en factura, o servicio no prestado.
4. SUGERENCIA: Propuesta de mejora, recomendación o idea.

REGLAS DE ENRUTAMIENTO:
- Asignar al área competente según el tema (Servicios Públicos, Tesorería, Jurídica, Obras Públicas, Medio Ambiente, Tránsito y Transporte, Salud, Educación, Hacienda, Contratación, Atención al Ciudadano, etc.)

REGLAS DE PRIORIDAD:
- "Urgente": Tutela, derechos fundamentales, salud, menores de edad
- "Alta": Servicios públicos esenciales, plazos próximos a vencer
- "Media": Casos regulares
- "Baja": Sugerencias, consultas generales"""

        response = self.client.chat.completions.create(
            model=settings.openai_classification_model,
            messages=[
                {"role": "system", "content": "Eres un clasificador experto de PQRs. Respondes ÚNICAMENTE con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500,
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)

        # Map to enums
        pqr_type = PQRType(data["pqr_type"])
        sub_type = None
        if data.get("sub_type") and data["sub_type"] != "null":
            try:
                sub_type = PQRSubType(data["sub_type"])
            except ValueError:
                sub_type = PQRSubType.PETICION_GENERAL

        # Get legal terms
        legal_key = data.get("sub_type") if pqr_type == PQRType.PETICION and data.get("sub_type") else data["pqr_type"]
        if legal_key and legal_key in PQR_LEGAL_TERMS:
            law = PQR_LEGAL_TERMS[legal_key]
        elif pqr_type.value in PQR_LEGAL_TERMS:
            law = PQR_LEGAL_TERMS[pqr_type.value]
        else:
            law = PQR_LEGAL_TERMS["Petición General"]

        return ClassificationResult(
            pqr_type=pqr_type,
            sub_type=sub_type,
            confidence=data.get("confidence", 0.8),
            assigned_area=data.get("assigned_area", "Atención al Ciudadano"),
            response_term_days=law.term_days,
            legal_basis=law.legal_basis,
            priority=PQRPriority(data.get("priority", "Media")),
            keywords=data.get("keywords", []),
            summary=data.get("summary"),
        )

    def _classify_with_keywords(self, text: str) -> ClassificationResult:
        """Fallback classification using keyword matching."""
        text_lower = text.lower()

        # Score each PQR type
        type_scores = {}
        for pqr_type, patterns in PQR_TYPE_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower)
            type_scores[pqr_type] = score

        # Determine best type
        max_score = max(type_scores.values()) if type_scores.values() else 0
        if max_score == 0:
            # Default to Petición General if no patterns match
            best_type = "Petición"
            confidence = 0.5
        else:
            best_type = max(type_scores, key=type_scores.get)
            total_matches = sum(type_scores.values())
            confidence = min(0.95, max_score / max(total_matches, 1) + 0.3)

        pqr_type = PQRType(best_type)

        # Determine sub-type for Peticiones
        sub_type = None
        if pqr_type == PQRType.PETICION:
            if any(w in text_lower for w in ["información", "saber", "conocer", "informe"]):
                sub_type = PQRSubType.INFORMACION
            elif any(w in text_lower for w in ["documento", "copias", "copia", "certificado"]):
                sub_type = PQRSubType.DOCUMENTOS
            elif any(w in text_lower for w in ["consulta", "consultar", "trámite", "procedimiento"]):
                sub_type = PQRSubType.CONSULTA
            else:
                sub_type = PQRSubType.GENERAL

        # Determine assigned area
        area_scores = {}
        for area, keywords in AREA_KEYWORDS_MAPPING.items():
            score = sum(1 for k in keywords if k in text_lower)
            if score > 0:
                area_scores[area] = score

        assigned_area = max(area_scores, key=area_scores.get) if area_scores else "Atención al Ciudadano"

        # Determine priority
        priority = PQRPriority.MEDIA
        if any(w in text_lower for w in ["tutela", "urgente", "salud", "menor", "vida"]):
            priority = PQRPriority.URGENTE
        elif any(w in text_lower for w in ["servicio público", "acueducto", "energía", "gas"]):
            priority = PQRPriority.ALTA
        elif pqr_type == PQRType.SUGERENCIA:
            priority = PQRPriority.BAJA

        # Get legal terms
        legal_key = sub_type.value if sub_type else pqr_type.value
        if legal_key in PQR_LEGAL_TERMS:
            law = PQR_LEGAL_TERMS[legal_key]
        elif pqr_type.value in PQR_LEGAL_TERMS:
            law = PQR_LEGAL_TERMS[pqr_type.value]
        else:
            law = PQR_LEGAL_TERMS["Petición General"]

        # Extract keywords
        keywords = []
        for area, kws in AREA_KEYWORDS_MAPPING.items():
            for kw in kws:
                if kw in text_lower and kw not in keywords:
                    keywords.append(kw)
                    if len(keywords) >= 5:
                        break
            if len(keywords) >= 5:
                break

        return ClassificationResult(
            pqr_type=pqr_type,
            sub_type=sub_type,
            confidence=confidence,
            assigned_area=assigned_area,
            response_term_days=law.term_days,
            legal_basis=law.legal_basis,
            priority=priority,
            keywords=keywords[:5],
            summary=None,
        )