"""Tests for Document Parser and Financial Chunker Engines."""

import pytest
from app.engine.rag.parser import AnnualReportParserEngine, ExtractedPage
from app.engine.rag.chunker import FinancialChunkerEngine


def test_parser_structured_pages_and_hashing():
    """Test structured page parsing, section identification, and SHA-256 identity."""
    parser = AnnualReportParserEngine()
    pages_data = [
        {
            "page_number": 1,
            "section": "GENERAL_CORPORATE_INFORMATION",
            "text": "Reliance Industries Limited Integrated Annual Report 2023-24. Consolidated revenue ₹10,00,122 crore."
        },
        {
            "page_number": 2,
            "section": None,
            "text": "DIRECTORS' REPORT TO THE SHAREHOLDERS\nCapital expenditure was ₹1,31,769 crore during the year."
        },
        {
            "page_number": 3,
            "section": None,
            "text": "INDEPENDENT AUDITOR'S REPORT\nIn our opinion, the consolidated financial statements give a true and fair view."
        }
    ]

    extracted = parser.parse_structured_pages(pages_data, "sample_ril_report.pdf")
    
    assert extracted.page_count == 3
    assert len(extracted.file_hash_sha256) == 64
    assert extracted.pages[0].page_number == 1
    assert extracted.pages[0].detected_section == "GENERAL_CORPORATE_INFORMATION"
    assert extracted.pages[1].detected_section == "DIRECTORS_REPORT"
    assert extracted.pages[2].detected_section == "INDEPENDENT_AUDITORS_REPORT"


def test_parser_table_detection():
    """Test heuristic table detection on formatted financial tabular text."""
    parser = AnnualReportParserEngine()
    tabular_text = """
    Particulars          FY 2023-24    FY 2022-23    YoY Growth (%)
    Segment Revenue       1,00,122        89,200          12.2%
    Segment EBITDA          18,500        15,200          21.7%
    Total Assets          4,50,000      3,90,000          15.4%
    """
    page = ExtractedPage(
        page_number=1,
        raw_text=tabular_text,
        cleaned_text=tabular_text.strip(),
        detected_section="CONSOLIDATED_STATEMENT_OF_PROFIT_AND_LOSS",
        char_count=len(tabular_text),
        has_tables=parser._detect_tables(tabular_text)
    )
    assert page.has_tables is True


def test_financial_chunker_window_and_overlap():
    """Test semantic chunking with overlapping windows and provenance retention."""
    chunker = FinancialChunkerEngine(target_chunk_words=50, overlap_words=10)
    
    # 150-word sample text
    sample_text = " ".join([f"Word_{i} discussing Indian financial performance and capex growth." for i in range(25)])
    pages = [
        ExtractedPage(
            page_number=4,
            raw_text=sample_text,
            cleaned_text=sample_text,
            detected_section="MANAGEMENT_DISCUSSION_AND_ANALYSIS",
            char_count=len(sample_text),
            has_tables=False,
        )
    ]

    chunks = chunker.chunk_pages(document_id=101, pages=pages, document_hash="fake_hash_123456789")
    
    assert len(chunks) >= 2
    for idx, chunk in enumerate(chunks):
        assert chunk.chunk_index == idx
        assert chunk.page_number == 4
        assert chunk.section_title == "MANAGEMENT_DISCUSSION_AND_ANALYSIS"
        assert len(chunk.provenance_hash) == 64
        assert chunk.token_count > 0
        assert len(chunk.text) > 0
