"""Tests for Annual Report Retrieval and Verifiable Citations."""

import pytest
from app.db.session import AsyncSessionLocal
from app.engine.rag.document_service import DocumentService
from app.engine.rag.retrieval_service import RetrievalService
from app.models.document_intelligence import DocumentRetrievalQuery


@pytest.mark.asyncio
async def test_seed_documents_ingestion_and_listing():
    """Verify seed documents are properly ingested and listed in the library."""
    async with AsyncSessionLocal() as session:
        doc_service = DocumentService(session)
        docs = await doc_service.list_documents()
        
        assert len(docs) >= 3
        tickers = [d.ticker for d in docs]
        assert "RELIANCE" in tickers
        assert "TCS" in tickers
        assert "HDFCBANK" in tickers

        # Verify page details
        ril_doc = next(d for d in docs if d.ticker == "RELIANCE")
        detail = await doc_service.get_document_detail(ril_doc.id)
        assert detail is not None
        assert detail.page_count == 5
        assert len(detail.pages) == 5
        assert "DIRECTORS_REPORT" in detail.sections_detected
        assert "INDEPENDENT_AUDITORS_REPORT" in detail.sections_detected


@pytest.mark.asyncio
async def test_retrieval_service_with_citations():
    """Verify semantic retrieval generates verifiable citations with page numbers and quotes."""
    async with AsyncSessionLocal() as session:
        retrieval_service = RetrievalService(session)

        query = DocumentRetrievalQuery(
            query_text="capital expenditure 5G network rollout capex",
            ticker="RELIANCE",
            top_k=3,
        )
        response = await retrieval_service.retrieve(query)

        assert response.total_matches > 0
        top_result = response.results[0]
        assert top_result.ticker == "RELIANCE"
        assert top_result.page_number in [1, 2, 3]  # Relevant capex pages
        
        citation = top_result.citation
        assert citation.document_title is not None
        assert citation.page_number > 0
        assert len(citation.exact_quote) > 0
        assert len(citation.provenance_hash) == 64
        assert citation.relevance_score >= 0.15


@pytest.mark.asyncio
async def test_retrieval_auditor_opinion_cross_company():
    """Verify cross-company retrieval for statutory auditor matters."""
    async with AsyncSessionLocal() as session:
        retrieval_service = RetrievalService(session)

        query = DocumentRetrievalQuery(
            query_text="internal financial controls over reporting true and fair view",
            top_k=5,
        )
        response = await retrieval_service.retrieve(query)

        assert response.total_matches >= 2
        for result in response.results:
            assert result.citation.provenance_hash != ""
            assert result.page_number >= 1
