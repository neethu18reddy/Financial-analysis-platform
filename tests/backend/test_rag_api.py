"""Integration Tests for Document Intelligence & RAG FastAPI Endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_list_documents_endpoint():
    """Verify GET /api/v1/documents endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        assert any(d["ticker"] == "RELIANCE" for d in data)


@pytest.mark.asyncio
async def test_get_document_detail_and_page_endpoint():
    """Verify GET /api/v1/documents/{id} and /api/v1/documents/{id}/pages/{page} endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        list_res = await ac.get("/api/v1/documents?ticker=TCS")
        assert list_res.status_code == 200
        docs = list_res.json()
        assert len(docs) > 0
        doc_id = docs[0]["id"]

        # Detail
        detail_res = await ac.get(f"/api/v1/documents/{doc_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["ticker"] == "TCS"
        assert len(detail["pages"]) >= 1

        # Page 1
        page_res = await ac.get(f"/api/v1/documents/{doc_id}/pages/1")
        assert page_res.status_code == 200
        page_data = page_res.json()
        assert page_data["page_number"] == 1
        assert "TATA CONSULTANCY SERVICES" in page_data["text"]


@pytest.mark.asyncio
async def test_canonical_sections_endpoint():
    """Verify GET /api/v1/documents/sections/canonical."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/documents/sections/canonical")
        assert res.status_code == 200
        sections = res.json()
        assert "MANAGEMENT_DISCUSSION_AND_ANALYSIS" in sections
        assert "INDEPENDENT_AUDITORS_REPORT" in sections


@pytest.mark.asyncio
async def test_document_semantic_search_endpoint():
    """Verify POST /api/v1/documents/search endpoint."""
    payload = {
        "query_text": "share buyback and dividend payout",
        "ticker": "TCS",
        "top_k": 3,
        "min_relevance_score": 0.1,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/documents/search", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["query_text"] == "share buyback and dividend payout"
        assert data["total_matches"] > 0
        assert data["results"][0]["citation"]["ticker"] == "TCS"
        assert "buyback" in data["results"][0]["chunk_text"].lower() or "dividend" in data["results"][0]["chunk_text"].lower()
