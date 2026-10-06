"""PDF Processing and Section Detection Engine.

Extracts text from PDF documents while strictly preserving:
- Exact 1-indexed page boundaries
- SHA-256 document hashing for provenance deduplication
- Structural Section detection calibrated for Indian Statutory Annual Reports (LODR / Companies Act 2013)
- Table detection and formatting preservation
"""

import hashlib
import io
import re
from typing import List, Dict, Any, Optional, Tuple
import pypdf

try:
    from app.engine.rag.base import INDIAN_ANNUAL_REPORT_SECTIONS
except ImportError:
    from backend.app.engine.rag.base import INDIAN_ANNUAL_REPORT_SECTIONS


class ExtractedPage:
    """Represents text extracted from a single physical page of a PDF."""
    def __init__(
        self,
        page_number: int,
        raw_text: str,
        cleaned_text: str,
        detected_section: Optional[str] = None,
        char_count: Optional[int] = None,
        has_tables: bool = False,
    ):
        self.page_number = page_number
        self.raw_text = raw_text
        self.cleaned_text = cleaned_text
        self.char_count = char_count if char_count is not None else len(cleaned_text)
        self.detected_section = detected_section or "GENERAL_DISCLOSURE"
        self.has_tables = has_tables


class ExtractedDocument:
    """Represents a fully extracted document with pages and SHA-256 identity."""
    def __init__(
        self,
        file_name: str,
        file_hash_sha256: str,
        pages: List[ExtractedPage],
        file_size_bytes: int = 0,
    ):
        self.file_name = file_name
        self.file_hash_sha256 = file_hash_sha256
        self.pages = pages
        self.page_count = len(pages)
        self.file_size_bytes = file_size_bytes


class AnnualReportParserEngine:
    """Extracts pages, generates SHA-256 hashes, and detects statutory sections."""

    SECTION_PATTERNS: List[Tuple[str, List[re.Pattern]]] = [
        (
            "MANAGEMENT_DISCUSSION_AND_ANALYSIS",
            [
                re.compile(r"management\s+discussion\s+and\s+analysis", re.IGNORECASE),
                re.compile(r"m\s*d\s*&\s*a", re.IGNORECASE),
                re.compile(r"operating\s+and\s+financial\s+review", re.IGNORECASE),
            ],
        ),
        (
            "INDEPENDENT_AUDITORS_REPORT",
            [
                re.compile(r"independent\s+auditor'?s\s+report", re.IGNORECASE),
                re.compile(r"report\s+on\s+the\s+audit\s+of\s+the\s+financial\s+statements", re.IGNORECASE),
            ],
        ),
        (
            "DIRECTORS_REPORT",
            [
                re.compile(r"board'?s?\s+report", re.IGNORECASE),
                re.compile(r"directors'?\s+report", re.IGNORECASE),
            ],
        ),
        (
            "CORPORATE_GOVERNANCE_REPORT",
            [
                re.compile(r"report\s+on\s+corporate\s+governance", re.IGNORECASE),
                re.compile(r"corporate\s+governance\s+report", re.IGNORECASE),
            ],
        ),
        (
            "NOTES_TO_CONSOLIDATED_FINANCIAL_STATEMENTS",
            [
                re.compile(r"notes\s+to\s+(the\s+)?(consolidated\s+)?financial\s+statements", re.IGNORECASE),
                re.compile(r"significant\s+accounting\s+policies", re.IGNORECASE),
            ],
        ),
        (
            "CONSOLIDATED_BALANCE_SHEET",
            [
                re.compile(r"consolidated\s+balance\s+sheet", re.IGNORECASE),
            ],
        ),
        (
            "CONSOLIDATED_STATEMENT_OF_PROFIT_AND_LOSS",
            [
                re.compile(r"consolidated\s+statement\s+of\s+profit\s+and\s+loss", re.IGNORECASE),
                re.compile(r"consolidated\s+income\s+statement", re.IGNORECASE),
            ],
        ),
        (
            "CONSOLIDATED_CASH_FLOW_STATEMENT",
            [
                re.compile(r"consolidated\s+cash\s+flow\s+statement", re.IGNORECASE),
                re.compile(r"statement\s+of\s+cash\s+flows", re.IGNORECASE),
            ],
        ),
        (
            "RELATED_PARTY_DISCLOSURES",
            [
                re.compile(r"related\s+party\s+transactions", re.IGNORECASE),
                re.compile(r"related\s+party\s+disclosures", re.IGNORECASE),
            ],
        ),
        (
            "RISK_MANAGEMENT_AND_INTERNAL_CONTROLS",
            [
                re.compile(r"risk\s+management", re.IGNORECASE),
                re.compile(r"internal\s+financial\s+controls", re.IGNORECASE),
            ],
        ),
    ]

    @staticmethod
    def compute_sha256(content_bytes: bytes) -> str:
        """Calculates cryptographic SHA-256 fingerprint for document identity."""
        return hashlib.sha256(content_bytes).hexdigest()

    @classmethod
    def detect_section(cls, text: str, previous_section: str = "GENERAL_DISCLOSURE") -> str:
        """Identifies active statutory section from text content."""
        first_few_lines = "\n".join(text.split("\n")[:10])
        for section_name, patterns in cls.SECTION_PATTERNS:
            for pat in patterns:
                if pat.search(first_few_lines):
                    return section_name
        for section_name, patterns in cls.SECTION_PATTERNS:
            for pat in patterns:
                if pat.search(text):
                    return section_name
        return previous_section

    @staticmethod
    def _detect_tables(text: str) -> bool:
        """Heuristic check for financial table presence (multi-column numeric data)."""
        lines = text.split("\n")
        numeric_lines = 0
        for line in lines:
            tokens = line.split()
            numbers = [t for t in tokens if re.search(r"\d+[\.,]?\d*", t)]
            if len(numbers) >= 2:
                numeric_lines += 1
        return numeric_lines >= 3

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """Normalizes whitespaces, removes null bytes and unprintable artifacts."""
        if not raw_text:
            return ""
        cleaned = raw_text.replace("\x00", " ")
        cleaned = re.sub(r"\r\n|\r", "\n", cleaned)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def parse_pdf_bytes(self, pdf_bytes: bytes, file_name: str = "document.pdf") -> ExtractedDocument:
        """Parses a PDF byte stream into structured pages with exact numbering."""
        doc_hash = self.compute_sha256(pdf_bytes)
        pages: List[ExtractedPage] = []
        
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            current_section = "GENERAL_DISCLOSURE"
            
            for idx, page in enumerate(reader.pages, start=1):
                raw_text = page.extract_text() or ""
                cleaned = self.clean_text(raw_text)
                
                current_section = self.detect_section(cleaned, current_section)
                has_tables = self._detect_tables(cleaned)
                
                pages.append(
                    ExtractedPage(
                        page_number=idx,
                        raw_text=raw_text,
                        cleaned_text=cleaned,
                        detected_section=current_section,
                        char_count=len(cleaned),
                        has_tables=has_tables,
                    )
                )
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document bytes: {str(e)}")

        return ExtractedDocument(
            file_name=file_name,
            file_hash_sha256=doc_hash,
            pages=pages,
            file_size_bytes=len(pdf_bytes),
        )

    def parse_structured_pages(self, pages_data: List[Dict[str, Any]], file_name: str = "document.pdf") -> ExtractedDocument:
        """Parses pre-extracted page dictionary structures."""
        combined_text = "".join(p.get("text", "") for p in pages_data)
        doc_hash = self.compute_sha256(combined_text.encode("utf-8"))
        
        pages: List[ExtractedPage] = []
        current_section = "GENERAL_DISCLOSURE"
        
        for p in pages_data:
            p_num = p.get("page_number", len(pages) + 1)
            raw = p.get("text", "")
            cleaned = self.clean_text(raw)
            sec = p.get("section") or self.detect_section(cleaned, current_section)
            current_section = sec
            has_tbl = self._detect_tables(cleaned)
            
            pages.append(
                ExtractedPage(
                    page_number=p_num,
                    raw_text=raw,
                    cleaned_text=cleaned,
                    detected_section=sec,
                    char_count=len(cleaned),
                    has_tables=has_tbl,
                )
            )

        return ExtractedDocument(
            file_name=file_name,
            file_hash_sha256=doc_hash,
            pages=pages,
            file_size_bytes=len(combined_text.encode("utf-8")),
        )


DocumentParserEngine = AnnualReportParserEngine
