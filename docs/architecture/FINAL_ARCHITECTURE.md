# Final System Architecture: AI-Powered Financial Intelligence Platform

## 1. Architectural Overview

The **Financial Decision Intelligence Platform for Indian Equities (NSE/BSE)** is a multi-tier, verifiable, and deterministic financial analysis and AI reasoning engine. Designed from the ground up for strict mathematical correctness, regulatory compliance (SEBI Research Analyst Regulations), and zero-hallucination guarantees, the system couples deterministic accounting engines with a verifiable retrieval-augmented AI analyst pipeline.

```mermaid
flowchart TD
    subgraph Data Layer [Layer 1: Statutory Data & Ingestion]
        NSE[NSE / BSE Filings] --> Ingestion[Ingestion Engine]
        PDF[Annual Reports PDF] --> DocParser[Document Parser & Hashing]
        DB[(SQLite / PostgreSQL Relational DB)]
        VecStore[(Vector Embedding Store)]
    end

    subgraph Analytical Core [Layer 2: Deterministic Analytical Engines]
        Validator[Financial Validator & Balance Sheet Reconciliation]
        Fundamental[Fundamental Engine: DuPont, Margins, Working Capital]
        Forensics[Forensic Engine: Beneish M, Piotroski F, Altman Z]
        Valuation[Valuation Engine: DCF, Reverse DCF, Multiples, Scenarios]
        RAG[Document Intelligence & Vector Retrieval Engine]
    end

    subgraph AI Analyst Pipeline [Layer 3: AI Intelligence & Verification Layer]
        Router[Financial Question Router]
        ContextBuilder[Structured Context Builder with PIT Guardrails]
        LLM[Deterministic / Pluggable LLM Provider]
        ValidatorAI[Citation & Claim Grounding Validator]
        SaidDid[Management Said-vs-Did Tracker]
        Watchlist[Watchlist & Anomaly Alert Engine]
        ReportGen[14-Section Institutional Report Generator]
    end

    subgraph Presentation [Layer 4: Interactive Frontend Workspace]
        UI[React 19 + TypeScript + Vite + Tailwind UI]
    end

    Ingestion --> DB
    DocParser --> VecStore
    DB --> Validator
    DB --> Fundamental
    DB --> Forensics
    DB --> Valuation
    VecStore --> RAG

    Router --> ContextBuilder
    Fundamental --> ContextBuilder
    Forensics --> ContextBuilder
    Valuation --> ContextBuilder
    RAG --> ContextBuilder

    ContextBuilder --> LLM
    LLM --> ValidatorAI
    ValidatorAI --> UI
    SaidDid --> UI
    Watchlist --> UI
    ReportGen --> UI
```

---

## 2. Core Architectural Principles

1. **Deterministic Foundations**:
   - Zero LLM math: All ROCE, DuPont 5-step, Beneish M-Score, Piotroski F-Score, Altman Z-Score, WACC, DCF enterprise values, and CAGRs are calculated via deterministic Python algorithms with 100% test coverage.
2. **Point-in-Time (PIT) Temporal Guardrails**:
   - Historical backtesting and simulation tools rigorously filter out any financial disclosure or annual report filing published after the chosen historical cut-off date (`as_of_year`), preventing lookahead bias.
3. **Mandatory Citation Grounding & Accusation Interception**:
   - The AI reasoning layer extracts granular analytical claims and validates them against retrieved source passages.
   - Defamatory or unsupported assertions (e.g., claiming a company "committed fraud" based solely on a statistical screening flag) are sanitized into objective analytical language ("statistical screening flag warrants investigation").
4. **Institutional Reporting & Watchlists**:
   - End-to-end 14-section equity research report synthesis.
   - Low-noise alert triggers for operating margin shifts, working capital spikes, and credit health transitions.
