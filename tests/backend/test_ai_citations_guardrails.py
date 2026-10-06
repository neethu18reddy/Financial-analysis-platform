"""Tests for Citation Verification and Unsupported Accusation Guardrails."""

import pytest
from app.engine.ai.citation_validator import CitationAndClaimValidator
from app.models.ai_analyst import ClaimGroundingStatus


def test_accusation_interception_and_normalization():
    """Verify that assertive claims like 'committed fraud' are sanitized to screening indicators."""
    validator = CitationAndClaimValidator()
    
    raw_claims = [
        {
            "claim_id": "CLM-001",
            "claim_text": "The company committed fraud according to the Beneish model.",
            "grounding_status": ClaimGroundingStatus.SCREENING_SIGNAL,
            "supporting_metric_names": ["beneish_m_score"],
            "supporting_values": {"m_score": -1.5},
            "citation": None,
        }
    ]

    validated, rejected_count, warnings = validator.validate_and_sanitize_claims(
        claims=raw_claims,
        context={},
    )

    assert len(validated) == 1
    assert "committed fraud" not in validated[0].claim_text.lower()
    assert "statistical forensic screening anomaly" in validated[0].claim_text
    assert len(warnings) >= 1
    assert "intercepted" in warnings[0].lower()


def test_unsupported_citation_rejection():
    """Verify claims claiming to be VERIFIED_CITATION without an attached citation are rejected."""
    validator = CitationAndClaimValidator()

    raw_claims = [
        {
            "claim_id": "CLM-002",
            "claim_text": "Management stated they will enter aerospace manufacturing.",
            "grounding_status": ClaimGroundingStatus.VERIFIED_CITATION,
            "supporting_metric_names": [],
            "supporting_values": {},
            "citation": None,  # Missing citation
        }
    ]

    validated, rejected_count, warnings = validator.validate_and_sanitize_claims(
        claims=raw_claims,
        context={},
    )

    assert len(validated) == 0
    assert rejected_count == 1
    assert "rejected" in warnings[0].lower()
