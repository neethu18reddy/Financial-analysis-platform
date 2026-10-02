"""Provenance Tracker recording field-level lineage and traceability."""

from typing import List, Dict, Any, Optional
from app.models.provenance import DataProvenance
from app.models.source import SourceDocument


class ProvenanceTracker:
    """Builds and records auditable lineage records linking database fields to raw source filing artifacts."""

    @staticmethod
    def create_field_provenance(
        source_doc: SourceDocument,
        entity_type: str,
        entity_id: int,
        field_name: str,
        reported_label: str,
        reported_value_raw: str,
        reported_unit: str,
        normalized_value: float,
        normalized_unit: str = "CRORES",
        currency: str = "INR",
        page_number: Optional[int] = None,
        table_reference: Optional[str] = None,
        note_reference: Optional[str] = None,
        extraction_method: str = "STATUTORY_AUDITED_FIXTURE",
        confidence_score: float = 1.0,
        transformation_applied: Optional[str] = None
    ) -> DataProvenance:
        """Create a single verified field provenance record."""
        return DataProvenance(
            source_document_id=source_doc.id,
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            reported_label=reported_label,
            reported_value_raw=str(reported_value_raw),
            reported_unit=reported_unit,
            reported_currency=currency,
            normalized_value=normalized_value,
            normalized_unit=normalized_unit,
            page_number=page_number,
            table_reference=table_reference,
            note_reference=note_reference,
            extraction_method=extraction_method,
            confidence_score=confidence_score,
            transformation_applied=transformation_applied or f"Normalized to {normalized_unit} from {reported_unit}"
        )
