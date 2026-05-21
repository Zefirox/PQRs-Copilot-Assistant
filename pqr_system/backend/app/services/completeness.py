# -*- coding: utf-8 -*-
"""
Completeness Analysis Service for PQRs.

Evaluates PQR content at filing time to detect missing mandatory data
(cedula, address, supporting documents, etc.) and provides friendly
suggestions to the citizen before finalizing the filing.
"""
import json
import logging
import re
from typing import Optional, List

from openai import OpenAI

from app.config import settings
from app.models.pqr import (
    CitizenInfo, CompletenessIssue, CompletenessResult, PQRType
)

logger = logging.getLogger(__name__)


class CompletenessAnalyzer:
    """Service for analyzing PQR completeness at filing time."""

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
                logger.info(f"LLM client initialized for completeness analysis (model: {settings.openai_model})")
            else:
                logger.warning("API key not configured, using rule-based completeness check")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM client: {e}")

    async def analyze(
        self,
        contenido: str,
        ciudadano: CitizenInfo,
        archivos_adjuntos: List[str],
        pqr_type: Optional[PQRType] = None
    ) -> CompletenessResult:
        """
        Analyze the completeness of a PQR at filing time.
        """
        if self.client:
            try:
                result = await self._analyze_with_llm(
                    contenido, ciudadano, archivos_adjuntos, pqr_type
                )
                if result:
                    return result
            except Exception as e:
                logger.error(f"LLM completeness analysis failed, using rules: {e}")

        return self._analyze_with_rules(contenido, ciudadano, archivos_adjuntos, pqr_type)

    async def _analyze_with_llm(
        self,
        contenido: str,
        ciudadano: CitizenInfo,
        archivos_adjuntos: List[str],
        pqr_type: Optional[PQRType]
    ) -> Optional[CompletenessResult]:
        """Analyze completeness using LLM."""
        citizen_data = ciudadano.model_dump()
        adjuntos_str = ", ".join(archivos_adjuntos) if archivos_adjuntos else "Ninguno"

        prompt = (
            "Eres un analista experto en radicacion de PQRs en entidades publicas colombianas. "
            "Tu trabajo es verificar que el PQR tenga toda la informacion necesaria para ser procesado.\n\n"
            f"CONTENIDO DEL PQR:\n{contenido}\n\n"
            f"DATOS DEL CIUDADANO:\n"
            f"- Nombre: {citizen_data.get('nombre_completo', 'No proporcionado')}\n"
            f"- Tipo documento: {citizen_data.get('tipo_documento', 'No proporcionado')}\n"
            f"- Numero documento: {citizen_data.get('numero_documento', 'No proporcionado')}\n"
            f"- Email: {citizen_data.get('email', 'No proporcionado')}\n"
            f"- Telefono: {citizen_data.get('telefono', 'No proporcionado')}\n"
            f"- Direccion: {citizen_data.get('direccion', 'No proporcionado')}\n"
            f"- Municipio: {citizen_data.get('municipio', 'No proporcionado')}\n"
            f"- Departamento: {citizen_data.get('departamento', 'No proporcionado')}\n\n"
            f"ARCHIVOS ADJUNTOS: {adjuntos_str}\n"
            f"TIPO PQR: {pqr_type.value if pqr_type else 'No clasificado aun'}\n\n"
            "Analiza y responde UNICAMENTE con JSON:\n"
            '{"is_complete": true/false, "completeness_score": 0.0-1.0, '
            '"issues": [{"field_name": "...", "description": "...", '
            '"severity": "critica|advertencia|sugerencia", "suggestion": "...", "is_blocking": true/false}], '
            '"suggestions": ["..."], "missing_documents": ["..."]}\n\n'
            "REGLAS:\n"
            "1. Es CRITICO que exista numero de cedula/documento de identidad\n"
            "2. Es CRITICO que exista direccion de notificacion o email\n"
            "3. Es CRITICO que el nombre del ciudadano este presente\n"
            "4. Si el PQR menciona una factura, recibo, contrato o documento especifico, verificar que este adjunto\n"
            "5. Para QUEJAS/RECLAMOS: es importante adjuntar soportes\n"
            "6. La direccion de notificacion es obligatoria segun el CPACA\n"
            "7. Las sugerencias deben ser amigables y orientadoras, no burocraticas"
        )

        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Eres un analista de completitud de PQRs. Respondes UNICAMENTE con JSON valido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=800,
        )

        content = response.choices[0].message.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)

        issues = [
            CompletenessIssue(
                field_name=i["field_name"],
                description=i["description"],
                severity=i["severity"],
                suggestion=i["suggestion"],
                is_blocking=i.get("is_blocking", False)
            )
            for i in data.get("issues", [])
        ]

        return CompletenessResult(
            is_complete=data.get("is_complete", len(issues) == 0),
            completeness_score=data.get("completeness_score", 1.0),
            issues=issues,
            suggestions=data.get("suggestions", []),
            missing_documents=data.get("missing_documents", []),
        )

    def _analyze_with_rules(
        self,
        contenido: str,
        ciudadano: CitizenInfo,
        archivos_adjuntos: List[str],
        pqr_type: Optional[PQRType]
    ) -> CompletenessResult:
        """Rule-based completeness analysis (fallback)."""
        issues: List[CompletenessIssue] = []
        suggestions: List[str] = []
        missing_docs: List[str] = []
        score = 1.0

        # Check citizen identification
        if not ciudadano.numero_documento:
            issues.append(CompletenessIssue(
                field_name="numero_documento",
                description="Numero de documento de identidad faltante",
                severity="critica",
                suggestion="Para radicar su PQR, necesitamos su numero de documento de identidad (cedula, NIT, etc.).",
                is_blocking=True
            ))
            score -= 0.2

        if not ciudadano.nombre_completo:
            issues.append(CompletenessIssue(
                field_name="nombre_completo",
                description="Nombre completo del ciudadano faltante",
                severity="critica",
                suggestion="Por favor ingrese su nombre completo para continuar con la radicacion.",
                is_blocking=True
            ))
            score -= 0.15

        # Check notification address
        if not ciudadano.direccion and not ciudadano.email:
            issues.append(CompletenessIssue(
                field_name="direccion_notificacion",
                description="No hay direccion de notificacion ni correo electronico",
                severity="critica",
                suggestion="Para enviarle la respuesta a su PQR, necesitamos su direccion de notificacion o correo electronico.",
                is_blocking=True
            ))
            score -= 0.15
        elif not ciudadano.direccion:
            issues.append(CompletenessIssue(
                field_name="direccion",
                description="Direccion de notificacion faltante (solo tiene email)",
                severity="advertencia",
                suggestion="Desea agregar una direccion fisica de notificacion? Esto puede agilizar el proceso.",
                is_blocking=False
            ))
            score -= 0.05

        # Check contact info
        if not ciudadano.email and not ciudadano.telefono:
            issues.append(CompletenessIssue(
                field_name="contacto",
                description="No hay medio de contacto (email ni telefono)",
                severity="advertencia",
                suggestion="Proporcione al menos un correo electronico o telefono para que podamos contactarlo.",
                is_blocking=False
            ))
            score -= 0.1

        # Check for referenced documents in content
        contenido_lower = contenido.lower()

        doc_references = {
            "factura": ["factura", "recibo", "cobro"],
            "contrato": ["contrato", "convenio"],
            "resolucion": ["resolucion", "auto"],
            "historia clinica": ["historia clinica", "historia medica"],
            "soporte de pago": ["comprobante", "soporte", "pago", "consignacion"],
        }

        for doc_name, patterns in doc_references.items():
            if any(p in contenido_lower for p in patterns):
                has_attachment = any(
                    doc_name.split()[0] in adj.lower()
                    for adj in archivos_adjuntos
                )
                if not has_attachment and not archivos_adjuntos:
                    missing_docs.append(doc_name)
                    issues.append(CompletenessIssue(
                        field_name=f"adjunto_{doc_name.replace(' ', '_')}",
                        description=f"Se menciona {doc_name} pero no se adjunto soporte",
                        severity="advertencia",
                        suggestion=f"Detectamos que menciona una {doc_name} pero no la ha adjuntado. Desea incluirla para agilizar su tramite?",
                        is_blocking=False
                    ))
                    score -= 0.05

        # For Quejas and Reclamos, attachments are more important
        if pqr_type in [PQRType.QUEJA, PQRType.RECLAMO] and not archivos_adjuntos:
            suggestions.append(
                "Para quejas y reclamos, adjuntar soportes ayuda a resolver su caso mas rapidamente."
            )

        # Generate friendly suggestions from issues
        for issue in issues:
            if issue.suggestion and issue.suggestion not in suggestions:
                suggestions.append(issue.suggestion)

        # Clamp score
        score = max(0.0, min(1.0, score))

        return CompletenessResult(
            is_complete=len([i for i in issues if i.is_blocking]) == 0,
            completeness_score=round(score, 2),
            issues=issues,
            suggestions=suggestions,
            missing_documents=missing_docs,
        )