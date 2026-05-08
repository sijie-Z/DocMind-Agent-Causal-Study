# RAG (Retrieval-Augmented Generation) package
# Decomposed from the monolithic rag_service.py into focused modules:
#
#   query_processor  — intent classification, query rewrite, HyDE
#   retriever        — hybrid retrieval (keyword + vector + RRF)
#   reranker         — cross-encoder / LLM reranking
#   context_compressor — context truncation and compression
#   cache            — exact + semantic retrieval cache
#   metrics          — RAG performance metrics
#   pipeline         — orchestrator that composes all components
