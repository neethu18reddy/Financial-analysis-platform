"""Document Management and Ingestion Service (Async SQLAlchemy 2.0).

Orchestrates:
1. Parsing PDF / structured annual reports into physical page records.
2. Extracting statutory sections and tables.
3. Financial semantic chunking with overlapping windows.
4. Deterministic vector embedding and persistence.
5. Seeding initial Indian Annual Reports into SQLite & Vector Store.
"""

import json
import logging
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

try:
    from app.models.document_intelligence import (
        DocumentRecord,
        DocumentPageRecord,
        DocumentChunkRecord,
        DocumentType,
        DocumentProcessingStatus,
        DocumentMetadataDTO,
        DocumentDetailDTO,
        DocumentPageDTO,
        IngestionUploadResponse,
    )
    from app.engine.rag.parser import AnnualReportParserEngine, ExtractedDocument
    from app.engine.rag.chunker import FinancialChunkerEngine
    from app.engine.rag.embeddings import get_default_embedding_provider
    from app.engine.rag.vector_store import get_global_vector_store, VectorStoreItem
    from app.engine.rag.seed_fixtures import SEED_ANNUAL_REPORTS
except ImportError:
    from backend.app.models.document_intelligence import (
        DocumentRecord,
        DocumentPageRecord,
        DocumentChunkRecord,
        DocumentType,
        DocumentProcessingStatus,
        DocumentMetadataDTO,
        DocumentDetailDTO,
        DocumentPageDTO,
        IngestionUploadResponse,
    )
    from backend.app.engine.rag.parser import AnnualReportParserEngine, ExtractedDocument
    from backend.app.engine.rag.chunker import FinancialChunkerEngine
    from backend.app.engine.rag.embeddings import get_default_embedding_provider
    from backend.app.engine.rag.vector_store import get_global_vector_store, VectorStoreItem
    from backend.app.engine.rag.seed_fixtures import SEED_ANNUAL_REPORTS

logger = logging.getLogger(__name__)


class DocumentService:
    """Service handling document lifecycle, ingestion, and page retrieval."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.parser = AnnualReportParserEngine()
        self.chunker = FinancialChunkerEngine()
        self.embedding_provider = get_default_embedding_provider()
        self.vector_store = get_global_vector_store()

    async def get_document_by_id(self, document_id: int) -> Optional[DocumentRecord]:
        """Fetch document record by primary ID."""
        stmt = select(DocumentRecord).where(DocumentRecord.id == document_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_documents(self, ticker: Optional[str] = None) -> List[DocumentMetadataDTO]:
        """List all indexed documents, optionally filtered by ticker."""
        await self.ensure_seed_documents()
        
        stmt = select(DocumentRecord)
        if ticker:
            stmt = stmt.where(DocumentRecord.ticker == ticker.upper())
        stmt = stmt.order_by(DocumentRecord.fiscal_year.desc(), DocumentRecord.ticker.asc())
        
        res = await self.db.execute(stmt)
        docs = res.scalars().all()
        
        results = []
        for d in docs:
            c_stmt = select(func.count(DocumentChunkRecord.id)).where(DocumentChunkRecord.document_id == d.id)
            c_res = await self.db.execute(c_stmt)
            chunk_count = c_res.scalar() or 0
            
            results.append(
                DocumentMetadataDTO(
                    id=d.id,
                    ticker=d.ticker,
                    fiscal_year=d.fiscal_year,
                    document_type=d.document_type,
                    title=d.title,
                    file_name=d.file_name,
                    source_url=d.source_url,
                    file_hash_sha256=d.file_hash_sha256,
                    page_count=d.page_count,
                    file_size_bytes=d.file_size_bytes,
                    extraction_method=d.extraction_method,
                    processing_status=d.processing_status,
                    error_message=d.error_message,
                    retrieval_date=d.retrieval_date.isoformat() if d.retrieval_date else "",
                    total_chunks=chunk_count,
                )
            )
        return results

    async def get_document_detail(self, document_id: int) -> Optional[DocumentDetailDTO]:
        """Get document details with all pages and detected sections."""
        doc = await self.get_document_by_id(document_id)
        if not doc:
            return None
        
        p_stmt = (
            select(DocumentPageRecord)
            .where(DocumentPageRecord.document_id == document_id)
            .order_by(DocumentPageRecord.page_number.asc())
        )
        p_res = await self.db.execute(p_stmt)
        pages_db = p_res.scalars().all()
        
        c_stmt = select(func.count(DocumentChunkRecord.id)).where(DocumentChunkRecord.document_id == doc.id)
        c_res = await self.db.execute(c_stmt)
        chunk_count = c_res.scalar() or 0
        
        sections = list(dict.fromkeys([p.detected_section for p in pages_db if p.detected_section]))
        page_dtos = [
            DocumentPageDTO(
                page_number=p.page_number,
                detected_section=p.detected_section,
                char_count=p.char_count,
                has_tables=p.has_tables,
                text=p.raw_text,
            )
            for p in pages_db
        ]

        return DocumentDetailDTO(
            id=doc.id,
            ticker=doc.ticker,
            fiscal_year=doc.fiscal_year,
            document_type=doc.document_type,
            title=doc.title,
            file_name=doc.file_name,
            source_url=doc.source_url,
            file_hash_sha256=doc.file_hash_sha256,
            page_count=doc.page_count,
            file_size_bytes=doc.file_size_bytes,
            extraction_method=doc.extraction_method,
            processing_status=doc.processing_status,
            error_message=doc.error_message,
            retrieval_date=doc.retrieval_date.isoformat() if doc.retrieval_date else "",
            total_chunks=chunk_count,
            sections_detected=sections,
            pages=page_dtos,
        )

    async def get_page_text(self, document_id: int, page_number: int) -> Optional[DocumentPageDTO]:
        """Fetch exact page text."""
        stmt = select(DocumentPageRecord).where(
            DocumentPageRecord.document_id == document_id,
            DocumentPageRecord.page_number == page_number,
        )
        res = await self.db.execute(stmt)
        page = res.scalar_one_or_none()
        if not page:
            return None
        return DocumentPageDTO(
            page_number=page.page_number,
            detected_section=page.detected_section,
            char_count=page.char_count,
            has_tables=page.has_tables,
            text=page.raw_text,
        )

    async def ingest_extracted_document(
        self,
        extracted: ExtractedDocument,
        ticker: str,
        fiscal_year: int,
        title: str,
        document_type: DocumentType = DocumentType.ANNUAL_REPORT,
        source_url: Optional[str] = None,
    ) -> IngestionUploadResponse:
        """Ingest extracted document pages, chunk them, embed them, and index in DB & Vector Store."""
        # Check duplicate hash
        stmt = select(DocumentRecord).where(DocumentRecord.file_hash_sha256 == extracted.file_hash_sha256)
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()
        
        if existing:
            await self._sync_document_chunks_to_vector_store(existing.id)
            c_stmt = select(func.count(DocumentChunkRecord.id)).where(DocumentChunkRecord.document_id == existing.id)
            c_res = await self.db.execute(c_stmt)
            chunk_count = c_res.scalar() or 0
            sections = await self.get_detected_sections(existing.id)
            return IngestionUploadResponse(
                document_id=existing.id,
                ticker=existing.ticker,
                fiscal_year=existing.fiscal_year,
                file_name=existing.file_name,
                file_hash_sha256=existing.file_hash_sha256,
                page_count=existing.page_count,
                total_chunks_indexed=chunk_count,
                sections_detected=sections,
                processing_status=existing.processing_status,
                message="Document with identical SHA-256 hash already indexed.",
            )

        # 1. Create Document Record
        doc_record = DocumentRecord(
            ticker=ticker.upper(),
            fiscal_year=fiscal_year,
            document_type=document_type,
            title=title,
            file_name=extracted.file_name,
            source_url=source_url,
            file_hash_sha256=extracted.file_hash_sha256,
            page_count=extracted.page_count,
            file_size_bytes=extracted.file_size_bytes,
            extraction_method="PYPDF_STRUCTURED",
            processing_status=DocumentProcessingStatus.PARSING,
        )
        self.db.add(doc_record)
        await self.db.flush()

        # 2. Add Page Records
        page_records: List[DocumentPageRecord] = []
        for page in extracted.pages:
            p_rec = DocumentPageRecord(
                document_id=doc_record.id,
                page_number=page.page_number,
                detected_section=page.detected_section,
                raw_text=page.raw_text,
                cleaned_text=page.cleaned_text,
                char_count=page.char_count,
                has_tables=page.has_tables,
            )
            self.db.add(p_rec)
            page_records.append(p_rec)
        await self.db.flush()

        # 3. Semantic Chunking
        doc_record.processing_status = DocumentProcessingStatus.CHUNKING
        chunks = self.chunker.chunk_pages(
            document_id=doc_record.id,
            pages=extracted.pages,
            document_hash=doc_record.file_hash_sha256,
        )

        # 4. Generate Embeddings & Index
        doc_record.processing_status = DocumentProcessingStatus.INDEXING
        vector_items: List[VectorStoreItem] = []

        for ch in chunks:
            matched_page = next((p for p in page_records if p.page_number == ch.page_number), page_records[0])
            embedding = self.embedding_provider.embed_text(ch.text)

            chunk_record = DocumentChunkRecord(
                document_id=doc_record.id,
                page_id=matched_page.id,
                chunk_index=ch.chunk_index,
                page_number=ch.page_number,
                section_title=ch.section_title,
                chunk_text=ch.text,
                token_count=ch.token_count,
                embedding_json=json.dumps(embedding),
                metadata_json=json.dumps({
                    "provenance_hash": ch.provenance_hash,
                    "char_start": ch.char_start,
                    "char_end": ch.char_end,
                }),
            )
            self.db.add(chunk_record)
            await self.db.flush()

            vector_item = VectorStoreItem(
                chunk_id=chunk_record.id,
                document_id=doc_record.id,
                document_title=doc_record.title,
                ticker=doc_record.ticker,
                fiscal_year=doc_record.fiscal_year,
                page_number=ch.page_number,
                section_title=ch.section_title,
                chunk_text=ch.text,
                embedding=embedding,
                provenance_hash=ch.provenance_hash,
                source_url=source_url,
            )
            vector_items.append(vector_item)

        self.vector_store.add_items(vector_items)

        # 5. Mark Completed
        doc_record.processing_status = DocumentProcessingStatus.COMPLETED
        await self.db.commit()

        sections = await self.get_detected_sections(doc_record.id)
        return IngestionUploadResponse(
            document_id=doc_record.id,
            ticker=doc_record.ticker,
            fiscal_year=doc_record.fiscal_year,
            file_name=doc_record.file_name,
            file_hash_sha256=doc_record.file_hash_sha256,
            page_count=doc_record.page_count,
            total_chunks_indexed=len(chunks),
            sections_detected=sections,
            processing_status=DocumentProcessingStatus.COMPLETED,
            message="Document successfully parsed, chunked, embedded, and indexed.",
        )

    async def ingest_pdf_bytes(
        self,
        pdf_bytes: bytes,
        file_name: str,
        ticker: str,
        fiscal_year: int,
        title: Optional[str] = None,
        source_url: Optional[str] = None,
    ) -> IngestionUploadResponse:
        """Parse raw PDF bytes and run full ingestion pipeline."""
        extracted = self.parser.parse_pdf_bytes(pdf_bytes=pdf_bytes, file_name=file_name)
        doc_title = title or f"{ticker.upper()} Annual Report FY{fiscal_year}"
        return await self.ingest_extracted_document(
            extracted=extracted,
            ticker=ticker,
            fiscal_year=fiscal_year,
            title=doc_title,
            document_type=DocumentType.ANNUAL_REPORT,
            source_url=source_url,
        )

    async def get_detected_sections(self, document_id: int) -> List[str]:
        """Fetch distinct detected section names for a document."""
        stmt = select(DocumentPageRecord).where(DocumentPageRecord.document_id == document_id)
        res = await self.db.execute(stmt)
        pages = res.scalars().all()
        return list(dict.fromkeys([p.detected_section for p in pages if p.detected_section]))

    async def ensure_seed_documents(self) -> None:
        """Seed pre-packaged statutory annual report fixtures if none exist in the database."""
        stmt = select(func.count(DocumentRecord.id))
        res = await self.db.execute(stmt)
        count = res.scalar() or 0
        
        if count > 0:
            if self.vector_store.count() == 0:
                await self._load_all_chunks_into_vector_store()
            return

        logger.info("Seeding statutory Indian Annual Report filings...")
        for fixture in SEED_ANNUAL_REPORTS:
            extracted = self.parser.parse_structured_pages(
                pages_data=fixture["pages"],
                file_name=fixture["file_name"],
            )
            await self.ingest_extracted_document(
                extracted=extracted,
                ticker=fixture["ticker"],
                fiscal_year=fixture["fiscal_year"],
                title=fixture["title"],
                document_type=DocumentType.ANNUAL_REPORT,
                source_url=fixture.get("source_url"),
            )

    async def _sync_document_chunks_to_vector_store(self, document_id: int) -> None:
        """Load chunks of a specific document into vector store if missing."""
        doc = await self.get_document_by_id(document_id)
        if not doc:
            return
        
        stmt = select(DocumentChunkRecord).where(DocumentChunkRecord.document_id == document_id)
        res = await self.db.execute(stmt)
        chunks = res.scalars().all()
        
        vector_items = []
        for ch in chunks:
            emb = json.loads(ch.embedding_json) if ch.embedding_json else self.embedding_provider.embed_text(ch.chunk_text)
            meta = json.loads(ch.metadata_json) if ch.metadata_json else {}
            prov_hash = meta.get("provenance_hash", "")
            vector_items.append(
                VectorStoreItem(
                    chunk_id=ch.id,
                    document_id=doc.id,
                    document_title=doc.title,
                    ticker=doc.ticker,
                    fiscal_year=doc.fiscal_year,
                    page_number=ch.page_number,
                    section_title=ch.section_title,
                    chunk_text=ch.chunk_text,
                    embedding=emb,
                    provenance_hash=prov_hash,
                    source_url=doc.source_url,
                )
            )
        self.vector_store.add_items(vector_items)

    async def _load_all_chunks_into_vector_store(self) -> None:
        """Reload all DB chunks into in-memory vector store."""
        stmt = select(DocumentRecord)
        res = await self.db.execute(stmt)
        docs = res.scalars().all()
        for d in docs:
            await self._sync_document_chunks_to_vector_store(d.id)
