# 🏛️ Sistema de Procesamiento de PQRs con IA

Sistema inteligente para el procesamiento de **Peticiones, Quejas, Reclamos y Sugerencias (PQRs)** en entidades públicas colombianas, basado en la **Ley 1437 de 2011 (CPACA)** y la **Ley 1755 de 2015**.

## 🚀 Funcionalidades Principales

### 1. 📊 Clasificación y Enrutamiento Semántico Automatizado
- Un LLM procesa el texto libre del ciudadano para clasificar la solicitud
- Identifica automáticamente si es **Petición, Queja, Reclamo o Sugerencia**
- Calcula los **términos legales de respuesta** en días hábiles según la normativa colombiana
- Asigna automáticamente al **área competente** de la entidad
- **Fallback** basado en palabras clave cuando no hay LLM disponible

### 2. ✅ Análisis de Completitud (Validación al Instante)
- La IA evalúa el contenido en **tiempo real** al momento de la radicación
- Detecta datos obligatorios faltantes (cédula, dirección, soportes)
- Mensajes amigables: *"Detectamos que mencionas una factura pero no la has adjuntado, ¿deseas incluirla para agilizar tu trámite?"*
- Puntuación de completitud (0-100%)

### 3. 🤖 Copiloto de Respuestas para Funcionarios (RAG)
- Arquitectura **RAG** (Retrieval-Augmented Generation)
- Busca en la base de conocimientos: normativas, políticas internas, respuestas históricas
- Genera **borradores formales, estructurados y jurídicamente sólidos**
- El funcionario revisa y ajusta — **no se reemplaza, se asiste**
- Reduce el tiempo de redacción de horas a minutos

## 🏗️ Arquitectura

```
pqr_system/
└── backend/
    ├── app/
    │   ├── main.py              # FastAPI application
    │   ├── config.py            # Configuration settings
    │   ├── routes.py            # API endpoints
    │   ├── models/
    │   │   ├── pqr.py           # PQR data models
    │   │   └── classification.py # Colombian law definitions
    │   ├── services/
    │   │   ├── classifier.py    # Semantic classification service
    │   │   ├── completeness.py  # Completeness analysis service
    │   │   └── rag_engine.py    # RAG engine & copilot service
    │   └── data/
    │       └── knowledge_base.py # Default knowledge base
    ├── frontend/
    │   ├── index.html           # Web interface
    │   ├── styles.css           # Styles
    │   └── app.js               # Frontend logic
    ├── requirements.txt
    ├── .env                     # Environment variables
    └── run.py                   # Run script
```

## ⚡ Inicio Rápido

### Prerrequisitos
- Python 3.10+
- pip

### Instalación

```bash
cd pqr_system/backend
pip install -r requirements.txt
```

### Configuración

Edite el archivo `.env` para configurar su API key de OpenAI:

```env
OPENAI_API_KEY=sk-su-api-key-aqui
OPENAI_MODEL=gpt-4
```

> **Nota:** El sistema funciona sin API key de OpenAI usando clasificación por palabras clave y plantillas de respuesta como fallback.

### Ejecución

```bash
python run.py
```

La aplicación estará disponible en:
- 🌐 **Interfaz web:** http://localhost:8000
- 📚 **API docs:** http://localhost:8000/docs
- 🔧 **API ReDoc:** http://localhost:8000/redoc

## 📡 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/pqr` | Radicar nuevo PQR (clasifica + analiza completitud) |
| `GET` | `/api/v1/pqr` | Listar PQRs con filtros |
| `GET` | `/api/v1/pqr/{id}` | Obtener PQR por ID |
| `POST` | `/api/v1/pqr/classify` | Clasificar texto sin radicar |
| `POST` | `/api/v1/pqr/analyze-completeness` | Analizar completitud sin radicar |
| `POST` | `/api/v1/copilot/generate` | Generar borrador de respuesta (RAG) |
| `GET` | `/api/v1/copilot/knowledge-base/stats` | Estadísticas de base de conocimientos |
| `POST` | `/api/v1/copilot/knowledge-base/load` | Cargar documentos a la base |
| `GET` | `/api/v1/health` | Health check |

## 🇨🇴 Normatividad Colombiana Implementada

| Tipo de PQR | Término | Base Legal |
|-------------|---------|------------|
| Petición de Información | 10 días hábiles | Art. 21 Ley 1437/2011 |
| Petición de Documentos | 10 días hábiles | Art. 21 Ley 1437/2011 |
| Petición de Consulta | 30 días hábiles | Art. 21 Ley 1437/2011 |
| Petición General | 15 días hábiles | Art. 14 Ley 1437/2011 |
| Queja | 15 días hábiles | Art. 14 Ley 1437/2011 |
| Reclamo | 15 días hábiles | Art. 14 Ley 1437/2011 |
| Sugerencia | 30 días calendario | Buena práctica |

## 🧪 Ejemplos de Uso

### Radicar un PQR
```bash
curl -X POST http://localhost:8000/api/v1/pqr \
  -H "Content-Type: application/json" \
  -d '{
    "contenido": "Solicito información sobre las tarifas del servicio de acueducto para el estrato 3 en el municipio de Bogotá",
    "asunto": "Información tarifas acueducto",
    "ciudadano": {
      "nombre_completo": "Juan Pérez García",
      "tipo_documento": "CC",
      "numero_documento": "12345678",
      "email": "juan@email.com",
      "direccion": "Calle 10 # 20-30"
    }
  }'
```

### Generar borrador con Copiloto
```bash
curl -X POST http://localhost:8000/api/v1/copilot/generate \
  -H "Content-Type: application/json" \
  -d '{
    "pqr_id": "test-001",
    "pqr_contenido": "Reclamo por cobro excesivo en la factura de acueducto del mes de marzo",
    "pqr_type": "Reclamo",
    "tono": "formal"
  }'
```

## 🔧 Tecnologías

- **Backend:** FastAPI, Pydantic, OpenAI Python SDK
- **IA/ML:** OpenAI GPT-4, ChromaDB (vector store), RAG
- **Frontend:** HTML5, CSS3, JavaScript (vanilla)
- **Normatividad:** Ley 1437/2011 (CPACA), Ley 1755/2015, Ley 850/2003

## 📄 Licencia

Este proyecto es de uso libre para entidades públicas colombianas.