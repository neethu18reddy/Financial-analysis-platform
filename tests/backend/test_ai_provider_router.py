"""Tests for AI LLM Provider and Question Router."""

import pytest
from app.engine.ai.llm_provider import DeterministicFinancialLLMProvider
from app.engine.ai.question_router import FinancialQuestionRouter
from app.models.ai_analyst import QuestionIntent, ClaimGroundingStatus


@pytest.mark.asyncio
async def test_deterministic_llm_provider_reasoning():
    """Verify deterministic financial reasoning generation and claim extraction."""
    provider = DeterministicFinancialLLMProvider()
    context = {
        "ticker": "RELIANCE",
        "company_name": "Reliance Industries Limited",
        "intent": QuestionIntent.FINANCIAL_PERFORMANCE,
        "financial_summary": {
            "revenue_crores": 1000122.0,
            "pat_crores": 79020.0,
            "ebitda_crores": 178677.0,
            "cfo_crores": 140000.0,
            "capex_crores": 131769.0,
            "fcf_crores": 8231.0,
        },
        "fundamental_metrics": {
            "roce_pct": 12.8,
            "ebitda_margin_pct": 17.86,
            "pat_margin_pct": 7.9,
            "fcf_conversion_pct": 10.4,
        },
        "forensic_scorecard": {
            "piotroski_f_score": 7,
            "beneish_m_score": -2.65,
            "beneish_manipulation_flag": False,
        },
        "valuation_summary": {
            "composite_central_fair_value": 3150.0,
            "current_market_price": 2980.0,
            "composite_upside_downside_pct": 5.7,
        },
        "retrieved_citations": [
            {
                "document_title": "RIL Annual Report FY24",
                "page_number": 2,
                "section_title": "DIRECTORS_REPORT",
                "exact_quote": "Capex was ₹1,31,769 crore directed to 5G rollout.",
                "relevance_score": 0.89,
                "provenance_hash": "hash_123",
            }
        ],
    }

    resp = await provider.generate_structured(prompt="Analyze financial performance and capex", context=context)

    assert resp["ticker"] == "RELIANCE"
    assert "1,000,122.00 Cr" in resp["executive_summary"]
    assert len(resp["key_claims"]) >= 3
    assert resp["confidence_score"] >= 0.90
    assert any(
        (c["grounding_status"] == ClaimGroundingStatus.VERIFIED_CITATION or
         getattr(c["grounding_status"], "value", None) == "VERIFIED_CITATION")
        for c in resp["key_claims"]
    )


def test_question_router_intents():
    """Verify question router correctly identifies analytical domain and activates subsystems."""
    router = FinancialQuestionRouter()

    # 1. ROCE question
    plan1 = router.route_query("Why did ROCE decline over the past three years?")
    assert plan1["intent"] == QuestionIntent.PROFITABILITY_ROCE
    assert plan1["needs_fundamentals"] is True

    # 2. Forensic question
    plan2 = router.route_query("Are there any Beneish M-score or Sloan accrual manipulation flags?")
    assert plan2["intent"] == QuestionIntent.FORENSIC_INTEGRITY
    assert plan2["needs_forensics"] is True

    # 3. Valuation question
    plan3 = router.route_query("What is the estimated fair value and DCF terminal growth rate?")
    assert plan3["intent"] == QuestionIntent.VALUATION_DRIVERS
    assert plan3["needs_valuation"] is True

    # 4. Said vs Did question
    plan4 = router.route_query("What was management's guidance track record on buyback delivery?")
    assert plan4["intent"] == QuestionIntent.SAID_VS_DID
    assert plan4["needs_said_vs_did"] is True
