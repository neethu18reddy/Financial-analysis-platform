"""Financial Research Semantic Chunker Engine.

Splits document text into research-oriented chunks while preserving:
- Exact 1-indexed page number
- Section title header
- Contextual character offsets and token bounds
- Paragraph and financial statement row boundaries
- Deterministic SHA-256 provenance hash per chunk
"""

import hashlib
import re
from typing import List, Dict, Any, Optional

try:
    from app.engine.rag.parser import ExtractedPage
except ImportError:
    from backend.app.engine.rag.parser import ExtractedPage


class FinancialChunk:
    """Represents a discrete semantic chunk of text with exact provenance."""

    def __init__(
        self,
        chunk_index: int,
        page_number: int,
        section_title: str,
        chunk_text: str,
        token_count: int,
        char_start: int = 0,
        char_end: int = 0,
        provenance_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.chunk_index = chunk_index
        self.page_number = page_number
        self.section_title = section_title
        self.chunk_text = chunk_text
        self.token_count = token_count
        self.char_start = char_start
        self.char_end = char_end
        self.provenance_hash = provenance_hash or hashlib.sha256(
            f"{page_number}_{chunk_index}_{chunk_text[:50]}".encode("utf-8")
        ).hexdigest()
        self.metadata = metadata or {}

    @property
    def text(self) -> str:
        """Alias property for chunk_text."""
        return self.chunk_text


class FinancialChunkerEngine:
    """Creates structured chunks calibrated for financial inquiries (e.g. capex, accounting policies, management commentary)."""

    def __init__(
        self,
        chunk_size_words: int = 250,
        overlap_words: int = 40,
        min_chunk_words: int = 25,
        target_chunk_words: Optional[int] = None,
    ):
        self.chunk_size_words = target_chunk_words if target_chunk_words is not None else chunk_size_words
        self.overlap_words = overlap_words
        self.min_chunk_words = min_chunk_words

    def chunk_page(
        self,
        page: ExtractedPage,
        starting_chunk_index: int,
        document_hash: str = "doc_hash",
    ) -> List[FinancialChunk]:
        """Chunks a single page while respecting paragraphs and section headers."""
        text = page.cleaned_text
        if not text:
            return []

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks: List[FinancialChunk] = []
        
        current_words: List[str] = []
        current_chunk_idx = starting_chunk_index
        char_offset = 0

        def _make_chunk(words_list: List[str], idx: int) -> FinancialChunk:
            content = " ".join(words_list)
            prov_hash = hashlib.sha256(
                f"{document_hash}_{page.page_number}_{idx}".encode("utf-8")
            ).hexdigest()
            return FinancialChunk(
                chunk_index=idx,
                page_number=page.page_number,
                section_title=page.detected_section,
                chunk_text=content,
                token_count=int(len(words_list) * 1.3),
                char_start=char_offset,
                char_end=char_offset + len(content),
                provenance_hash=prov_hash,
                metadata={
                    "page": page.page_number,
                    "section": page.detected_section,
                    "has_tables": page.has_tables,
                },
            )

        for para in paragraphs:
            para_words = para.split()
            if not para_words:
                continue

            # If single paragraph is very long, split it by sentences
            if len(para_words) > self.chunk_size_words:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for sent in sentences:
                    sent_words = sent.split()
                    if len(current_words) + len(sent_words) > self.chunk_size_words and len(current_words) >= self.min_chunk_words:
                        chunks.append(_make_chunk(current_words, current_chunk_idx))
                        current_chunk_idx += 1
                        current_words = current_words[-self.overlap_words:] if len(current_words) > self.overlap_words else []
                    current_words.extend(sent_words)
            else:
                if len(current_words) + len(para_words) > self.chunk_size_words and len(current_words) >= self.min_chunk_words:
                    chunks.append(_make_chunk(current_words, current_chunk_idx))
                    current_chunk_idx += 1
                    current_words = current_words[-self.overlap_words:] if len(current_words) > self.overlap_words else []
                current_words.extend(para_words)

        # Flush remaining words
        if current_words and len(current_words) >= self.min_chunk_words:
            chunks.append(_make_chunk(current_words, current_chunk_idx))
        elif current_words and not chunks:
            chunks.append(_make_chunk(current_words, current_chunk_idx))

        # Fallback if text was short but non-empty (e.g. cover page or single sentence)
        if not chunks and text.strip():
            words = text.split()
            chunks.append(_make_chunk(words, starting_chunk_index))

        return chunks

    def chunk_pages(
        self,
        document_id: int,
        pages: List[ExtractedPage],
        document_hash: str,
    ) -> List[FinancialChunk]:
        """Processes an entire document into an indexed sequence of chunks with document hash provenance."""
        all_chunks: List[FinancialChunk] = []
        global_idx = 0
        for page in pages:
            page_chunks = self.chunk_page(page, starting_chunk_index=global_idx, document_hash=document_hash)
            all_chunks.extend(page_chunks)
            global_idx += len(page_chunks)
        return all_chunks

    def chunk_document(self, pages: List[ExtractedPage]) -> List[FinancialChunk]:
        """Processes an entire document into an indexed sequence of chunks."""
        return self.chunk_pages(document_id=0, pages=pages, document_hash="default_doc")
