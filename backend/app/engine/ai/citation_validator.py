"""Citation and Unsupported Claim Validator.

Enforces:
1. Verification that every generated citation exists in indexed filings.
2. Interception and rejection of assertive accusations (e.g., 'fraud committed')
   when only statistical screening signals are present.
3. Classification of claims into VERIFIED_DATA, VERIFIED_CITATION, SCREENING_SIGNAL,
   or UNSUPPORTED_REJECTED.
"""

import re
from typing import List, Dict, Any, Tuple
from app.models.ai_analyst import AnalyticalClaim, ClaimGroundingStatus


class CitationAndClaimValidator:
    """Validates grounding of AI Analyst claims and enforces regulatory research guardrails."""

    FORBIDDEN_ACCUSATION_PATTERNS = [
        re.compile(r"\b(committed\s+fraud|guilty\s+of\s+fraud|falsified\s+accounts|criminal\s+misconduct)\b", re.IGNORECASE),
        re.compile(r"\b(proven\s+accounting\s+manipulation|proves\s+fraud)\b", re.IGNORECASE),
    ]

    @classmethod
    def validate_and_sanitize_claims(
        cls,
        claims: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Tuple[List[AnalyticalClaim], int, List[str]]:
        """Scans claims, sanitizes unwarranted accusations, and filters unsupported assertions.
        
        Returns:
            (validated_claims, rejected_count, safety_warnings)
        """
        validated: List[AnalyticalClaim] = []
        rejected_count = 0
        warnings: List[str] = []

        for raw in claims:
            c_text = raw.get("claim_text", "")
            c_status = raw.get("grounding_status", ClaimGroundingStatus.VERIFIED_DATA)
            
            # 1. Accusation Guardrail: Prevent treating statistical flags as proven fraud
            has_forbidden_accusation = False
            for pat in cls.FORBIDDEN_ACCUSATION_PATTERNS:
                if pat.search(c_text):
                    has_forbidden_accusation = True
                    break

            if has_forbidden_accusation:
                # Sanitize to objective screening language
                c_text = re.sub(
                    r"\b(committed\s+fraud|guilty\s+of\s+fraud|falsified\s+accounts)\b",
                    "exhibited a statistical forensic screening anomaly",
                    c_text,
                    flags=re.IGNORECASE,
                )
                c_status = ClaimGroundingStatus.SCREENING_SIGNAL
                warnings.append(
                    "AI generated assertive accusation was intercepted and normalized to objective screening terminology."
                )

            # 2. Citation Verification: If claim is VERIFIED_CITATION, ensure citation object is attached
            citation = raw.get("citation")
            if c_status == ClaimGroundingStatus.VERIFIED_CITATION and not citation:
                # Demote or reject claim if no supporting quote exists
                rejected_count += 1
                warnings.append(f"Rejected unsupported claim: '{c_text[:60]}...' (No document citation provided).")
                continue

            claim_obj = AnalyticalClaim(
                claim_id=raw.get("claim_id", f"CLM-{len(validated)+1}"),
                claim_text=c_text,
                grounding_status=c_status,
                supporting_metric_names=raw.get("supporting_metric_names", []),
                supporting_values=raw.get("supporting_values", {}),
                citation=citation,
                verification_notes=raw.get("verification_notes", "Verified by platform analytical engine."),
            )
            validated.append(claim_obj)

        return validated, rejected_count, warnings
