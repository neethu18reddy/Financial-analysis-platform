"""Vector Store index for Document Intelligence and Annual Report retrieval.

Provides in-memory and persistent vector similarity indexing with structured
financial metadata filters (ticker, fiscal_year, section, document_id, page_number).
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from app.engine.rag.embeddings import BaseEmbeddingProvider, DeterministicLocalEmbeddingProvider


class VectorStoreItem:
    """Indexed vector representation with metadata."""

    def __init__(
        self,
        chunk_id: int,
        document_id: int,
        document_title: str,
        ticker: str,
        fiscal_year: int,
        page_number: int,
        section_title: str,
        chunk_text: str,
        embedding: List[float],
        provenance_hash: str,
        source_url: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.document_title = document_title
        self.ticker = ticker.upper()
        self.fiscal_year = fiscal_year
        self.page_number = page_number
        self.section_title = section_title
        self.chunk_text = chunk_text
        self.embedding = embedding
        self.provenance_hash = provenance_hash
        self.source_url = source_url
        self.extra_metadata = extra_metadata or {}

    def matches_filter(
        self,
        ticker: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        section: Optional[str] = None,
        document_id: Optional[int] = None,
        page_number: Optional[int] = None,
    ) -> bool:
        """Evaluate if the item matches all provided query metadata filters."""
        if ticker and self.ticker != ticker.upper():
            return False
        if fiscal_year and self.fiscal_year != fiscal_year:
            return False
        if document_id and self.document_id != document_id:
            return False
        if page_number and self.page_number != page_number:
            return False
        if section:
            # Fuzzy match section title
            clean_filter = section.upper().replace(" ", "_").replace("&", "AND")
            clean_item_sec = self.section_title.upper().replace(" ", "_").replace("&", "AND")
            if clean_filter not in clean_item_sec and clean_item_sec not in clean_filter:
                return False
        return True


class InMemoryVectorStore:
    """In-memory Vector Store with cosine similarity and metadata indexing."""

    def __init__(self, embedding_provider: Optional[BaseEmbeddingProvider] = None):
        self.embedding_provider = embedding_provider or DeterministicLocalEmbeddingProvider()
        self._items: Dict[int, VectorStoreItem] = {}

    def count(self) -> int:
        """Total indexed chunks count."""
        return len(self._items)

    def clear(self) -> None:
        """Clear all items in the vector store."""
        self._items.clear()

    def add_item(self, item: VectorStoreItem) -> None:
        """Add or update an item in the index."""
        self._items[item.chunk_id] = item

    def add_items(self, items: List[VectorStoreItem]) -> None:
        """Batch add items to the index."""
        for item in items:
            self.add_item(item)

    def delete_by_document_id(self, document_id: int) -> int:
        """Remove all chunks associated with a document ID."""
        to_delete = [cid for cid, item in self._items.items() if item.document_id == document_id]
        for cid in to_delete:
            del self._items[cid]
        return len(to_delete)

    def search(
        self,
        query_text: str,
        ticker: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        section: Optional[str] = None,
        document_id: Optional[int] = None,
        page_number: Optional[int] = None,
        top_k: int = 5,
        min_relevance_score: float = 0.15,
    ) -> List[Tuple[VectorStoreItem, float]]:
        """Perform semantic search with metadata pre-filtering.
        
        Returns:
            List of (VectorStoreItem, relevance_score) sorted by relevance descending.
        """
        if not self._items or not query_text.strip():
            return []

        query_vec = self.embedding_provider.embed_text(query_text)
        scored_candidates: List[Tuple[VectorStoreItem, float]] = []

        for item in self._items.values():
            if not item.matches_filter(
                ticker=ticker,
                fiscal_year=fiscal_year,
                section=section,
                document_id=document_id,
                page_number=page_number,
            ):
                continue

            similarity = BaseEmbeddingProvider.cosine_similarity(query_vec, item.embedding)
            
            # Exact keyword boost for precise terms like 'EBITDA', 'auditor', 'contingent'
            q_lower = query_text.lower()
            text_lower = item.chunk_text.lower()
            if any(term in text_lower for term in q_lower.split() if len(term) >= 4):
                similarity = min(1.0, similarity + 0.05)

            if similarity >= min_relevance_score:
                scored_candidates.append((item, round(similarity, 4)))

        # Sort descending by similarity score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:top_k]


# Global singleton instance for app-wide in-memory retrieval caching
_global_vector_store = InMemoryVectorStore()


def get_global_vector_store() -> InMemoryVectorStore:
    """Retrieve the application singleton vector store."""
    return _global_vector_store
