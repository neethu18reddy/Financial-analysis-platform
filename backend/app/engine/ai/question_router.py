"""Financial Question Router Engine.

Analyzes natural language financial queries to:
1. Classify analytical intent (e.g., ROCE driver, cash quality, forensic check, valuation, management guidance).
2. Determine required analytical pipelines (Fundamentals, Forensics, Valuation, Annual Report RAG, Said vs Did).
3. Generate optimized targeted RAG search queries for filing evidence extraction.
"""

import re
from typing import Dict, Any, List, Tuple
from app.models.ai_analyst import QuestionIntent


class FinancialQuestionRouter:
    """Classifies user queries and routes them to appropriate data and calculation subsystems."""

    INTENT_KEYWORDS: List[Tuple[QuestionIntent, List[str]]] = [
        (
            QuestionIntent.SAID_VS_DID,
            ["said vs did", "promise", "guidance track record", "guidance vs actual", "management delivery", "commitments", "buyback completed", "guidance met"],
        ),
        (
            QuestionIntent.FORENSIC_INTEGRITY,
            ["forensic", "beneish", "m-score", "manipulation", "fraud", "accounting quality", "piotroski", "f-score", "altman", "z-score", "accrual", "sloan", "channel stuffing", "auditor qualification"],
        ),
        (
            QuestionIntent.VALUATION_DRIVERS,
            ["valuation", "fair value", "dcf", "reverse dcf", "target price", "undervalued", "overvalued", "wacc", "terminal growth", "multiple", "pe ratio", "ev/ebitda", "implied growth"],
        ),
        (
            QuestionIntent.WORKING_CAPITAL_CASH_FLOW,
            ["cash flow", "fcf", "free cash", "working capital", "receivables", "debtor days", "inventory days", "cash conversion", "operating cash"],
        ),
        (
            QuestionIntent.PROFITABILITY_ROCE,
            ["roce", "roe", "dupont", "margin", "ebitda margin", "pat margin", "operating margin", "asset turnover", "financial leverage", "why did margin", "why did roce"],
        ),
        (
            QuestionIntent.MANAGEMENT_COMMENTARY,
            ["what did management say", "commentary", "annual report says", "capex plans", "capacity expansion", "5g rollout", "digital services", "future outlook", "strategy"],
        ),
        (
            QuestionIntent.RISK_GOVERNANCE,
            ["contingent liability", "guarantee", "related party", "tax dispute", "legal dispute", "auditor matter", "governance", "independent director", "remuneration"],
        ),
        (
            QuestionIntent.FINANCIAL_PERFORMANCE,
            ["revenue", "sales", "net profit", "pat", "ebitda", "growth", "performance", "how is company performing", "cagr"],
        ),
    ]

    def route_query(self, question: str) -> Dict[str, Any]:
        """Classifies intent and determines data subsystem execution plan."""
        q_lower = question.lower()
        classified_intent = QuestionIntent.GENERAL_RESEARCH

        for intent, keywords in self.INTENT_KEYWORDS:
            if any(kw in q_lower for kw in keywords):
                classified_intent = intent
                break

        # Subsystem activation flags based on intent
        needs_fundamentals = True
        needs_forensics = classified_intent in [
            QuestionIntent.FORENSIC_INTEGRITY,
            QuestionIntent.RISK_GOVERNANCE,
            QuestionIntent.GENERAL_RESEARCH,
        ]
        needs_valuation = classified_intent in [
            QuestionIntent.VALUATION_DRIVERS,
            QuestionIntent.GENERAL_RESEARCH,
        ]
        needs_rag = classified_intent in [
            QuestionIntent.MANAGEMENT_COMMENTARY,
            QuestionIntent.RISK_GOVERNANCE,
            QuestionIntent.SAID_VS_DID,
            QuestionIntent.FORENSIC_INTEGRITY,
            QuestionIntent.GENERAL_RESEARCH,
        ]
        needs_said_vs_did = classified_intent in [
            QuestionIntent.SAID_VS_DID,
            QuestionIntent.MANAGEMENT_COMMENTARY,
            QuestionIntent.GENERAL_RESEARCH,
        ]

        # Formulate optimized RAG semantic search query
        rag_search_query = self._generate_rag_query(question, classified_intent)

        return {
            "intent": classified_intent,
            "needs_fundamentals": needs_fundamentals,
            "needs_forensics": needs_forensics,
            "needs_valuation": needs_valuation,
            "needs_rag": needs_rag,
            "needs_said_vs_did": needs_said_vs_did,
            "rag_search_query": rag_search_query,
        }

    def _generate_rag_query(self, question: str, intent: QuestionIntent) -> str:
        """Constructs focused keyword queries for document similarity search."""
        if intent == QuestionIntent.MANAGEMENT_COMMENTARY:
            return f"management discussion strategy capex outlook {question}"
        elif intent == QuestionIntent.FORENSIC_INTEGRITY:
            return f"auditor report key audit matters internal financial controls {question}"
        elif intent == QuestionIntent.RISK_GOVERNANCE:
            return f"contingent liabilities related party commitments guarantees {question}"
        elif intent == QuestionIntent.SAID_VS_DID:
            return f"directors report capex buyback capacity expansion {question}"
        return question
