"""RAG pipeline — orchestrates retrieval, reranking, compression, and LLM generation."""
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, AsyncGenerator, cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.core.config import settings
from app.rag.retriever import HybridRetriever
from app.rag.reranker import rerank
from app.rag.context_compressor import compress_context_list
from app.rag.cache import RetrievalCache, SemanticCache
from app.rag.metrics import RAGMetrics
from app.rag.query_processor import QueryIntentClassifier

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Composes retrieval, reranking, caching, and generation into a single pipeline."""

    def __init__(
        self,
        openai_client: Optional[AsyncOpenAI] = None,
        embedding_client: Optional[AsyncOpenAI] = None,
        rerank_client: Optional[AsyncOpenAI] = None,
    ):
        self.openai_client = openai_client
        self.rerank_client = rerank_client
        self.retriever = HybridRetriever(openai_client=openai_client, embedding_client=embedding_client)
        self.cache = RetrievalCache()
        self.semantic_cache = SemanticCache()
        self.metrics = RAGMetrics()

    async def get_embedding(self, text: str) -> List[float]:
        return await self.retriever.get_embedding(text)

    # ---- Retrieval with caching ----

    async def search_knowledge_base(
        self,
        query: str,
        organization_id: int,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents with caching and retry."""
        start = time.perf_counter()
        self.metrics.inc("retrieval_total")
        self.metrics.record_event("retrieval", 1)

        # Exact cache (skip for document-specific queries)
        if not document_ids:
            cached = await self.cache.get(query, organization_id, top_k)
            if cached is not None:
                self.metrics.inc("cache_hit")
                self.metrics.record_event("cache_hit", 1)
                if cached:
                    self.metrics.inc("retrieval_hit")
                    self.metrics.record_event("retrieval_hit", 1)
                elapsed = (time.perf_counter() - start) * 1000
                self.metrics.inc("latency_count")
                self.metrics.record_event("latency", elapsed)
                return cached

        # Semantic cache
        query_vector = None
        if not document_ids:
            query_vector = await self.get_embedding(query)
            if query_vector:
                sem_cached = await self.semantic_cache.get(query_vector)
                if sem_cached:
                    self.metrics.inc("semantic_cache_hit")
                    self.metrics.inc("cache_hit")
                    if sem_cached:
                        self.metrics.inc("retrieval_hit")
                    elapsed = (time.perf_counter() - start) * 1000
                    self.metrics.inc("latency_count")
                    self.metrics.record_event("latency", elapsed)
                    if not document_ids:
                        await self.cache.set(query, organization_id, top_k, sem_cached)
                    return sem_cached

        # Retrieve with retry
        retries = max(0, int(settings.RAG_RETRIEVAL_MAX_RETRIES or 2))
        result = []
        for attempt in range(retries + 1):
            try:
                if attempt > 0:
                    self.metrics.inc("retry_total")
                result, qv = await self.retriever.retrieve(query, organization_id, top_k, document_ids)
                if not query_vector and qv:
                    query_vector = qv
                break
            except Exception as e:
                logger.warning(f"Retrieval attempt {attempt + 1}/{retries + 1} failed: {e}")
                if attempt < retries:
                    await asyncio.sleep(min(1.5, 0.3 * (2 ** attempt)))

        if not document_ids:
            await self.cache.set(query, organization_id, top_k, result)
        if query_vector and result:
            await self.semantic_cache.set(query, query_vector, "", result)

        if result:
            self.metrics.inc("retrieval_hit")
            self.metrics.record_event("retrieval_hit", 1)
        elapsed = (time.perf_counter() - start) * 1000
        self.metrics.inc("latency_count")
        self.metrics.record_event("latency", elapsed)
        return result

    # ---- Groundedness reporting ----

    def report_grounded(self, has_sources: bool) -> None:
        self.metrics.inc("grounded_total")
        self.metrics.record_event("grounded", 1)
        if has_sources:
            self.metrics.inc("grounded_hit")
            self.metrics.record_event("grounded_hit", 1)

    def report_tokens(self, input_tokens: int, output_tokens: int) -> None:
        self.metrics.inc("total_input_tokens", input_tokens)
        self.metrics.inc("total_output_tokens", output_tokens)
        self.metrics.inc("llm_request_count")

    def get_metrics(self, window_seconds: int = 0) -> Dict[str, Any]:
        return self.metrics.get_snapshot(window_seconds)

    # ---- LLM streaming ----

    async def chat_stream(
        self,
        query: str,
        context: List[Dict[str, Any]],
        history: List[Dict[str, str]] = None,
        system_prompt_override: Optional[str] = None,
        enable_compression: bool = True,
        enable_masking: bool = True,
    ) -> AsyncGenerator[str, None]:
        """Stream LLM response with context compression and optional PII masking."""
        if not self.openai_client:
            yield "LLM未配置"
            return

        # PII masking
        original_query = query
        masking_mapping = {}
        if enable_masking and getattr(settings, "ENABLE_PII_MASKING", False):
            from app.services.masking_service import masking_service
            query, masking_mapping = masking_service.mask_text(query)

        # Compress context
        if enable_compression and context:
            compressed = compress_context_list(context, query, max_context_chars=8000)
        else:
            compressed = context

        context_str = "\n\n".join([
            f"资料[{i + 1}] (文件名: {item.get('filename', '未知文档')}):\n{(item.get('snippet') or item.get('text', ''))[:3000]}"
            for i, item in enumerate(compressed)
        ]) if compressed else "（未找到相关文档）"

        # Intent-based guidance
        intent = QueryIntentClassifier.classify(query)
        intent_guidance = {
            "factual": "请以事实陈述的方式回答，准确引用来源。",
            "procedural": "请按步骤清晰说明操作流程。",
            "list": "请列出所有相关项并简要说明。",
            "definition": "请给出清晰的定义和解释。",
            "comparison": "请从多个维度对比分析。",
            "causal": "请说明原因和结果。",
            "summary": "请给出简明扼要的总结。",
            "other": "请基于文档内容回答。",
        }.get(intent, "请基于文档内容回答。")

        system_prompt = system_prompt_override or (
            "你是企业知识库问答助手。你的任务是基于提供的【参考文档】提供准确、客观的回答。\n"
            f"📌 回答指导: {intent_guidance}\n"
            "⚠️ 核心约束：\n"
            "1. **严格忠于原文**：只能根据提供的【参考文档】回答。如果文档中没有相关信息，必须明确告知用户。\n"
            "2. **精准引用**：使用 [n] 格式标注引用来源。\n"
            "3. **结构化输出**：多使用分点列表（Markdown 格式）。\n"
            "4. **语言要求**：始终使用【简体中文】回答。\n"
            "5. **拒绝臆测**：严禁引用训练数据中的外部知识补充文档缺失部分。"
        )

        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            *cast(List[ChatCompletionMessageParam], (history or [])[-8:]),
            {"role": "user", "content": f"【参考文档】：\n{context_str}\n\n【问题】：{query}"},
        ]

        try:
            model = settings.LOCAL_LLM_MODEL if settings.ENABLE_LOCAL_LLM else settings.DEEPSEEK_MODEL
            stream = await self.openai_client.chat.completions.create(
                model=model, messages=messages, stream=True,
                temperature=0.1, max_tokens=settings.AI_MAX_TOKENS,
                timeout=settings.AI_STREAM_TIMEOUT,
            )
            full_response = ""
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            # Token estimation
            input_text = "".join(str(m.get("content", "")) for m in messages if m.get("content"))
            self.report_tokens(max(1, int(len(input_text) / 1.5)), max(1, int(len(full_response) / 1.5)))

            # Unmask
            if masking_mapping:
                from app.services.masking_service import masking_service
                masking_service.unmask_text(full_response, masking_mapping)
                logger.info("PII masking: response unmasked")

        except Exception as e:
            yield f"LLM Error: {e}"
