"""Document Intelligence and Annual Report API Endpoints.

Provides endpoints for:
- Listing ingested statutory documents / annual reports
- Fetching document structure, detected sections, and page text
- Uploading and indexing raw annual report PDFs
- Executing semantic vector retrieval with page-level verifiable citations
- Inspecting statutory Indian annual report sections taxonomy
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from app.db.session import get_db
    from app.models.document_intelligence import (
        DocumentMetadataDTO,
        DocumentDetailDTO,
        DocumentPageDTO,
        DocumentRetrievalQuery,
        DocumentRetrievalResponse,
        IngestionUploadResponse,
    )
    from app.engine.rag.document_service import DocumentService
    from app.engine.rag.retrieval_service import RetrievalService
    from app.engine.rag.base import INDIAN_ANNUAL_REPORT_SECTIONS, RAG_METHODOLOGY_VERSION
except ImportError:
    from backend.app.db.session import get_db
    from backend.app.models.document_intelligence import (
        DocumentMetadataDTO,
        DocumentDetailDTO,
        DocumentPageDTO,
        DocumentRetrievalQuery,
        DocumentRetrievalResponse,
        IngestionUploadResponse,
    )
    from backend.app.engine.rag.document_service import DocumentService
    from backend.app.engine.rag.retrieval_service import RetrievalService
    from backend.app.engine.rag.base import INDIAN_ANNUAL_REPORT_SECTIONS, RAG_METHODOLOGY_VERSION

router = APIRouter(prefix="/documents", tags=["Document Intelligence & RAG"])


@router.get("", response_model=List[DocumentMetadataDTO])
async def list_documents(
    ticker: Optional[str] = Query(None, description="Filter documents by company ticker (e.g. RELIANCE, TCS)"),
    db: AsyncSession = Depends(get_db),
):
    """List all indexed annual reports and statutory filings."""
    service = DocumentService(db)
    return await service.list_documents(ticker=ticker)


@router.get("/sections/canonical", response_model=List[str])
async def get_canonical_sections():
    """List canonical Indian statutory annual report sections."""
    return INDIAN_ANNUAL_REPORT_SECTIONS


@router.get("/{document_id}", response_model=DocumentDetailDTO)
async def get_document_detail(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed document metadata, page list, and detected statutory sections."""
    service = DocumentService(db)
    detail = await service.get_document_detail(document_id=document_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found.",
        )
    return detail


@router.get("/{document_id}/pages/{page_number}", response_model=DocumentPageDTO)
async def get_document_page(
    document_id: int,
    page_number: int,
    db: AsyncSession = Depends(get_db),
):
    """Fetch exact extracted text and metadata for a physical page in an annual report."""
    service = DocumentService(db)
    page = await service.get_page_text(document_id=document_id, page_number=page_number)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page {page_number} for Document {document_id} not found.",
        )
    return page


@router.post("/search", response_model=DocumentRetrievalResponse)
async def search_documents(
    query: DocumentRetrievalQuery,
    db: AsyncSession = Depends(get_db),
):
    """Execute semantic retrieval across annual reports with exact verifiable citations."""
    service = RetrievalService(db)
    return await service.retrieve(query=query)


@router.post("/upload", response_model=IngestionUploadResponse)
async def upload_annual_report(
    file: UploadFile = File(...),
    ticker: str = Form(...),
    fiscal_year: int = Form(...),
    title: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Upload and process an annual report PDF through the complete extraction & vector indexing pipeline."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported for statutory filing ingestion.",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    service = DocumentService(db)
    try:
        response = await service.ingest_pdf_bytes(
            pdf_bytes=content,
            file_name=file.filename,
            ticker=ticker.upper().strip(),
            fiscal_year=fiscal_year,
            title=title.strip() if title else f"{ticker.upper()} Annual Report FY{fiscal_year}",
            source_url=source_url.strip() if source_url else None,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}",
        )
