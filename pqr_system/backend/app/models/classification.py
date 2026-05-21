"""
Classification models and Colombian legal definitions for PQR processing.
Based on Ley 1437 de 2011 (CPACA) and Ley 1755 de 2015.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class AreaCompetente(str, Enum):
    """Áreas funcionales típicas de una entidad pública colombiana."""
    ATENCION_CIUDADANO = "Atención al Ciudadano"
    SERVICIOS_PUBLICOS = "Servicios Públicos"
    TESORERIA = "Tesorería"
    RECURSOS_HUMANOS = "Recursos Humanos"
    JURIDICA = "Jurídica"
    PLANEACION = "Planeación"
    OBRAS_PUBLICAS = "Obras Públicas"
    MEDIO_AMBIENTE = "Medio Ambiente"
    EDUCACION = "Educación"
    SALUD = "Salud"
    TRANSITO = "Tránsito y Transporte"
    HACIENDA = "Hacienda"
    TIC = "Tecnologías de la Información"
    CONTROL_INTERNO = "Control Interno"
    CONTRATACION = "Contratación"


class ColombianPQRLaw(BaseModel):
    """
    Términos legales de respuesta según la normativa colombiana.
    
    Referencias:
    - Ley 1437 de 2011 (CPACA)
    - Ley 1755 de 2015 (Ley de Transparencia)
    - Ley 850 de 2003 (Estatuto del Consumidor)
    """
    pqr_type: str
    sub_type: Optional[str] = None
    term_days: int = Field(description="Término en días hábiles")
    legal_basis: str = Field(description="Base legal")
    description: str = Field(description="Descripción del término")


# Términos de respuesta según la normativa colombiana
PQR_LEGAL_TERMS: Dict[str, ColombianPQRLaw] = {
    "Petición de Información": ColombianPQRLaw(
        pqr_type="Petición",
        sub_type="Información",
        term_days=10,
        legal_basis="Art. 21 Ley 1437/2011 (CPACA)",
        description="10 días hábiles para entregar la información solicitada"
    ),
    "Petición de Documentos": ColombianPQRLaw(
        pqr_type="Petición",
        sub_type="Documentos",
        term_days=10,
        legal_basis="Art. 21 Ley 1437/2011 (CPACA)",
        description="10 días hábiles para expedir copias o documentos"
    ),
    "Petición de Consulta": ColombianPQRLaw(
        pqr_type="Petición",
        sub_type="Consulta",
        term_days=30,
        legal_basis="Art. 21 Ley 1437/2011 (CPACA)",
        description="30 días hábiles para resolver consultas de gran complejidad"
    ),
    "Petición de Copia": ColombianPQRLaw(
        pqr_type="Petición",
        sub_type="Copia",
        term_days=10,
        legal_basis="Art. 21 Ley 1437/2011 (CPACA)",
        description="10 días hábiles para expedir copias"
    ),
    "Petición General": ColombianPQRLaw(
        pqr_type="Petición",
        sub_type="General",
        term_days=15,
        legal_basis="Art. 14 Ley 1437/2011 (CPACA)",
        description="15 días hábiles para responder peticiones generales"
    ),
    "Queja": ColombianPQRLaw(
        pqr_type="Queja",
        sub_type=None,
        term_days=15,
        legal_basis="Art. 14 Ley 1437/2011 (CPACA)",
        description="15 días hábiles para dar respuesta a la queja"
    ),
    "Reclamo": ColombianPQRLaw(
        pqr_type="Reclamo",
        sub_type=None,
        term_days=15,
        legal_basis="Art. 14 Ley 1437/2011 (CPACA)",
        description="15 días hábiles para resolver el reclamo"
    ),
    "Sugerencia": ColombianPQRLaw(
        pqr_type="Sugerencia",
        sub_type=None,
        term_days=30,
        legal_basis="Buena práctica / Art. 14 Ley 1437/2011",
        description="30 días calendario como buena práctica"
    ),
}

# Mapeo de áreas por temas clave
AREA_KEYWORDS_MAPPING: Dict[str, List[str]] = {
    "Atención al Ciudadano": [
        "atención", "servicio", "trato", "espera", "fila", "turno",
        "información", "orientación", "punto de atención"
    ],
    "Servicios Públicos": [
        "acueducto", "alcantarillado", "agua", "energía", "electricidad",
        "gas", "telefonía", "internet", "aseo", "recolección", "basuras",
        "factura", "servicio público", "suscriptor", "consumo"
    ],
    "Tesorería": [
        "pago", "factura", "cobro", "tarifa", "impuesto", "tributo",
        "contribución", "valorización", "descuento", "exención", "pensionado"
    ],
    "Recursos Humanos": [
        "empleado", "contratación", "nomina", "salario", "vinculación",
        "hoja de vida", "selección", "personal", "trabajador"
    ],
    "Jurídica": [
        "demanda", "tutela", "recurso", "apelación", "nulidad",
        "proceso", "sentencia", "auto", "resolución", "acto administrativo",
        "notificación", "legal", "jurídico", "derecho", "ley"
    ],
    "Planeación": [
        "plan", "proyecto", "programa", "presupuesto", "pdt",
        "plan de desarrollo", "indicador", "meta", "estrategia"
    ],
    "Obras Públicas": [
        "obra", "construcción", "vía", "carretera", "puente",
        "infraestructura", "mantenimiento", "repavimentación", "bacheo"
    ],
    "Medio Ambiente": [
        "ambiente", "contaminación", "basura", "residuo", "reciclaje",
        "arbol", "zona verde", "ruido", "emisión", "vertimiento"
    ],
    "Educación": [
        "escuela", "colegio", "educación", "estudiante", "matrícula",
        "beca", "profesor", "curriculum", "jornada", "sedes educativas"
    ],
    "Salud": [
        "salud", "eps", "hospital", "cita médica", "urgencia",
        "medicamento", "tratamiento", "historia clínica", "vacuna"
    ],
    "Tránsito y Transporte": [
        "tránsito", "comparendo", "licencia", "vehículo", "semáforo",
        "accidente", "peaje", "transporte público", "pico y placa"
    ],
    "Hacienda": [
        "impuesto", "tributo", "renta", "ica", "predial", "iva",
        "declaración", "recaudo", "fiscal", "evasión"
    ],
    "Tecnologías de la Información": [
        "sistema", "plataforma", "portal", "correo", "tecnología",
        "datos", "software", "app", "aplicativo", "línea"
    ],
    "Control Interno": [
        "queja", "denuncia", "irregularidad", "auditoría", "control",
        "supervisión", "evaluación", "rendición de cuentas"
    ],
    "Contratación": [
        "contrato", "licitación", "proveedor", "oferta", "propuesta",
        "selección", "adjudicación", "pliego", "convocatoria"
    ],
}

# Patrones de clasificación por tipo de PQR
PQR_TYPE_PATTERNS: Dict[str, List[str]] = {
    "Petición": [
        "solicito", "pido", "requiero", "necesito", "pido información",
        "quiero saber", "deseo obtener", "me gustaría conocer",
        "solicitamos", "requérimos", "pedimos", "información sobre",
        "copias", "certificado", "constancia", "documento"
    ],
    "Queja": [
        "quejo", "me quejo", "insatisfecho", "mal servicio", "pésimo",
        "deficiente", "inadecuado", "no estoy de acuerdo", "descontento",
        "mala atención", "irregularidad", "problema con el servicio",
        "no funciona", "no responde", "incumplimiento"
    ],
    "Reclamo": [
        "reclamo", "reclamación", "cobro excesivo", "factura errada",
        "no corresponde", "incorrecto", "error en", "equivocado",
        "sobrecobro", "cargo no autorizado", "doble cobro",
        "servicio no prestado", "dinero", "devolución", "reembolso"
    ],
    "Sugerencia": [
        "sugiero", "propongo", "recomiendo", "sería bueno", "podrían",
        "idea", "propuesta", "mejora", "optimización", "innovación",
        "sugerencia", "recomendación", "opino que", "considero que"
    ],
}