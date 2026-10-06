import React, { useState, useEffect } from 'react';
import {
  Bot,
  ShieldCheck,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Sparkles,
  Bookmark,
  Plus,
  Trash2,
  ChevronRight,
  Target,
  FileCheck2,
} from 'lucide-react';
import { api } from '../services/api';
import {
  AIAnalystResponse,
  AnalyticalClaim,
  Company,
  CompanyResearchReport,
  EvidenceCitation,
  ManagementGuidanceItem,
  ManagementSaidVsDidResponse,
  PointInTimeAnalysisResponse,
  WatchlistAlert,
  WatchlistItemDTO,
} from '../types/api';

interface AIAnalystWorkspaceViewProps {
  companies: Company[];
  selectedCompany: Company | null;
  onSelectCompany: (company: Company) => void;
}

export const AIAnalystWorkspaceView: React.FC<AIAnalystWorkspaceViewProps> = ({
  companies,
  selectedCompany,
  onSelectCompany,
}) => {
  const [activeTab, setActiveTab] = useState<'analyst' | 'said_did' | 'pit' | 'report' | 'watchlist'>('analyst');

  // AI Analyst Chat State
  const [queryText, setQueryText] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [analystResponse, setAnalystResponse] = useState<AIAnalystResponse | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<EvidenceCitation | null>(null);

  // Said vs Did State
  const [saidVsDidData, setSaidVsDidData] = useState<ManagementSaidVsDidResponse | null>(null);
  const [loadingSaidDid, setLoadingSaidDid] = useState(false);

  // PIT Simulation State
  const [pitYear, setPitYear] = useState<number>(2023);
  const [pitQuestion, setPitQuestion] = useState('');
  const [pitResponse, setPitResponse] = useState<PointInTimeAnalysisResponse | null>(null);
  const [loadingPit, setLoadingPit] = useState(false);

  // Research Report State
  const [researchReport, setResearchReport] = useState<CompanyResearchReport | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);

  // Watchlist State
  const [watchlist, setWatchlist] = useState<WatchlistItemDTO[]>([]);
  const [loadingWatchlist, setLoadingWatchlist] = useState(false);
  const [newTicker, setNewTicker] = useState('');
  const [newNotes, setNewNotes] = useState('');

  // Suggested Prompts
  const suggestedPrompts = [
    'Why did ROCE change over the last 2 financial years?',
    'What are the primary capital expenditure and 5G network rollout drivers?',
    'Is cash flow from operations keeping pace with reported net profit?',
    'What are the key forensic screening signals and accounting anomalies?',
    'What assumptions drive the composite intrinsic fair value estimate?',
  ];

  // Load Said vs Did when company changes
  useEffect(() => {
    if (selectedCompany) {
      loadSaidVsDid(selectedCompany.ticker);
      if (activeTab === 'report') {
        loadResearchReport(selectedCompany.id);
      }
    }
  }, [selectedCompany]);

  // Load Watchlist on mount
  useEffect(() => {
    loadWatchlist();
  }, []);

  const handleRunQuery = async (promptToRun?: string) => {
    const q = promptToRun || queryText;
    if (!q.trim() || !selectedCompany) return;

    setIsQuerying(true);
    try {
      const res = await api.queryAIAnalyst({
        ticker: selectedCompany.ticker,
        question: q,
        include_annual_report_rag: true,
      });
      setAnalystResponse(res);
      if (res.supporting_citations && res.supporting_citations.length > 0) {
        setSelectedCitation(res.supporting_citations[0]);
      }
    } catch (err) {
      console.error('AI Query failed:', err);
    } finally {
      setIsQuerying(false);
    }
  };

  const loadSaidVsDid = async (ticker: string) => {
    setLoadingSaidDid(true);
    try {
      const data = await api.getSaidVsDid(ticker);
      setSaidVsDidData(data);
    } catch (err) {
      console.error('Failed to load said-vs-did:', err);
      setSaidVsDidData(null);
    } finally {
      setLoadingSaidDid(false);
    }
  };

  const handleRunPIT = async () => {
    if (!selectedCompany) return;
    setLoadingPit(true);
    try {
      const res = await api.runPointInTime({
        ticker: selectedCompany.ticker,
        as_of_year: pitYear,
        custom_question: pitQuestion.trim() || undefined,
      });
      setPitResponse(res);
    } catch (err) {
      console.error('PIT Simulation failed:', err);
    } finally {
      setLoadingPit(false);
    }
  };

  const loadResearchReport = async (companyId: number) => {
    setLoadingReport(true);
    try {
      const rep = await api.getResearchReport(companyId);
      setResearchReport(rep);
    } catch (err) {
      console.error('Failed to generate research report:', err);
    } finally {
      setLoadingReport(false);
    }
  };

  const loadWatchlist = async () => {
    setLoadingWatchlist(true);
    try {
      const items = await api.getWatchlist();
      setWatchlist(items);
    } catch (err) {
      console.error('Failed to load watchlist:', err);
    } finally {
      setLoadingWatchlist(false);
    }
  };

  const handleAddToWatchlist = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTicker.trim()) return;
    try {
      await api.addToWatchlist(newTicker.trim().toUpperCase(), newNotes.trim() || undefined);
      setNewTicker('');
      setNewNotes('');
      loadWatchlist();
    } catch (err) {
      console.error('Failed to add to watchlist:', err);
    }
  };

  const handleRemoveFromWatchlist = async (ticker: string) => {
    try {
      await api.removeFromWatchlist(ticker);
      loadWatchlist();
    } catch (err) {
      console.error('Failed to remove from watchlist:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Subsystem Description */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-xl border border-indigo-500/30 text-indigo-400">
            <Bot className="w-8 h-8" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-white tracking-tight">
                AI Analyst & Research Product
              </h1>
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full">
                Phase 7 Final Engine
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-1">
              Zero-hallucination institutional intelligence, verifiable statutory citations, historical Said-vs-Did scorecard, Point-in-Time temporal guardrails, and anomaly alerts.
            </p>
          </div>
        </div>

        {/* Company Selector */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <select
              aria-label="Select Company for AI Analysis"
              className="appearance-none bg-slate-950 text-white font-medium text-sm pl-4 pr-10 py-2.5 rounded-xl border border-slate-700 hover:border-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={selectedCompany?.id || ''}
              onChange={(e) => {
                const comp = companies.find((c) => c.id === parseInt(e.target.value));
                if (comp) onSelectCompany(comp);
              }}
            >
              {companies.map((comp) => (
                <option key={comp.id} value={comp.id}>
                  {comp.ticker} — {comp.legal_name}
                </option>
              ))}
            </select>
            <ChevronRight className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none rotate-90" />
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 space-x-2">
        <button
          onClick={() => setActiveTab('analyst')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'analyst'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
          }`}
        >
          <Bot className="w-4 h-4" />
          Grounded AI Analyst
        </button>
        <button
          onClick={() => setActiveTab('said_did')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'said_did'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
          }`}
        >
          <Target className="w-4 h-4" />
          Management "Said vs Did"
        </button>
        <button
          onClick={() => setActiveTab('pit')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'pit'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
          }`}
        >
          <Clock className="w-4 h-4" />
          Point-in-Time Simulation
        </button>
        <button
          onClick={() => {
            setActiveTab('report');
            if (selectedCompany) loadResearchReport(selectedCompany.id);
          }}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'report'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
          }`}
        >
          <FileCheck2 className="w-4 h-4" />
          Institutional Research Report
        </button>
        <button
          onClick={() => {
            setActiveTab('watchlist');
            loadWatchlist();
          }}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'watchlist'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
          }`}
        >
          <Bookmark className="w-4 h-4" />
          Watchlist & Anomaly Radar
        </button>
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* TAB 1: Grounded AI Analyst */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === 'analyst' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Query & Claims Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Input Box */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
              <label className="text-sm font-semibold text-slate-200 flex items-center justify-between">
                <span>Ask Analytical Financial Question ({selectedCompany?.ticker})</span>
                <span className="text-xs text-indigo-400 font-normal flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  Mandatory Citation Grounding Enforced
                </span>
              </label>

              <div className="relative">
                <textarea
                  rows={3}
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  placeholder="e.g. Why did ROCE decline? What did management state about capex & 5G rollout?"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  onClick={() => handleRunQuery()}
                  disabled={isQuerying || !queryText.trim()}
                  className="absolute right-3 bottom-3 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition"
                >
                  {isQuerying ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5" />
                      Generate Grounded Answer
                    </>
                  )}
                </button>
              </div>

              {/* Quick Suggestion Pills */}
              <div className="space-y-1.5">
                <span className="text-xs text-slate-400 font-medium">Suggested queries:</span>
                <div className="flex flex-wrap gap-2">
                  {suggestedPrompts.map((prompt: string, idx: number) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQueryText(prompt);
                        handleRunQuery(prompt);
                      }}
                      className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition flex items-center gap-1.5 text-left"
                    >
                      <ChevronRight className="w-3 h-3 text-indigo-400 flex-shrink-0" />
                      <span>{prompt}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Answer Display */}
            {analystResponse && (
              <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-6">
                {/* Meta Header */}
                <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg">
                      <ShieldCheck className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-white">
                        {analystResponse.company_name} ({analystResponse.ticker})
                      </h3>
                      <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-400">
                        <span>Intent: <strong className="text-indigo-400">{analystResponse.detected_intent}</strong></span>
                        <span>•</span>
                        <span>Generated: {analystResponse.generated_at}</span>
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-slate-400">Confidence Score</div>
                    <div className="text-lg font-bold text-emerald-400">
                      {Math.round(analystResponse.data_confidence_score * 100)}%
                    </div>
                  </div>
                </div>

                {/* Executive Summary */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Executive Summary & Analysis
                  </h4>
                  <div className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 text-sm text-slate-200 leading-relaxed font-sans">
                    {analystResponse.executive_summary}
                  </div>
                </div>

                {/* Key Claims Breakdown */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    Extracted Analytical Claims & Verification Lineage ({analystResponse.key_claims.length})
                  </h4>
                  <div className="space-y-3">
                    {analystResponse.key_claims.map((claim: AnalyticalClaim, idx: number) => (
                      <div
                        key={idx}
                        className="p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-2 hover:border-slate-700 transition"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm font-medium text-slate-200 leading-snug">
                            {claim.statement}
                          </p>
                          <span
                            className={`px-2.5 py-0.5 text-xs font-semibold rounded-md uppercase whitespace-nowrap ${
                              claim.grounding_status === 'VERIFIED_CITATION'
                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                : claim.grounding_status === 'DERIVED_METRIC'
                                ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                                : claim.grounding_status === 'UNSUPPORTED_REJECTED'
                                ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                                : 'bg-slate-800 text-slate-300'
                            }`}
                          >
                            {claim.grounding_status.replace('_', ' ')}
                          </span>
                        </div>
                        {claim.verifiable_source && (
                          <div className="text-xs text-slate-400 flex items-center gap-1.5">
                            <FileText className="w-3.5 h-3.5 text-indigo-400" />
                            <span>Source: <strong className="text-slate-300">{claim.verifiable_source}</strong></span>
                          </div>
                        )}
                        {claim.rejection_reason && (
                          <div className="text-xs text-red-400 bg-red-950/40 p-2 rounded-lg border border-red-900/50">
                            Sanitizer Notice: {claim.rejection_reason}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Caveats & Compliance */}
                <div className="p-3.5 bg-amber-950/20 border border-amber-900/40 rounded-xl space-y-1">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400">
                    <AlertTriangle className="w-4 h-4" />
                    Regulatory & Methodology Limitations
                  </div>
                  <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                    {analystResponse.caveats_and_limitations.map((c: string, i: number) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* Right Citation Explorer */}
          <div className="space-y-6">
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <FileText className="w-4 h-4 text-indigo-400" />
                  Supporting Statutory Evidence
                </h3>
                <span className="text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
                  {analystResponse?.supporting_citations.length || 0} Citations
                </span>
              </div>

              {!analystResponse ? (
                <div className="text-center py-12 text-slate-500 text-xs">
                  Run a query to retrieve verified annual report passages and citations.
                </div>
              ) : analystResponse.supporting_citations.length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-xs">
                  No statutory PDF citations matched for this structured prompt.
                </div>
              ) : (
                <div className="space-y-3">
                  {analystResponse.supporting_citations.map((cit: EvidenceCitation, idx: number) => (
                    <div
                      key={idx}
                      onClick={() => setSelectedCitation(cit)}
                      className={`p-3.5 rounded-xl border cursor-pointer transition ${
                        selectedCitation?.exact_quote === cit.exact_quote
                          ? 'bg-indigo-950/40 border-indigo-500/60'
                          : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="font-semibold text-indigo-300">
                          {cit.ticker} FY{cit.fiscal_year} (p. {cit.page_number})
                        </span>
                        <span className="text-emerald-400 font-mono">
                          {Math.round(cit.relevance_score * 100)}% Match
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 font-medium mb-1">
                        Section: {cit.section_title}
                      </div>
                      <p className="text-xs text-slate-300 line-clamp-3 italic">
                        "{cit.exact_quote}"
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {selectedCitation && (
                <div className="p-4 bg-slate-950 rounded-xl border border-indigo-500/30 space-y-2 mt-4">
                  <div className="text-xs font-semibold text-indigo-400 flex items-center justify-between">
                    <span>Active Citation Provenance</span>
                    <span className="text-[10px] font-mono text-slate-400">
                      {selectedCitation.provenance_hash.slice(0, 12)}...
                    </span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed bg-slate-900/80 p-2.5 rounded border border-slate-800">
                    "{selectedCitation.exact_quote}"
                  </p>
                  <div className="text-[11px] text-slate-400 space-y-0.5">
                    <div>Document: <strong className="text-slate-300">{selectedCitation.document_title}</strong></div>
                    <div>Page Number: <strong className="text-slate-300">{selectedCitation.page_number}</strong></div>
                    <div>Source Filing: <a href={selectedCitation.source_url || '#'} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">{selectedCitation.source_url || 'Statutory Filing'}</a></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 2: Management "Said vs Did" Credibility Tracker */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === 'said_did' && (
        <div className="space-y-6">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Target className="w-5 h-5 text-indigo-400" />
                  Management Guidance vs Outturn Credibility Tracker
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Tracks forward-looking statements in Annual Reports against multi-year actual financial outcomes.
                </p>
              </div>

              {saidVsDidData && (
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="text-xs text-slate-400">Commitments Tracked</div>
                    <div className="text-base font-bold text-white">
                      {saidVsDidData.total_commitments} Items
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-slate-400">Credibility Score</div>
                    <div className="text-xl font-bold text-emerald-400">
                      {saidVsDidData.credibility_score_pct.toFixed(1)}%
                    </div>
                  </div>
                </div>
              )}
            </div>

            {loadingSaidDid ? (
              <div className="py-16 text-center text-slate-400 text-sm">
                Evaluating statutory guidance records...
              </div>
            ) : !saidVsDidData || saidVsDidData.items.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-sm">
                No statutory guidance records available for {selectedCompany?.ticker}.
              </div>
            ) : (
              <div className="space-y-4">
                {saidVsDidData.items.map((item: ManagementGuidanceItem, idx: number) => (
                  <div
                    key={idx}
                    className="p-5 bg-slate-950/80 rounded-xl border border-slate-800 space-y-4 hover:border-slate-700 transition"
                  >
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <span className="px-2.5 py-1 text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-lg">
                          {item.category.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-slate-400">
                          Stated in <strong className="text-slate-200">{item.stated_period_label}</strong> (FY{item.fiscal_year_stated})
                        </span>
                      </div>

                      <div className="flex items-center gap-3">
                        <span
                          className={`px-3 py-1 text-xs font-bold rounded-lg border ${
                            item.delivery_status === 'MET'
                              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                              : item.delivery_status === 'PARTIALLY_MET'
                              ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                              : item.delivery_status === 'MISSED'
                              ? 'bg-red-500/20 text-red-400 border-red-500/30'
                              : 'bg-slate-800 text-slate-300 border-slate-700'
                          }`}
                        >
                          {item.delivery_status}
                        </span>
                        <span className="text-xs font-mono text-emerald-400 bg-emerald-950/40 px-2 py-1 rounded border border-emerald-900/50">
                          Score: {Math.round(item.credibility_score * 100)}%
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-3 bg-slate-900/90 rounded-lg border border-slate-800 space-y-1">
                        <div className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
                          <Bot className="w-3.5 h-3.5 text-indigo-400" />
                          Management Stated Guidance / Commitment
                        </div>
                        <p className="text-xs text-slate-200 italic leading-relaxed">
                          "{item.stated_guidance_text}"
                        </p>
                      </div>

                      <div className="p-3 bg-slate-900/90 rounded-lg border border-slate-800 space-y-1">
                        <div className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          Actual Financial Outcome (Evaluation FY{item.evaluation_year})
                        </div>
                        <p className="text-xs text-slate-200 leading-relaxed">
                          {item.actual_outcome_text}
                        </p>
                      </div>
                    </div>

                    <div className="text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-850 pt-2">
                      <span>Source: <strong className="text-slate-300">{item.source_citation}</strong></span>
                      <span>Evaluation Year: FY{item.evaluation_year}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 3: Point-in-Time Historical Simulation */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === 'pit' && (
        <div className="space-y-6">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Clock className="w-5 h-5 text-indigo-400" />
                Point-in-Time (PIT) Zero-Leakage Historical Backtesting
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Reconstructs financial analysis and AI reasoning as of a past historical cut-off period, rigorously discarding all subsequent future disclosures.
              </p>
            </div>

            {/* Controls */}
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Historical Cut-off Fiscal Year
                </label>
                <select
                  aria-label="Historical Cut-off Fiscal Year"
                  value={pitYear}
                  onChange={(e) => setPitYear(parseInt(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value={2023}>FY 2022-23 (FY23)</option>
                  <option value={2024}>FY 2023-24 (FY24)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Custom Historical Question (Optional)
                </label>
                <input
                  type="text"
                  value={pitQuestion}
                  onChange={(e) => setPitQuestion(e.target.value)}
                  placeholder="e.g. Evaluate leverage & capex as of FY23"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <button
                onClick={handleRunPIT}
                disabled={loadingPit}
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg flex items-center justify-center gap-2 transition"
              >
                {loadingPit ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Simulating...
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    Run Point-in-Time Simulation
                  </>
                )}
              </button>
            </div>

            {pitResponse && (
              <div className="p-6 bg-slate-950/90 rounded-xl border border-slate-800 space-y-6">
                {/* Guardrail Status Banner */}
                <div className="p-4 bg-emerald-950/30 border border-emerald-500/40 rounded-xl flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                    <div>
                      <div className="text-sm font-bold text-emerald-300">
                        Zero-Leakage Guardrail Enforced
                      </div>
                      <div className="text-xs text-slate-300">
                        Simulated as of FY{pitResponse.as_of_year}. Discarded {pitResponse.future_data_excluded.length} future periods: [{pitResponse.future_data_excluded.join(', ')}].
                      </div>
                    </div>
                  </div>
                  <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold rounded-lg uppercase">
                    PASS
                  </span>
                </div>

                {/* Simulated AI Analyst Response */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Point-in-Time Historical Analyst Verdict
                  </h4>
                  <div className="p-4 bg-slate-900/90 rounded-xl border border-slate-800 text-sm text-slate-200 leading-relaxed font-sans">
                    {pitResponse.historical_analyst_verdict.executive_summary}
                  </div>
                </div>

                {/* Key Claims as of that date */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    Historical Grounded Claims ({pitResponse.historical_analyst_verdict.key_claims.length})
                  </h4>
                  <div className="space-y-2">
                    {pitResponse.historical_analyst_verdict.key_claims.map((claim: AnalyticalClaim, idx: number) => (
                      <div
                        key={idx}
                        className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center justify-between text-xs"
                      >
                        <span className="text-slate-200 font-medium">{claim.statement}</span>
                        <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded font-semibold">
                          {claim.grounding_status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 4: Institutional 14-Section Company Research Report */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === 'report' && (
        <div className="space-y-6">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <FileCheck2 className="w-5 h-5 text-indigo-400" />
                  Comprehensive 14-Section Institutional Equity Research Report
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Synthesizes fundamentals, DuPont decomposition, forensics, DCF valuation scenarios, Said-vs-Did credibility, and statutory citations.
                </p>
              </div>

              <button
                onClick={() => selectedCompany && loadResearchReport(selectedCompany.id)}
                disabled={loadingReport}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg flex items-center gap-2 transition"
              >
                {loadingReport ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    Regenerate Report
                  </>
                )}
              </button>
            </div>

            {loadingReport ? (
              <div className="py-24 text-center text-slate-400 text-sm">
                Generating 14-section institutional research document...
              </div>
            ) : !researchReport ? (
              <div className="py-16 text-center text-slate-500 text-sm">
                Select a company to generate the institutional research report.
              </div>
            ) : (
              <div className="space-y-6 bg-slate-950 p-8 rounded-2xl border border-slate-800">
                {/* Report Header */}
                <div className="border-b border-slate-800 pb-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-black text-white tracking-tight">
                        {researchReport.legal_name}
                      </h2>
                      <div className="text-sm font-semibold text-indigo-400 mt-0.5">
                        NSE: {researchReport.ticker} | Sector: {researchReport.sector} | Industry: {researchReport.industry}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-slate-400">Current Market Price</div>
                      <div className="text-2xl font-bold text-white font-mono">
                        ₹{researchReport.current_market_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-2">
                    Methodology: {researchReport.methodology_version} | Published: {researchReport.generated_at}
                  </div>
                </div>

                {/* 1. Executive Summary */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                    1. Executive Summary & Investment Thesis
                  </h4>
                  <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 text-sm text-slate-200 leading-relaxed">
                    {researchReport.executive_summary}
                  </div>
                </div>

                {/* 2. Business Overview */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                    2. Business Overview & Operating Segments
                  </h4>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    {researchReport.business_overview}
                  </p>
                </div>

                {/* 3 & 4. Valuation & Profitability Summary Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
                    <h5 className="text-xs font-semibold text-slate-400 uppercase">Valuation Synthesis</h5>
                    <div className="text-xl font-bold text-emerald-400 font-mono">
                      Intrinsic Fair Value: ₹{researchReport.valuation_synthesis?.composite_central_fair_value?.toLocaleString('en-IN', { minimumFractionDigits: 2 }) || 'N/A'}
                    </div>
                    <div className="text-xs text-slate-300">
                      Upside / Downside: <strong className="text-emerald-400">{researchReport.valuation_synthesis?.composite_upside_downside_pct || '0.0'}%</strong>
                    </div>
                  </div>

                  <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
                    <h5 className="text-xs font-semibold text-slate-400 uppercase">Key Margins</h5>
                    <div className="text-sm text-slate-200 space-y-1">
                      <div>EBITDA Margin: <strong>{researchReport.profitability_analysis?.ebitda_margin_pct || '0.0'}%</strong></div>
                      <div>ROCE: <strong>{researchReport.profitability_analysis?.roce_pct || '0.0'}%</strong></div>
                    </div>
                  </div>
                </div>

                {/* 5. Statutory Caveats */}
                <div className="p-4 bg-amber-950/20 border border-amber-900/40 rounded-xl space-y-2">
                  <div className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" />
                    Regulatory Disclaimers & Limitations
                  </div>
                  <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                    {researchReport.research_caveats_and_uncertainty.map((c: string, i: number) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 5: Watchlist & Metric Anomaly Radar */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === 'watchlist' && (
        <div className="space-y-6">
          {/* Add Ticker Bar */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
            <form onSubmit={handleAddToWatchlist} className="flex flex-col md:flex-row items-center gap-4">
              <input
                type="text"
                value={newTicker}
                onChange={(e) => setNewTicker(e.target.value)}
                placeholder="Ticker (e.g. INFY, TCS, RELIANCE)"
                className="bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 w-full md:w-48 uppercase"
              />
              <input
                type="text"
                value={newNotes}
                onChange={(e) => setNewNotes(e.target.value)}
                placeholder="Monitoring thesis / notes (optional)"
                className="bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 w-full md:flex-1"
              />
              <button
                type="submit"
                disabled={!newTicker.trim()}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl flex items-center gap-2 transition whitespace-nowrap w-full md:w-auto justify-center"
              >
                <Plus className="w-4 h-4" />
                Add to Watchlist
              </button>
            </form>
          </div>

          {/* Watchlist Grid */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Bookmark className="w-4 h-4 text-indigo-400" />
                Tracked Equities & Active Anomaly Triggers ({watchlist.length})
              </h3>
            </div>

            {loadingWatchlist ? (
              <div className="py-12 text-center text-slate-400 text-sm">
                Scanning financial metrics for material anomalies...
              </div>
            ) : watchlist.length === 0 ? (
              <div className="py-8 text-center text-slate-500 text-sm">
                No active companies on your watchlist. Add a ticker above.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {watchlist.map((item: WatchlistItemDTO) => (
                  <div
                    key={item.id}
                    className="p-5 bg-slate-950/80 rounded-xl border border-slate-800 space-y-4 hover:border-slate-700 transition relative"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="text-base font-bold text-white">{item.ticker}</h4>
                        <p className="text-xs text-slate-400">{item.company_name}</p>
                      </div>
                      <button
                        onClick={() => handleRemoveFromWatchlist(item.ticker)}
                        className="text-slate-500 hover:text-red-400 p-1 transition"
                        title="Remove from watchlist"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="p-2 bg-slate-900 rounded border border-slate-800">
                        <span className="text-slate-400">P/E Ratio</span>
                        <div className="font-bold text-white mt-0.5">{item.latest_pe.toFixed(1)}x</div>
                      </div>
                      <div className="p-2 bg-slate-900 rounded border border-slate-800">
                        <span className="text-slate-400">ROCE</span>
                        <div className="font-bold text-emerald-400 mt-0.5">{item.latest_roce_pct.toFixed(1)}%</div>
                      </div>
                    </div>

                    {item.notes && (
                      <p className="text-xs text-slate-300 italic bg-slate-900/50 p-2 rounded border border-slate-850">
                        "{item.notes}"
                      </p>
                    )}

                    {/* Active Alerts */}
                    <div className="space-y-1.5 pt-2 border-t border-slate-850">
                      <div className="text-[11px] font-semibold text-slate-400 flex items-center justify-between">
                        <span>Anomaly Triggers</span>
                        <span className="text-indigo-400 font-bold">{item.active_alerts.length}</span>
                      </div>
                      {item.active_alerts.map((al: WatchlistAlert, idx: number) => (
                        <div
                          key={idx}
                          className="p-2 bg-indigo-950/30 border border-indigo-900/40 rounded text-[11px] text-slate-300 space-y-0.5"
                        >
                          <div className="font-semibold text-indigo-300 flex items-center justify-between">
                            <span>{al.metric_name}</span>
                            <span className="font-mono">{al.current_value}</span>
                          </div>
                          <p className="text-slate-400">{al.message}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
