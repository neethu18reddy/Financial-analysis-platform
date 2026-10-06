"""Retrieval and Evidence Citation Service for Annual Report Intelligence (Async).

Handles:
1. Multi-filter vector similarity search across indexed annual report chunks.
2. Generating verbatim, verifiable EvidenceCitations with exact page numbers and provenance hashes.
3. Ranking results by cosine relevance and semantic financial keyword proximity.
"""

import time
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from app.models.document_intelligence import (
        DocumentRetrievalQuery,
        DocumentRetrievalResponse,
        DocumentRetrievalResult,
        EvidenceCitation,
    )
    from app.engine.rag.vector_store import get_global_vector_store
    from app.engine.rag.document_service import DocumentService
    from app.engine.rag.embeddings import get_default_embedding_provider
    from app.engine.rag.base import RAG_METHODOLOGY_VERSION
except ImportError:
    from backend.app.models.document_intelligence import (
        DocumentRetrievalQuery,
        DocumentRetrievalResponse,
        DocumentRetrievalResult,
        EvidenceCitation,
    )
    from backend.app.engine.rag.vector_store import get_global_vector_store
    from backend.app.engine.rag.document_service import DocumentService
    from backend.app.engine.rag.embeddings import get_default_embedding_provider
    from backend.app.engine.rag.base import RAG_METHODOLOGY_VERSION


class RetrievalService:
    """Service for querying indexed filings and generating verifiable evidence citations."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.doc_service = DocumentService(db_session)
        self.vector_store = get_global_vector_store()
        self.embedding_provider = get_default_embedding_provider()

    async def retrieve(self, query: DocumentRetrievalQuery) -> DocumentRetrievalResponse:
        """Execute semantic search across document library and return ranked evidence citations."""
        start_time = time.perf_counter()

        # Ensure seed documents are ingested & indexed
        await self.doc_service.ensure_seed_documents()

        # Search vector store
        raw_matches = self.vector_store.search(
            query_text=query.query_text,
            ticker=query.ticker,
            fiscal_year=query.fiscal_year,
            section=query.section,
            top_k=query.top_k,
            min_relevance_score=query.min_relevance_score,
        )

        results: List[DocumentRetrievalResult] = []
        for item, score in raw_matches:
            # Build verifiable citation
            citation = EvidenceCitation(
                document_id=item.document_id,
                document_title=item.document_title,
                ticker=item.ticker,
                fiscal_year=item.fiscal_year,
                page_number=item.page_number,
                section_title=item.section_title,
                exact_quote=item.chunk_text[:300].strip() + ("..." if len(item.chunk_text) > 300 else ""),
                relevance_score=score,
                source_url=item.source_url,
                provenance_hash=item.provenance_hash,
            )

            result = DocumentRetrievalResult(
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                document_title=item.document_title,
                ticker=item.ticker,
                fiscal_year=item.fiscal_year,
                page_number=item.page_number,
                section_title=item.section_title,
                chunk_text=item.chunk_text,
                relevance_score=score,
                citation=citation,
            )
            results.append(result)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        filters_applied = {
            k: v for k, v in {
                "ticker": query.ticker,
                "fiscal_year": query.fiscal_year,
                "section": query.section,
                "document_type": query.document_type.value if query.document_type else None,
                "top_k": query.top_k,
                "min_relevance_score": query.min_relevance_score,
            }.items() if v is not None
        }

        return DocumentRetrievalResponse(
            query_text=query.query_text,
            filters_applied=filters_applied,
            total_matches=len(results),
            results=results,
            retrieval_latency_ms=latency_ms,
            embedding_model=self.embedding_provider.model_name,
            methodology_version=RAG_METHODOLOGY_VERSION,
        )
