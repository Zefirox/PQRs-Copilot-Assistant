"""
PQR Data Models - Core domain models for the PQR processing system.
Based on Colombian regulations (Ley 1437 de 2011 - CPACA).
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PQRType(str, Enum):
    """Tipos de PQR según la normativa colombiana."""
    PETICION = "Petición"
    QUEJA = "Queja"
    RECLAMO = "Reclamo"
    SUGERENCIA = "Sugerencia"


class PQRSubType(str, Enum):
    """Subtipos de Petición según el CPACA."""
    INFORMACION = "Petición de Información"
    DOCUMENTOS = "Petición de Documentos"
    CONSULTA = "Petición de Consulta"
    COPIA = "Petición de Copia"
    GENERAL = "Petición General"


class PQRPriority(str, Enum):
    """Niveles de prioridad del PQR."""
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    URGENTE = "Urgente"


class PQRStatus(str, Enum):
    """Estados del PQR en el ciclo de vida."""
    RADICADO = "Radicado"
    EN_REVISION = "En Revisión"
    ASIGNADO = "Asignado"
    EN_PROCESO = "En Proceso"
    RESPONDIDO = "Respondido"
    CERRADO = "Cerrado"
    REABIERTO = "Reabierto"


class CitizenInfo(BaseModel):
    """Información del ciudadano que radica el PQR."""
    nombre_completo: Optional[str] = Field(
        None, description="Nombre completo del ciudadano"
    )
    tipo_documento: Optional[str] = Field(
        None, description="Tipo de documento (CC, CE, TI, NIT, PP)"
    )
    numero_documento: Optional[str] = Field(
        None, description="Número de documento de identidad"
    )
    email: Optional[str] = Field(None, description="Correo electrónico")
    telefono: Optional[str] = Field(None, description="Teléfono de contacto")
    direccion: Optional[str] = Field(
        None, description="Dirección de notificación"
    )
    municipio: Optional[str] = Field(None, description="Municipio/CIudad")
    departamento: Optional[str] = Field(None, description="Departamento")


class CompletenessIssue(BaseModel):
    """Problema de completitud detectado en el PQR."""
    field_name: str = Field(description="Campo faltante")
    description: str = Field(description="Descripción del dato faltante")
    severity: str = Field(description="Severidad: critica, advertencia, sugerencia")
    suggestion: str = Field(description="Sugerencia para el ciudadano")
    is_blocking: bool = Field(
        default=False, description="Si bloquea la radicación"
    )


class CompletenessResult(BaseModel):
    """Resultado del análisis de completitud."""
    is_complete: bool = Field(description="Si el PQR está completo")
    completeness_score: float = Field(
        ge=0, le=1, description="Puntuación de completitud (0-1)"
    )
    issues: List[CompletenessIssue] = Field(
        default_factory=list, description="Problemas detectados"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Sugerencias amigables para el ciudadano"
    )
    missing_documents: List[str] = Field(
        default_factory=list, description="Documentos faltantes detectados"
    )


class ClassificationResult(BaseModel):
    """Resultado de la clasificación semántica."""
    pqr_type: PQRType = Field(description="Tipo de PQR clasificado")
    sub_type: Optional[PQRSubType] = Field(
        None, description="Subtipo (aplica solo para Peticiones)"
    )
    confidence: float = Field(
        ge=0, le=1, description="Confianza de la clasificación"
    )
    assigned_area: str = Field(description="Área competente asignada")
    response_term_days: int = Field(
        description="Término de respuesta en días hábiles"
    )
    legal_basis: str = Field(
        description="Base legal del término de respuesta"
    )
    priority: PQRPriority = Field(
        default=PQRPriority.MEDIA, description="Prioridad asignada"
    )
    keywords: List[str] = Field(
        default_factory=list, description="Palabras clave identificadas"
    )
    summary: Optional[str] = Field(
        None, description="Resumen del contenido del PQR"
    )


class PQRCreate(BaseModel):
    """Modelo para la creación de un nuevo PQR."""
    contenido: str = Field(
        ..., min_length=10, description="Contenido textual del PQR"
    )
    asunto: Optional[str] = Field(None, description="Asunto o título")
    ciudadano: CitizenInfo = Field(
        default_factory=CitizenInfo, description="Información del ciudadano"
    )
    archivos_adjuntos: List[str] = Field(
        default_factory=list, description="Nombres de archivos adjuntos"
    )
    canal_recepcion: str = Field(
        default="Web", description="Canal de recepción (Web, Presencial, Teléfonico, Email)"
    )


class PQRResponse(BaseModel):
    """Modelo de respuesta del PQR procesado."""
    id: str = Field(description="Identificador único del PQR")
    radicado: str = Field(description="Número de radicado")
    fecha_radicado: datetime = Field(description="Fecha de radicación")
    contenido: str = Field(description="Contenido del PQR")
    asunto: Optional[str] = Field(None, description="Asunto")
    ciudadano: CitizenInfo = Field(description="Información del ciudadano")
    classification: ClassificationResult = Field(
        description="Resultado de la clasificación"
    )
    completeness: CompletenessResult = Field(
        description="Resultado del análisis de completitud"
    )
    status: PQRStatus = Field(
        default=PQRStatus.RADICADO, description="Estado actual"
    )
    fecha_limite_respuesta: Optional[datetime] = Field(
        None, description="Fecha límite de respuesta"
    )
    archivos_adjuntos: List[str] = Field(default_factory=list)


class CopilotRequest(BaseModel):
    """Solicitud del copiloto de respuestas."""
    pqr_id: str = Field(description="ID del PQR a responder")
    pqr_contenido: str = Field(description="Contenido del PQR")
    pqr_type: PQRType = Field(description="Tipo del PQR")
    funcionario_notas: Optional[str] = Field(
        None, description="Notas adicionales del funcionario"
    )
    tono: str = Field(
        default="formal", description="Tono de la respuesta (formal, amable, directo)"
    )


class CopilotResponse(BaseModel):
    """Respuesta generada por el copiloto."""
    borrador_respuesta: str = Field(
        description="Borrador de respuesta generado"
    )
    fuentes_utilizadas: List[str] = Field(
        default_factory=list, description="Fuentes/normas utilizadas"
    )
    sugerencias_adicionales: List[str] = Field(
        default_factory=list, description="Sugerencias adicionales para el funcionario"
    )
    confidence_score: float = Field(
        ge=0, le=1, description="Confianza en la respuesta generada"
    )
    requires_review: bool = Field(
        default=True, description="Si requiere revisión adicional"
    )