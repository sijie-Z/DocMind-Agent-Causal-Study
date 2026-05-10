"""Built-in tools for the DocMind agent.

Tools are organized by capability:
- search:  Knowledge base retrieval (hybrid search, vector, keyword)
- analyze: Document analysis (summarize, extract, compare)
- manage:  Session management (create session, bind documents)
- sql:     Text-to-SQL for structured data queries
"""
import json
import logging
from typing import Any, Dict, List, Optional

from app.agent.registry import register_tool

logger = logging.getLogger(__name__)


# ─── Search Tools ────────────────────────────────────────────────────────────

@register_tool(
    name="search_knowledge_base",
    description=(
        "Search the enterprise knowledge base using hybrid retrieval "
        "(keyword + vector + RRF fusion). Returns ranked document snippets "
        "with relevance scores and source attribution."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results to return (default 5, max 20)",
                "default": 5,
            },
            "document_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional: restrict search to specific document IDs",
            },
        },
        "required": ["query"],
    },
    tags=["search", "retrieval"],
)
async def search_knowledge_base(
    query: str,
    top_k: int = 5,
    document_ids: Optional[List[str]] = None,
    organization_id: int = 1,
    **_: Any,
) -> str:
    from app.dependencies import get_rag_pipeline
    pipeline = get_rag_pipeline()
    results = await pipeline.search_knowledge_base(
        query=query,
        organization_id=organization_id,
        top_k=min(top_k, 20),
        document_ids=document_ids,
    )
    if not results:
        return "No relevant documents found for this query."

    output = []
    for i, doc in enumerate(results, 1):
        score = doc.get("score", 0)
        filename = doc.get("filename", "Unknown")
        snippet = doc.get("snippet", doc.get("text", "")[:300])
        output.append(f"[{i}] ({score:.2f}) {filename}\n{snippet}")
    return "\n\n".join(output)


@register_tool(
    name="vector_search",
    description=(
        "Pure vector (semantic) search over the knowledge base. "
        "Best for conceptual queries where exact keywords may not match."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Semantic search query",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results (default 5)",
                "default": 5,
            },
        },
        "required": ["query"],
    },
    tags=["search"],
)
async def vector_search(
    query: str,
    top_k: int = 5,
    organization_id: int = 1,
    **_: Any,
) -> str:
    from app.dependencies import get_rag_pipeline
    pipeline = get_rag_pipeline()
    query_vector = await pipeline.get_embedding(query)
    if not query_vector:
        return "Embedding service unavailable."

    from app.core.elasticsearch import ElasticsearchTools
    es_query = {
        "size": top_k,
        "min_score": 1.15,
        "query": {
            "script_score": {
                "query": {"bool": {"filter": [{"term": {"organization_id": str(organization_id)}}]}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_vector},
                },
            }
        },
        "_source": ["content", "filename", "document_id"],
    }
    res = await ElasticsearchTools.search_documents(es_query)
    hits = res.get("hits", {}).get("hits", [])
    if not hits:
        return "No semantically similar documents found."

    output = []
    for i, hit in enumerate(hits, 1):
        src = hit.get("_source", {})
        score = hit.get("_score", 0)
        output.append(f"[{i}] ({score:.2f}) {src.get('filename', '?')}\n{src.get('content', '')[:300]}")
    return "\n\n".join(output)


# ─── Analysis Tools ──────────────────────────────────────────────────────────

@register_tool(
    name="summarize_document",
    description=(
        "Generate a concise summary of a specific document by its ID. "
        "Extracts key points, main topics, and conclusions."
    ),
    parameters={
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "The document ID to summarize",
            },
        },
        "required": ["document_id"],
    },
    tags=["analysis"],
)
async def summarize_document(
    document_id: str,
    organization_id: int = 1,
    **_: Any,
) -> str:
    from app.dependencies import get_rag_pipeline
    from app.core.elasticsearch import ElasticsearchTools

    es_query = {
        "size": 50,
        "query": {"term": {"document_id": document_id}},
        "sort": [{"metadata.chunk_index": {"order": "asc"}}],
        "_source": ["content", "filename"],
    }
    res = await ElasticsearchTools.search_documents(es_query)
    hits = res.get("hits", {}).get("hits", [])
    if not hits:
        return f"Document {document_id} not found in index."

    full_text = "\n".join(h.get("_source", {}).get("content", "") for h in hits)
    filename = hits[0].get("_source", {}).get("filename", "Unknown")

    # Use LLM to summarize
    pipeline = get_rag_pipeline()
    if not pipeline.openai_client:
        return f"Document: {filename}\nContent preview: {full_text[:1000]}..."

    try:
        from app.core.config import settings
        resp = await pipeline.openai_client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是文档摘要专家。请用中文生成结构化摘要。"},
                {"role": "user", "content": f"请为以下文档生成摘要，包含：1)主题 2)关键要点(3-5条) 3)结论\n\n文档：{full_text[:6000]}"},
            ],
            temperature=0.1,
            max_tokens=500,
        )
        summary = resp.choices[0].message.content or "Summary generation failed."
        return f"Document: {filename}\n\n{summary}"
    except Exception as e:
        return f"Document: {filename}\nSummary failed: {e}"


@register_tool(
    name="extract_keywords",
    description=(
        "Extract key terms and entities from a piece of text. "
        "Useful for understanding document topics and building search queries."
    ),
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to extract keywords from",
            },
            "max_keywords": {
                "type": "integer",
                "description": "Maximum number of keywords to extract (default 10)",
                "default": 10,
            },
        },
        "required": ["text"],
    },
    tags=["analysis"],
)
async def extract_keywords(text: str, max_keywords: int = 10, **_: Any) -> str:
    from app.rag.query_processor import extract_query_terms
    terms = extract_query_terms(text)
    return json.dumps(terms[:max_keywords], ensure_ascii=False)


# ─── Document Management Tools ───────────────────────────────────────────────

@register_tool(
    name="list_documents",
    description=(
        "List all documents in the knowledge base for the current organization. "
        "Returns document IDs, filenames, status, and upload dates."
    ),
    parameters={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum documents to return (default 20)",
                "default": 20,
            },
            "status": {
                "type": "string",
                "description": "Filter by status: indexed, parsing, failed, etc.",
            },
        },
    },
    tags=["management"],
    requires_auth=True,
)
async def list_documents(
    limit: int = 20,
    status: Optional[str] = None,
    organization_id: int = 1,
    **_: Any,
) -> str:
    from app.core.database import AsyncSessionLocal
    from app.models.document import Document, DocumentStatus
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        stmt = select(Document).where(Document.organization_id == organization_id)
        if status:
            try:
                stmt = stmt.where(Document.status == DocumentStatus(status))
            except ValueError:
                pass
        stmt = stmt.order_by(Document.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        docs = result.scalars().all()

    if not docs:
        return "No documents found."

    output = []
    for doc in docs:
        status_val = doc.status.value if hasattr(doc.status, "value") else str(doc.status)
        output.append(f"- {doc.id[:8]}... | {doc.filename} | {status_val} | {doc.created_at.strftime('%Y-%m-%d') if doc.created_at else '?'}")
    return "\n".join(output)


@register_tool(
    name="get_document_info",
    description=(
        "Get detailed information about a specific document including "
        "its status, chunk count, file size, and metadata."
    ),
    parameters={
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "The document ID",
            },
        },
        "required": ["document_id"],
    },
    tags=["management"],
)
async def get_document_info(document_id: str, **_: Any) -> str:
    from app.core.database import AsyncSessionLocal
    from app.models.document import Document
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        stmt = select(Document).where(Document.id == document_id)
        result = await session.execute(stmt)
        doc = result.scalar_one_or_none()

    if not doc:
        return f"Document {document_id} not found."

    status_val = doc.status.value if hasattr(doc.status, "value") else str(doc.status)
    return json.dumps({
        "id": doc.id,
        "filename": doc.filename,
        "title": doc.title,
        "status": status_val,
        "file_size": doc.file_size,
        "chunk_count": doc.chunk_count,
        "description": doc.description,
        "keywords": doc.keywords or [],
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "parsed_at": doc.parsed_at.isoformat() if doc.parsed_at else None,
        "indexed_at": doc.indexed_at.isoformat() if doc.indexed_at else None,
    }, ensure_ascii=False, indent=2)


# ─── Conversation Management Tools ──────────────────────────────────────────

@register_tool(
    name="list_conversations",
    description=(
        "List recent chat conversations for the current user. "
        "Returns session IDs, titles, message counts, and last activity."
    ),
    parameters={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum conversations to return (default 10)",
                "default": 10,
            },
        },
    },
    tags=["conversation", "management"],
    requires_auth=True,
)
async def list_conversations(
    limit: int = 10,
    user_id: int = 0,
    organization_id: int = 1,
    **_: Any,
) -> str:
    from app.core.database import AsyncSessionLocal
    from app.models.chat import ChatSession
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .where(ChatSession.organization_id == organization_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        sessions = result.scalars().all()

    if not sessions:
        return "No conversations found."

    output = []
    for s in sessions:
        title = s.title or "Untitled"
        count = s.message_count or 0
        updated = s.updated_at.strftime("%Y-%m-%d %H:%M") if s.updated_at else "?"
        output.append(f"- [{s.id[:8]}...] {title} | {count} msgs | {updated}")
    return "\n".join(output)


@register_tool(
    name="get_conversation_history",
    description=(
        "Retrieve the message history of a specific chat conversation. "
        "Returns messages in chronological order with role and content."
    ),
    parameters={
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "The chat session ID",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum messages to return (default 20)",
                "default": 20,
            },
        },
        "required": ["session_id"],
    },
    tags=["conversation"],
    requires_auth=True,
)
async def get_conversation_history(
    session_id: str,
    limit: int = 20,
    user_id: int = 0,
    **_: Any,
) -> str:
    from app.core.database import AsyncSessionLocal
    from app.models.chat import ChatSession, ChatMessage
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        # Verify ownership
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        result = await session.execute(stmt)
        chat_session = result.scalar_one_or_none()

        if not chat_session:
            return f"Conversation {session_id} not found."
        if chat_session.user_id != user_id:
            return "Access denied: you do not own this conversation."

        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        messages = result.scalars().all()

    if not messages:
        return f"Conversation '{chat_session.title or session_id}' has no messages."

    output = []
    for msg in messages:
        role = msg.message_type.value if hasattr(msg.message_type, "value") else str(msg.message_type)
        content = msg.content[:500] if msg.content else ""
        output.append(f"[{role}] {content}")
    return "\n\n".join(output)


# ─── Prompt Template Tools ──────────────────────────────────────────────────

@register_tool(
    name="list_prompt_templates",
    description=(
        "List available prompt templates. "
        "Returns template names, categories, and descriptions. "
        "Useful for finding reusable prompts for specific tasks."
    ),
    parameters={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Filter by category (e.g. general, translation, summary)",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum templates to return (default 20)",
                "default": 20,
            },
        },
    },
    tags=["prompts"],
)
async def list_prompt_templates(
    category: Optional[str] = None,
    limit: int = 20,
    **_: Any,
) -> str:
    from app.core.database import AsyncSessionLocal
    from app.models.prompt import PromptTemplate
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        stmt = select(PromptTemplate).where(PromptTemplate.is_active == True)
        if category:
            stmt = stmt.where(PromptTemplate.category == category)
        stmt = stmt.order_by(PromptTemplate.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        templates = result.scalars().all()

    if not templates:
        return "No prompt templates found."

    output = []
    for tpl in templates:
        scope = "system" if tpl.is_system else "user"
        output.append(f"- [{tpl.category}] {tpl.name} ({scope}) — {tpl.description or 'No description'}")
    return "\n".join(output)


@register_tool(
    name="get_prompt_template",
    description=(
        "Get the full content of a specific prompt template by name. "
        "Use this to retrieve and apply a reusable prompt."
    ),
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The prompt template name",
            },
        },
        "required": ["name"],
    },
    tags=["prompts"],
)
async def get_prompt_template(name: str, **_: Any) -> str:
    from app.core.database import AsyncSessionLocal
    from app.models.prompt import PromptTemplate
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        stmt = select(PromptTemplate).where(PromptTemplate.name == name)
        result = await session.execute(stmt)
        tpl = result.scalar_one_or_none()

    if not tpl:
        return f"Prompt template '{name}' not found."

    return json.dumps({
        "name": tpl.name,
        "content": tpl.content,
        "description": tpl.description,
        "category": tpl.category,
        "is_system": tpl.is_system,
    }, ensure_ascii=False, indent=2)


# ─── Utility Tools ───────────────────────────────────────────────────────────

@register_tool(
    name="get_current_time",
    description="Get the current date and time. Useful for time-sensitive queries.",
    parameters={"type": "object", "properties": {}},
    tags=["utility"],
)
async def get_current_time(**_: Any) -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
