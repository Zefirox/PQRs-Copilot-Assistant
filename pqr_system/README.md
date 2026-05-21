# 🏛️ AI-Powered PQR Processing System

Intelligent system for processing **Peticiones, Quejas, Reclamos y Sugerencias (PQRs)** in Colombian public entities, based on **Ley 1437 de 2011 (CPACA)** and **Ley 1755 de 2015**.

## 🚀 Core Features

### 1. 📊 Semantic Classification & Automated Routing
- An LLM processes the citizen's free-text input to classify the request
- Automatically identifies whether it's a **Petición, Queja, Reclamo or Sugerencia**
- Calculates **legal response terms** in business days according to Colombian regulations
- Automatically assigns to the **competent area** within the entity
- **Fallback** based on keyword analysis when no LLM is available

### 2. 🤖 Response Copilot for Officials (RAG)
- **RAG** architecture (Retrieval-Augmented Generation)
- Searches the knowledge base: regulations, internal policies, historical responses
- Generates **formal, structured, and legally sound drafts**
- The official reviews and adjusts — **assisted, not replaced**
- Reduces drafting time from hours to minutes

## 🏗️ Architecture

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

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
cd pqr_system/backend
pip install -r requirements.txt
```

### Configuration

Edit the `.env` file to configure your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
```

> **Note:** The system works without an OpenAI API key using keyword-based classification and response templates as fallback.

### Running

```bash
python run.py
```

The application will be available at:
- 🌐 **Web interface:** http://localhost:8000
- 📚 **API docs:** http://localhost:8000/docs
- 🔧 **API ReDoc:** http://localhost:8000/redoc

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/pqr` | File a new PQR (classifies + assigns + calculates deadline) |
| `GET` | `/api/v1/pqr` | List PQRs with filters |
| `GET` | `/api/v1/pqr/{id}` | Get PQR by ID |
| `POST` | `/api/v1/pqr/classify` | Classify text without filing |
| `POST` | `/api/v1/copilot/generate` | Generate response draft (RAG) |
| `GET` | `/api/v1/copilot/knowledge-base/stats` | Knowledge base statistics |
| `POST` | `/api/v1/copilot/knowledge-base/load` | Load documents into the knowledge base |
| `GET` | `/api/v1/health` | Health check |

## 🇨🇴 Colombian Regulations Implemented

| PQR Type | Response Term | Legal Basis |
|----------|---------------|-------------|
| Petición de Información | 10 business days | Art. 21 Ley 1437/2011 |
| Petición de Documentos | 10 business days | Art. 21 Ley 1437/2011 |
| Petición de Consulta | 30 business days | Art. 21 Ley 1437/2011 |
| Petición General | 15 business days | Art. 14 Ley 1437/2011 |
| Queja | 15 business days | Art. 14 Ley 1437/2011 |
| Reclamo | 15 business days | Art. 14 Ley 1437/2011 |
| Sugerencia | 30 calendar days | Best practice |

## 🧪 Usage Examples

### File a PQR
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

### Generate draft with Copilot
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

## 🔧 Technologies

- **Backend:** FastAPI, Pydantic, OpenAI Python SDK
- **AI/ML:** OpenAI GPT-4 / DeepSeek, ChromaDB (vector store), RAG, sentence-transformers
- **Frontend:** HTML5, CSS3, JavaScript (vanilla)
- **Regulations:** Ley 1437/2011 (CPACA), Ley 1755/2015, Ley 850/2003

## 📄 License

This project is free to use for Colombian public entities.