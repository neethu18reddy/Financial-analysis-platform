"""RAG and Document Intelligence Engine package."""

from app.engine.rag.base import (
    RAG_METHODOLOGY_VERSION,
    INDIAN_ANNUAL_REPORT_SECTIONS,
)
from app.engine.rag.parser import (
    AnnualReportParserEngine,
    ExtractedPage,
    ExtractedDocument,
)
from app.engine.rag.chunker import (
    FinancialChunkerEngine,
    FinancialChunk,
)
from app.engine.rag.embeddings import (
    BaseEmbeddingProvider,
    DeterministicLocalEmbeddingProvider,
    get_default_embedding_provider,
)
from app.engine.rag.vector_store import (
    InMemoryVectorStore,
    VectorStoreItem,
    get_global_vector_store,
)
from app.engine.rag.document_service import DocumentService
from app.engine.rag.retrieval_service import RetrievalService
from app.engine.rag.seed_fixtures import SEED_ANNUAL_REPORTS

__all__ = [
    "RAG_METHODOLOGY_VERSION",
    "INDIAN_ANNUAL_REPORT_SECTIONS",
    "AnnualReportParserEngine",
    "ExtractedPage",
    "ExtractedDocument",
    "FinancialChunkerEngine",
    "FinancialChunk",
    "BaseEmbeddingProvider",
    "DeterministicLocalEmbeddingProvider",
    "get_default_embedding_provider",
    "InMemoryVectorStore",
    "VectorStoreItem",
    "get_global_vector_store",
    "DocumentService",
    "RetrievalService",
    "SEED_ANNUAL_REPORTS",
]
