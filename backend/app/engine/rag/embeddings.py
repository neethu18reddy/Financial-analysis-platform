"""Embedding providers abstraction for Document Intelligence & RAG subsystem.

Supports:
1. DeterministicLocalEmbeddingProvider: Zero-dependency, 384-dimensional hashed
   TF-IDF vectorizer for instantaneous local testing, deterministic execution, and
   offline environments.
2. Pluggable BaseEmbeddingProvider contract for future external embedding endpoints
   (e.g., SentenceTransformers, Gemini, OpenAI).
"""

import abc
import hashlib
import math
import re
from typing import List, Sequence


class BaseEmbeddingProvider(abc.ABC):
    """Abstract base class for all embedding generation backends."""

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """Name of the underlying embedding model."""
        pass

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        """Vector dimensionality."""
        pass

    @abc.abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate normalized embedding vector for a single text chunk."""
        pass

    @abc.abstractmethod
    def embed_batch(self, texts: Sequence[str]) -> List[List[float]]:
        """Generate normalized embedding vectors for a batch of text chunks."""
        pass

    @staticmethod
    def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
        """Compute cosine similarity between two unit-normalized vectors.
        
        Range: [-1.0, 1.0], clamped to [0.0, 1.0] for retrieval relevance.
        """
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        
        sim = dot_product / (norm_a * norm_b)
        return max(0.0, min(1.0, float(sim)))


class DeterministicLocalEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministic, zero-dependency 384-dimensional feature hashing vectorizer.
    
    Generates rich, consistent, normalized dense embedding vectors based on
    word tokens, character n-grams (subword features), and domain-specific financial term
    weighting. Ideal for local development, CI/CD test suites, and offline environments.
    """

    def __init__(self, dimension: int = 384):
        self._dimension = dimension
        self._model_name = f"deterministic-financial-hashing-{dimension}d"
        
        # Financial domain boost keywords
        self._financial_keywords = {
            "revenue", "profit", "ebitda", "margin", "pat", "ebit", "capex", "depreciation",
            "amortization", "borrowings", "debt", "equity", "cash", "dividend", "contingent",
            "liability", "auditor", "opinion", "qualifications", "impairment", "related",
            "party", "director", "remuneration", "segment", "geographic", "risk", "governance",
            "internal", "controls", "going", "concern", "taxation", "provision", "receivables",
            "inventory", "turnover", "roce", "roe", "npa", "slippages", "guidance", "headwinds"
        }

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def _tokenize(self, text: str) -> List[str]:
        """Extract alphanumeric words and 3-4 char ngrams for robust matching."""
        cleaned = text.lower()
        words = re.findall(r"\b[a-z0-9_]{2,}\b", cleaned)
        
        tokens = list(words)
        # Add character tri-grams for subword matching
        for word in words:
            if len(word) >= 4:
                for i in range(len(word) - 2):
                    tokens.append(f"ng_{word[i:i+3]}")
        return tokens

    def embed_text(self, text: str) -> List[float]:
        """Embeds text into a unit-normalized vector using feature hashing."""
        vector = [0.0] * self._dimension
        tokens = self._tokenize(text)
        
        if not tokens:
            return vector

        # Count frequencies
        token_counts: dict[str, float] = {}
        for token in tokens:
            token_counts[token] = token_counts.get(token, 0.0) + 1.0

        for token, count in token_counts.items():
            # Term weight: log(1 + count)
            weight = math.log1p(count)
            
            # Domain boost for key financial terms
            if token in self._financial_keywords:
                weight *= 2.2
            
            # Hash to index and sign bit
            h = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(h[:4], "big") % self._dimension
            sign = 1.0 if (int.from_bytes(h[4:6], "big") % 2 == 0) else -1.0
            
            vector[idx] += sign * weight

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0.0:
            vector = [v / norm for v in vector]

        return vector

    def embed_batch(self, texts: Sequence[str]) -> List[List[float]]:
        """Batch embedding generation."""
        return [self.embed_text(t) for t in texts]


def get_default_embedding_provider() -> BaseEmbeddingProvider:
    """Factory helper returning the default active embedding provider."""
    return DeterministicLocalEmbeddingProvider(dimension=384)
