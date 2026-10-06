"""Tests for Embedding Provider and Vector Store."""

import pytest
import math
from app.engine.rag.embeddings import DeterministicLocalEmbeddingProvider, BaseEmbeddingProvider
from app.engine.rag.vector_store import InMemoryVectorStore, VectorStoreItem


def test_deterministic_embedding_provider_properties():
    """Verify vector dimension, unit normalization, and deterministic reproducibility."""
    provider = DeterministicLocalEmbeddingProvider(dimension=384)
    assert provider.dimension == 384
    assert "deterministic" in provider.model_name

    text = "Reliance Industries reported consolidated EBITDA of ₹1,78,677 crore driven by retail and 5G digital services."
    vec1 = provider.embed_text(text)
    vec2 = provider.embed_text(text)

    assert len(vec1) == 384
    assert vec1 == vec2, "Embeddings must be strictly deterministic"

    # L2 norm must be ~1.0
    norm = math.sqrt(sum(v * v for v in vec1))
    assert math.isclose(norm, 1.0, rel_tol=1e-4)


def test_embedding_cosine_similarity():
    """Test cosine similarity calculation and domain keyword boosting."""
    provider = DeterministicLocalEmbeddingProvider(dimension=384)
    
    text_a = "Auditor issued clean unmodified opinion on internal financial controls."
    text_b = "Independent auditor report on internal financial controls over reporting."
    text_c = "Agricultural tractor manufacturing and tractor implements export."

    vec_a = provider.embed_text(text_a)
    vec_b = provider.embed_text(text_b)
    vec_c = provider.embed_text(text_c)

    sim_ab = BaseEmbeddingProvider.cosine_similarity(vec_a, vec_b)
    sim_ac = BaseEmbeddingProvider.cosine_similarity(vec_a, vec_c)

    assert sim_ab > sim_ac, "Similar auditor disclosures must score significantly higher than unrelated tractor manufacturing"
    assert 0.0 <= sim_ab <= 1.0


def test_in_memory_vector_store_filtering_and_ranking():
    """Test vector index search with ticker, section, and fiscal year filtering."""
    provider = DeterministicLocalEmbeddingProvider(dimension=384)
    store = InMemoryVectorStore(embedding_provider=provider)

    items = [
        VectorStoreItem(
            chunk_id=1,
            document_id=10,
            document_title="RIL Annual Report FY24",
            ticker="RELIANCE",
            fiscal_year=2024,
            page_number=2,
            section_title="DIRECTORS_REPORT",
            chunk_text="Incurred consolidated capital expenditure capex of ₹1,31,769 crore in 5G rollout.",
            embedding=provider.embed_text("Incurred consolidated capital expenditure capex of ₹1,31,769 crore in 5G rollout."),
            provenance_hash="prov_1",
        ),
        VectorStoreItem(
            chunk_id=2,
            document_id=20,
            document_title="TCS Annual Report FY24",
            ticker="TCS",
            fiscal_year=2024,
            page_number=2,
            section_title="DIRECTORS_REPORT",
            chunk_text="Completed share buyback of 40.9 million equity shares totaling ₹17,000 crore.",
            embedding=provider.embed_text("Completed share buyback of 40.9 million equity shares totaling ₹17,000 crore."),
            provenance_hash="prov_2",
        ),
        VectorStoreItem(
            chunk_id=3,
            document_id=30,
            document_title="HDFC Bank Annual Report FY24",
            ticker="HDFCBANK",
            fiscal_year=2024,
            page_number=3,
            section_title="MANAGEMENT_DISCUSSION_AND_ANALYSIS",
            chunk_text="Gross Non-Performing Assets GNPA stood at 1.24% with provision coverage ratio PCR of 74%.",
            embedding=provider.embed_text("Gross Non-Performing Assets GNPA stood at 1.24% with provision coverage ratio PCR of 74%."),
            provenance_hash="prov_3",
        )
    ]

    store.add_items(items)
    assert store.count() == 3

    # Query for capex in RELIANCE
    results = store.search(query_text="capital expenditure capex 5G", ticker="RELIANCE", top_k=2)
    assert len(results) == 1
    assert results[0][0].ticker == "RELIANCE"
    assert results[0][0].chunk_id == 1

    # Query for buyback across all tickers
    results_all = store.search(query_text="share buyback dividend", top_k=2)
    assert len(results_all) >= 1
    assert results_all[0][0].ticker == "TCS"
