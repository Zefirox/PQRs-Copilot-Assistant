"""
RAG (Retrieval-Augmented Generation) Engine for PQR Copilot.

Uses ChromaDB for vector storage and retrieval of knowledge base documents,
internal regulations, and historical PQR responses. Generates draft responses
for officials using the retrieved context.
"""
import json
import logging
import os
from typing import List, Optional, Dict, Any

from openai import OpenAI

from app.config import settings
from app.models.pqr import CopilotRequest, CopilotResponse, PQRType

logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieval-Augmented Generation engine for PQR response copilot."""

    def __init__(self):
        self.client = None
        self.collection = None
        self.chroma_client = None
        self._init_openai()
        self._init_chroma()

    def _init_openai(self):
        """Initialize OpenAI-compatible client (Huawei Cloud MaaS)."""
        try:
            if settings.openai_api_key and settings.openai_api_key != "sk-placeholder":
                self.client = OpenAI(
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_base_url,
                )
                logger.info(f"LLM client initialized for RAG engine (model: {settings.openai_model})")
            else:
                logger.warning("API key not configured, RAG will use template-based responses")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM client: {e}")

    def _init_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            persist_dir = settings.chroma_persist_dir
            os.makedirs(persist_dir, exist_ok=True)

            self.chroma_client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.chroma_client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"description": "PQR Knowledge Base - Normativas y respuestas históricas"}
            )
            logger.info(f"ChromaDB initialized with {self.collection.count()} documents")
        except Exception as e:
            logger.warning(f"Failed to initialize ChromaDB: {e}")

    def load_knowledge_base(self, documents: List[Dict[str, Any]]) -> int:
        """
        Load documents into the ChromaDB vector store.
        
        Args:
            documents: List of dicts with keys: id, content, metadata
            
        Returns:
            Number of documents loaded
        """
        if not self.collection:
            logger.error("ChromaDB collection not initialized")
            return 0

        loaded = 0
        for doc in documents:
            try:
                # Check if document already exists
                existing = self.collection.get(ids=[doc["id"]])
                if existing["ids"]:
                    self.collection.update(
                        ids=[doc["id"]],
                        documents=[doc["content"]],
                        metadatas=[doc.get("metadata", {})]
                    )
                else:
                    self.collection.add(
                        ids=[doc["id"]],
                        documents=[doc["content"]],
                        metadatas=[doc.get("metadata", {})]
                    )
                loaded += 1
            except Exception as e:
                logger.error(f"Failed to load document {doc.get('id', 'unknown')}: {e}")

        logger.info(f"Loaded {loaded} documents into knowledge base")
        return loaded

    def _retrieve_context(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from the knowledge base.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of relevant documents with content and metadata
        """
        if not self.collection or self.collection.count() == 0:
            return []

        try:
            query_params = {
                "query_texts": [query],
                "n_results": min(n_results, self.collection.count()),
            }
            if filter_metadata:
                query_params["where"] = filter_metadata

            results = self.collection.query(**query_params)

            documents = []
            for i in range(len(results["ids"][0])):
                documents.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if "distances" in results else None,
                })

            return documents
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []

    async def generate_response(
        self,
        request: CopilotRequest,
    ) -> CopilotResponse:
        """
        Generate a draft response for a PQR using RAG.
        
        Args:
            request: CopilotRequest with PQR details and official's notes
            
        Returns:
            CopilotResponse with draft, sources, and suggestions
        """
        # Build retrieval query
        query = f"{request.pqr_type.value}: {request.pqr_contenido[:500]}"
        if request.funcionario_notas:
            query += f" Notas: {request.funcionario_notas}"

        # Retrieve relevant context
        context_docs = self._retrieve_context(query, n_results=5)
        context_text = "\n\n".join([
            f"[Fuente: {d['metadata'].get('source', 'Desconocida')}]\n{d['content']}"
            for d in context_docs
        ])

        sources = list(set([
            d["metadata"].get("source", "Desconocida")
            for d in context_docs
            if d["metadata"].get("source")
        ]))

        if self.client:
            try:
                return await self._generate_with_llm(request, context_text, sources)
            except Exception as e:
                logger.error(f"LLM generation failed, using template: {e}")

        return self._generate_template_response(request, context_docs, sources)

    async def _generate_with_llm(
        self,
        request: CopilotRequest,
        context_text: str,
        sources: List[str]
    ) -> CopilotResponse:
        """Generate response using LLM with RAG context."""
        tono_instructions = {
            "formal": "Use un tono formal y jurídico, apropiado para una entidad pública colombiana.",
            "amable": "Use un tono amable y cercano, manteniendo el respeto y la formalidad necesaria.",
            "directo": "Use un tono directo y conciso, yendo al grano sin perder formalidad.",
        }

        prompt = f"""Eres un copiloto de respuestas para funcionarios de una entidad pública colombiana. Tu trabajo es generar un borrador de respuesta formal, estructurado y jurídicamente sólido para el siguiente PQR.

TIPO DE PQR: {request.pqr_type.value}
CONTENIDO DEL PQR:
\"\"\"{request.pqr_contenido}\"\"\"

{f"NOTAS DEL FUNCIONARIO: {request.funcionario_notas}" if request.funcionario_notas else ""}

CONTEXTO RECUPERADO DE LA BASE DE CONOCIMIENTO:
{context_text if context_text else "No se encontró contexto relevante en la base de conocimientos."}

INSTRUCCIONES:
1. {tono_instructions.get(request.tono, tono_instructions["formal"])}
2. La respuesta debe incluir:
   - Encabezado formal con fecha y referencia
   - Saludo formal al ciudadano
   - Cuerpo de la respuesta abordando todos los puntos del PQR
   - Fundamento legal cuando aplique
   - Información sobre recursos o siguientes pasos si aplica
   - Despedida formal con nombre y cargo del funcionario
3. Si el contexto recuperado contiene información relevante, úsala y cita la fuente
4. Si no hay suficiente información, indica qué información adicional se necesita
5. NO inventes información que no esté en el contexto o en el PQR
6. La respuesta debe ser un borrador que el funcionario pueda revisar y ajustar

Genera el borrador de respuesta:"""

        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Eres un copiloto experto en redacción de respuestas a PQRs para entidades públicas colombianas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        draft = response.choices[0].message.content.strip()

        # Generate additional suggestions
        suggestions = []
        if not context_text:
            suggestions.append("No se encontró contexto relevante. Verifique que la base de conocimientos esté actualizada.")
        if request.pqr_type == PQRType.RECLAMO:
            suggestions.append("Para reclamos, verifique si se requiere notificación personal según el CPACA.")
        if request.pqr_type == PQRType.QUEJA:
            suggestions.append("Considere si la queja debe ser remitida a Control Interno o Disciplinaria.")

        return CopilotResponse(
            borrador_respuesta=draft,
            fuentes_utilizadas=sources,
            sugerencias_adicionales=suggestions,
            confidence_score=0.85 if context_text else 0.5,
            requires_review=True,
        )

    def _generate_template_response(
        self,
        request: CopilotRequest,
        context_docs: List[Dict],
        sources: List[str]
    ) -> CopilotResponse:
        """Generate a template-based response (fallback when LLM unavailable)."""
        from datetime import datetime

        fecha = datetime.now().strftime("%d de %B de %Y").replace(
            "January", "enero").replace("February", "febrero").replace(
            "March", "marzo").replace("April", "abril").replace(
            "May", "mayo").replace("June", "junio").replace(
            "July", "julio").replace("August", "agosto").replace(
            "September", "septiembre").replace("October", "octubre").replace(
            "November", "noviembre").replace("December", "diciembre")

        # Build context section
        context_section = ""
        if context_docs:
            context_section = "\n\nINFORMACIÓN RELEVANTE:\n"
            for doc in context_docs[:3]:
                context_section += f"- {doc['content'][:300]}...\n"

        # Type-specific templates
        templates = {
            PQRType.PETICION: f"""Bogotá D.C., {fecha}

Señor(a)
Ciudadano

Ref: Respuesta a Petición - {request.pqr_id}

Respetado señor(a):

En atención a su petición, nos permitimos informarle que su solicitud ha sido recibida y se encuentra en proceso de estudio y verificación.{context_section}

Una vez adelantadas las verificaciones correspondientes, procederemos a dar respuesta oportuna a su solicitud, de conformidad con lo establecido en el artículo 14 de la Ley 1437 de 2011 (Código de Procedimiento Administrativo y de lo Contencioso Administrativo).

Atentamente,

_________________________
[Nombre del Funcionario]
[Cargo]
{settings.default_entity_name}""",
            PQRType.QUEJA: f"""Bogotá D.C., {fecha}

Señor(a)
Ciudadano

Ref: Respuesta a Queja - {request.pqr_id}

Respetado señor(a):

Hemos recibido su queja y damos traslado a la dependencia competente para su correspondiente verificación y atención.{context_section}

Le informamos que su queja será analizada y se adoptarán las medidas pertinentes conforme a las normas internas de la entidad. De ser necesario, nos pondremos en contacto con usted para solicitar información adicional.

Atentamente,

_________________________
[Nombre del Funcionario]
[Cargo]
{settings.default_entity_name}""",
            PQRType.RECLAMO: f"""Bogotá D.C., {fecha}

Señor(a)
Ciudadano

Ref: Respuesta a Reclamo - {request.pqr_id}

Respetado señor(a):

Hemos recibido su reclamo y procederemos a realizar la verificación correspondiente de los hechos y circunstancias que lo motivan.{context_section}

Con base en el resultado de la verificación, se determinará si procede o no la aceptación de su reclamo, de conformidad con la normativa vigente. Le informaremos oportunamente sobre el resultado de esta gestión.

Atentamente,

_________________________
[Nombre del Funcionario]
[Cargo]
{settings.default_entity_name}""",
            PQRType.SUGERENCIA: f"""Bogotá D.C., {fecha}

Señor(a)
Ciudadano

Ref: Respuesta a Sugerencia - {request.pqr_id}

Respetado señor(a):

Agradecemos su interés en contribuir al mejoramiento de nuestra entidad. Hemos recibido su sugerencia y la hemos remitido al área competente para su evaluación.{context_section}

Las sugerencias de los ciudadanos son valiosas insumos para el mejoramiento continuo de nuestros servicios. Serán tenidas en cuenta en los procesos de planeación de la entidad.

Atentamente,

_________________________
[Nombre del Funcionario]
[Cargo]
{settings.default_entity_name}""",
        }

        draft = templates.get(request.pqr_type, templates[PQRType.PETICION])

        suggestions = [
            "Revise y ajuste el borrador antes de enviar la respuesta definitiva.",
            "Verifique que la información del ciudadano sea correcta.",
        ]
        if not context_docs:
            suggestions.insert(0, "No se encontró contexto relevante en la base de conocimientos. Considere actualizarla.")

        return CopilotResponse(
            borrador_respuesta=draft,
            fuentes_utilizadas=sources,
            sugerencias_adicionales=suggestions,
            confidence_score=0.4 if not context_docs else 0.6,
            requires_review=True,
        )