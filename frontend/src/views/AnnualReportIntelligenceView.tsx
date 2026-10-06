import React, { useState, useEffect } from 'react';
import {
  FileText,
  Search,
  Upload,
  BookOpen,
  CheckCircle2,
  AlertCircle,
  Layers,
  ShieldCheck,
  Hash,
  Database,
  Building2,
  FileCheck,
} from 'lucide-react';
import { ApiService } from '../services/api';
import {
  DocumentMetadataDTO,
  DocumentDetailDTO,
  DocumentPageDTO,
  DocumentRetrievalResult,
  DocumentRetrievalResponse,
  IngestionUploadResponse,
} from '../types/api';

export const AnnualReportIntelligenceView: React.FC = () => {
  // State
  const [documents, setDocuments] = useState<DocumentMetadataDTO[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [selectedDocDetail, setSelectedDocDetail] = useState<DocumentDetailDTO | null>(null);
  const [activePageNumber, setActivePageNumber] = useState<number>(1);
  const [activePageData, setActivePageData] = useState<DocumentPageDTO | null>(null);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState<string>('capital expenditure 5G network rollout capex');
  const [tickerFilter, setTickerFilter] = useState<string>('');
  const [sectionFilter, setSectionFilter] = useState<string>('');
  const [canonicalSections, setCanonicalSections] = useState<string[]>([]);
  const [searchResults, setSearchResults] = useState<DocumentRetrievalResult[]>([]);
  const [searchMeta, setSearchMeta] = useState<DocumentRetrievalResponse | null>(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState<boolean>(true);

  // Active View Tab
  const [activeTab, setActiveTab] = useState<'search' | 'reader' | 'taxonomy'>('search');

  // Upload Modal State
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTicker, setUploadTicker] = useState<string>('RELIANCE');
  const [uploadFY, setUploadFY] = useState<number>(2024);
  const [uploadTitle, setUploadTitle] = useState<string>('');
  const [uploadSourceUrl, setUploadSourceUrl] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<IngestionUploadResponse | null>(null);

  // Preset Financial Queries
  const PRESET_QUERIES = [
    { label: '5G Capex & Digital Strategy', query: 'capital expenditure 5G network rollout capex investments', ticker: 'RELIANCE' },
    { label: 'Share Buyback & Capital Return', query: 'completed share buyback dividend payout capital return', ticker: 'TCS' },
    { label: 'Post-Merger Asset Quality & NPA', query: 'gross non-performing assets GNPA provision coverage ratio PCR', ticker: 'HDFCBANK' },
    { label: 'Auditor Key Matters & Opinions', query: 'independent auditor key audit matters internal financial controls', ticker: '' },
    { label: 'Related Party & Contingent Liabilities', query: 'related party transactions guarantees contingent liabilities commitments', ticker: '' },
  ];

  // Load documents and canonical sections on mount
  useEffect(() => {
    loadDocuments();
    loadCanonicalSections();
  }, []);

  const loadDocuments = async () => {
    setIsLoadingDocs(true);
    try {
      const docs = await ApiService.getDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !selectedDocId) {
        setSelectedDocId(docs[0].id);
      }
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setIsLoadingDocs(false);
    }
  };

  const loadCanonicalSections = async () => {
    try {
      const secs = await ApiService.getCanonicalSections();
      setCanonicalSections(secs);
    } catch (err) {
      console.error('Failed to load canonical sections:', err);
    }
  };

  // Load document detail when selectedDocId changes
  useEffect(() => {
    if (selectedDocId) {
      loadDocDetail(selectedDocId);
    }
  }, [selectedDocId]);

  const loadDocDetail = async (id: number) => {
    try {
      const detail = await ApiService.getDocumentDetail(id);
      setSelectedDocDetail(detail);
      if (detail.pages.length > 0) {
        setActivePageNumber(1);
        setActivePageData(detail.pages[0]);
      }
    } catch (err) {
      console.error('Failed to load doc detail:', err);
    }
  };

  // Update active page data when page number changes
  useEffect(() => {
    if (selectedDocDetail && selectedDocDetail.pages) {
      const page = selectedDocDetail.pages.find((p) => p.page_number === activePageNumber);
      if (page) {
        setActivePageData(page);
      }
    }
  }, [activePageNumber, selectedDocDetail]);

  // Execute Search
  const handleSearch = async (overrideQuery?: string, overrideTicker?: string) => {
    const q = overrideQuery !== undefined ? overrideQuery : searchQuery;
    const t = overrideTicker !== undefined ? overrideTicker : tickerFilter;

    if (!q.trim()) return;

    setIsSearching(true);
    try {
      const response = await ApiService.searchDocuments({
        query_text: q,
        ticker: t || undefined,
        section: sectionFilter || undefined,
        top_k: 6,
        min_relevance_score: 0.1,
      });
      setSearchResults(response.results);
      setSearchMeta(response);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  // Jump from Citation directly to Reader Page
  const jumpToCitation = async (docId: number, pageNum: number) => {
    setSelectedDocId(docId);
    await loadDocDetail(docId);
    setActivePageNumber(pageNum);
    setActiveTab('reader');
  };

  // Handle PDF Upload Ingestion
  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadError('Please select a PDF annual report file to upload.');
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const res = await ApiService.uploadDocument(
        uploadFile,
        uploadTicker,
        uploadFY,
        uploadTitle || undefined,
        uploadSourceUrl || undefined
      );
      setUploadSuccess(res);
      await loadDocuments();
      setSelectedDocId(res.document_id);
    } catch (err: any) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                PHASE 6: DOCUMENT INTELLIGENCE & RAG
              </span>
              <span className="flex items-center gap-1 text-xs text-emerald-400 font-mono">
                <ShieldCheck className="w-3.5 h-3.5" /> Zero-Hallucination Provenance
              </span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Statutory Annual Report Intelligence
            </h1>
            <p className="text-sm text-slate-400 mt-1 max-w-3xl">
              Deterministic RAG subsystem indexing full statutory Indian corporate filings (LODR Reg 34 / Companies Act 2013).
              Every analytical finding is backed by 1-indexed physical page numbers, section taxonomy, and cryptographic SHA-256 provenance hashes.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsUploadOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
            >
              <Upload className="w-4 h-4" />
              Upload Filing PDF
            </button>
          </div>
        </div>

        {/* Document Library Horizontal Selector */}
        <div className="mt-6 pt-5 border-t border-slate-800">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-indigo-400" />
              Indexed Document Library ({documents.length} Filings)
            </span>
            <span className="text-xs font-mono text-slate-500">Methodology: v1.0.0-phase6</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {isLoadingDocs ? (
              <div className="col-span-3 py-6 text-center text-xs text-slate-500 font-mono">
                Loading indexed statutory annual reports...
              </div>
            ) : (
              documents.map((doc) => {
                const isSelected = selectedDocId === doc.id;
                return (
                  <div
                    key={doc.id}
                    onClick={() => setSelectedDocId(doc.id)}
                    className={`cursor-pointer p-3.5 rounded-lg border transition-all ${
                      isSelected
                        ? 'bg-indigo-950/30 border-indigo-500/50 text-white shadow-sm'
                        : 'bg-slate-950/50 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700">
                          {doc.ticker}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">FY{doc.fiscal_year}</span>
                      </div>
                      <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {doc.processing_status}
                      </span>
                    </div>

                    <div className="font-medium text-xs mt-2 truncate text-slate-200" title={doc.title}>
                      {doc.title}
                    </div>

                    <div className="flex items-center gap-3 text-[11px] text-slate-400 mt-2.5 pt-2 border-t border-slate-800/80">
                      <span className="flex items-center gap-1">
                        <FileText className="w-3 h-3 text-slate-500" /> {doc.page_count} Pages
                      </span>
                      <span className="flex items-center gap-1">
                        <Layers className="w-3 h-3 text-slate-500" /> {doc.total_chunks} Chunks
                      </span>
                      <span className="text-[10px] font-mono text-slate-500 truncate ml-auto" title={doc.file_hash_sha256}>
                        #{doc.file_hash_sha256.substring(0, 6)}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Main Tabs Header */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('search')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'search'
              ? 'bg-indigo-600 text-white'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Search className="w-4 h-4" />
          Semantic Research & Citations
        </button>
        <button
          onClick={() => setActiveTab('reader')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'reader'
              ? 'bg-indigo-600 text-white'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          Interactive Page & Section Reader
        </button>
        <button
          onClick={() => setActiveTab('taxonomy')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'taxonomy'
              ? 'bg-indigo-600 text-white'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Statutory Indian Taxonomy & Governance
        </button>
      </div>

      {/* TAB 1: Semantic Research & Citation Search */}
      {activeTab === 'search' && (
        <div className="space-y-5">
          {/* Query Bar */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex flex-col md:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Enter financial research query (e.g., 5G capex, buyback details, auditor qualifications, loan loss provisions)..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div className="flex items-center gap-2">
                <select
                  value={tickerFilter}
                  onChange={(e) => setTickerFilter(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">All Tickers</option>
                  <option value="RELIANCE">RELIANCE</option>
                  <option value="TCS">TCS</option>
                  <option value="HDFCBANK">HDFCBANK</option>
                </select>

                <select
                  value={sectionFilter}
                  onChange={(e) => setSectionFilter(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 max-w-[180px] truncate"
                >
                  <option value="">All Sections</option>
                  {canonicalSections.map((sec) => (
                    <option key={sec} value={sec}>
                      {sec.replace(/_/g, ' ')}
                    </option>
                  ))}
                </select>

                <button
                  onClick={() => handleSearch()}
                  disabled={isSearching}
                  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors flex items-center gap-2 whitespace-nowrap"
                >
                  {isSearching ? 'Searching...' : 'Search Filings'}
                </button>
              </div>
            </div>

            {/* Presets */}
            <div className="flex flex-wrap items-center gap-2 mt-4 pt-3 border-t border-slate-800/80">
              <span className="text-xs text-slate-400 font-medium">Quick Prompts:</span>
              {PRESET_QUERIES.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setSearchQuery(preset.query);
                    setTickerFilter(preset.ticker);
                    handleSearch(preset.query, preset.ticker);
                  }}
                  className="text-xs px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          {/* Search Results */}
          {searchMeta && (
            <div className="flex items-center justify-between text-xs text-slate-400 px-1">
              <span>
                Found <strong className="text-white">{searchMeta.total_matches}</strong> verifiable citations in{' '}
                <strong className="text-indigo-400">{searchMeta.retrieval_latency_ms}ms</strong>
              </span>
              <span className="font-mono text-[11px] text-slate-500">
                Vector Model: {searchMeta.embedding_model}
              </span>
            </div>
          )}

          <div className="grid grid-cols-1 gap-4">
            {searchResults.map((res, idx) => (
              <div
                key={res.chunk_id || idx}
                className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all space-y-3"
              >
                {/* Result Header */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                      {res.ticker}
                    </span>
                    <span className="text-xs text-slate-300 font-semibold">{res.document_title}</span>
                    <span className="text-xs text-slate-500 font-mono">FY{res.fiscal_year}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {(res.relevance_score * 100).toFixed(1)}% Match Score
                    </span>
                    <button
                      onClick={() => jumpToCitation(res.document_id, res.page_number)}
                      className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium px-2 py-1 rounded bg-indigo-950/40 border border-indigo-800/50 hover:bg-indigo-900/50 transition-colors"
                    >
                      <BookOpen className="w-3.5 h-3.5" /> Jump to Page {res.page_number}
                    </button>
                  </div>
                </div>

                {/* Section Badge & Provenance */}
                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[11px]">
                    Section: {res.section_title}
                  </span>
                  <span className="font-mono text-slate-500 text-[11px] flex items-center gap-1">
                    <Hash className="w-3 h-3" /> Provenance: {res.citation.provenance_hash.substring(0, 16)}...
                  </span>
                </div>

                {/* Verbatim Excerpt */}
                <div className="bg-slate-950/80 border border-slate-800/80 rounded-lg p-4 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {res.chunk_text}
                </div>
              </div>
            ))}

            {searchResults.length === 0 && !isSearching && (
              <div className="bg-slate-900/50 border border-dashed border-slate-800 rounded-xl p-12 text-center text-slate-400">
                <FileCheck className="w-10 h-10 mx-auto mb-3 text-slate-600" />
                <p className="text-base font-semibold text-slate-300">Ready for Financial RAG Inquiries</p>
                <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                  Execute search across Reliance Industries, TCS, and HDFC Bank annual report disclosures with exact verifiable citations.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: Interactive Page & Section Reader */}
      {activeTab === 'reader' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Table of Contents & Page List */}
          <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <span className="text-xs font-semibold uppercase text-slate-400 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-indigo-400" />
                Table of Contents & Pages
              </span>
              <span className="text-xs font-mono text-slate-500">
                {selectedDocDetail?.page_count || 0} Pages Total
              </span>
            </div>

            {/* Document Selector Dropdown */}
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Active Document:</label>
              <select
                value={selectedDocId || ''}
                onChange={(e) => setSelectedDocId(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              >
                {documents.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.ticker} FY{d.fiscal_year} - {d.title}
                  </option>
                ))}
              </select>
            </div>

            {/* Detected Statutory Sections */}
            {selectedDocDetail?.sections_detected && selectedDocDetail.sections_detected.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Detected Statutory Sections:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {selectedDocDetail.sections_detected.map((sec) => (
                    <span
                      key={sec}
                      className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950/40 text-indigo-300 border border-indigo-800/40"
                    >
                      {sec.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Page List */}
            <div className="space-y-1.5 max-h-[500px] overflow-y-auto pr-1">
              {selectedDocDetail?.pages.map((p) => {
                const isActive = activePageNumber === p.page_number;
                return (
                  <div
                    key={p.page_number}
                    onClick={() => setActivePageNumber(p.page_number)}
                    className={`cursor-pointer p-2.5 rounded-lg border transition-all text-xs flex items-center justify-between ${
                      isActive
                        ? 'bg-indigo-600 text-white border-indigo-500 font-medium'
                        : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <span className="font-mono text-[11px] opacity-80">Page {p.page_number}</span>
                      <span className="truncate opacity-90 text-[11px]">
                        {p.detected_section ? p.detected_section.replace(/_/g, ' ') : 'General'}
                      </span>
                    </div>
                    {p.has_tables && (
                      <span
                        className={`text-[9px] px-1 py-0.2 rounded font-mono ${
                          isActive ? 'bg-indigo-800 text-white' : 'bg-slate-800 text-emerald-400'
                        }`}
                      >
                        [TABLE]
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right: Page Viewer */}
          <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
            {/* Viewer Header */}
            <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-white">
                    {selectedDocDetail?.title || 'Document Page Viewer'}
                  </span>
                  <span className="px-2 py-0.5 rounded text-xs font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    Page {activePageNumber} of {selectedDocDetail?.page_count || 1}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
                  <span>Section: <strong className="text-slate-200">{activePageData?.detected_section || 'GENERAL_DISCLOSURE'}</strong></span>
                  <span>•</span>
                  <span>{activePageData?.char_count || 0} characters</span>
                  {activePageData?.has_tables && (
                    <span className="text-emerald-400 font-mono text-[10px]">• Numeric Tables Detected</span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  disabled={activePageNumber <= 1}
                  onClick={() => setActivePageNumber((prev) => Math.max(1, prev - 1))}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-xs font-medium text-slate-200 rounded transition-colors"
                >
                  Previous Page
                </button>
                <button
                  disabled={!selectedDocDetail || activePageNumber >= selectedDocDetail.page_count}
                  onClick={() => setActivePageNumber((prev) => Math.min(selectedDocDetail?.page_count || 1, prev + 1))}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-xs font-medium text-slate-200 rounded transition-colors"
                >
                  Next Page
                </button>
              </div>
            </div>

            {/* Verbatim Page Content */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap min-h-[420px] max-h-[620px] overflow-y-auto">
              {activePageData?.text || 'No text extracted on this page.'}
            </div>

            {/* Footer Metadata */}
            <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono pt-2 border-t border-slate-800/60">
              <span>SHA-256 Provenance Fingerprint: {selectedDocDetail?.file_hash_sha256}</span>
              <span>Extraction Method: {selectedDocDetail?.extraction_method}</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Statutory Indian Taxonomy & Governance */}
      {activeTab === 'taxonomy' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Building2 className="w-4 h-4 text-indigo-400" />
              Indian Statutory Filing Framework
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Under SEBI (Listing Obligations and Disclosure Requirements) Regulations, 2015 (Reg 34) and the Companies Act, 2013, Indian listed companies submit comprehensive annual reports with standardized statutory sections.
            </p>

            <div className="space-y-2.5 pt-2">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1">
                <span className="font-semibold text-slate-200">1. Management Discussion & Analysis (MD&A)</span>
                <p className="text-slate-400 text-[11px]">
                  Mandated under Schedule V of SEBI LODR. Covers industry structure, segment performance, risks, internal control systems, and financial ratios.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1">
                <span className="font-semibold text-slate-200">2. Independent Auditor's Report (CARO 2020)</span>
                <p className="text-slate-400 text-[11px]">
                  Conducted under Section 143 of Companies Act, 2013. Includes Key Audit Matters (KAMs), opinion on Internal Financial Controls (IFCoFR), and CARO clauses.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1">
                <span className="font-semibold text-slate-200">3. Related Party Disclosures (Ind AS 24)</span>
                <p className="text-slate-400 text-[11px]">
                  Complete disclosure of transactions with holding, subsidiary, joint venture, and Key Management Personnel (KMP).
                </p>
              </div>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1">
                <span className="font-semibold text-slate-200">4. Contingent Liabilities & Commitments (Ind AS 37)</span>
                <p className="text-slate-400 text-[11px]">
                  Statutory reporting of tax disputes, guarantees, capital commitments, and unacknowledged debts.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Non-Hallucination RAG Principles
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Institutional financial research mandates zero fabrication. Our RAG engine guarantees provenance through cryptographic hashing and exact verbatim citations.
            </p>

            <div className="space-y-3 pt-2">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div className="text-xs">
                  <strong className="text-slate-200 block">Physical Page Integrity</strong>
                  <span className="text-slate-400 text-[11px]">
                    Every extracted chunk is strictly anchored to its 1-indexed physical PDF page, ensuring analyst verification against original exchange filings.
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div className="text-xs">
                  <strong className="text-slate-200 block">SHA-256 Provenance Fingerprinting</strong>
                  <span className="text-slate-400 text-[11px]">
                    Chunks and documents carry cryptographic SHA-256 hashes, preventing silent mutations or outdated document references.
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div className="text-xs">
                  <strong className="text-slate-200 block">Deterministic 384-Dim Embedding Vectorizer</strong>
                  <span className="text-slate-400 text-[11px]">
                    Normalized feature-hashing embedding provider with financial domain keyword boosts (e.g. capex, EBITDA, auditor opinion, borrowings) for 100% reproducible retrieval.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Filing Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Upload className="w-4 h-4 text-indigo-400" />
                Upload Statutory Annual Report PDF
              </h3>
              <button
                onClick={() => setIsUploadOpen(false)}
                className="text-slate-400 hover:text-white text-lg leading-none"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Company Ticker</label>
                <input
                  type="text"
                  required
                  value={uploadTicker}
                  onChange={(e) => setUploadTicker(e.target.value.toUpperCase())}
                  placeholder="e.g. INFY, ICICIBANK, RELIANCE"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Fiscal Year</label>
                  <input
                    type="number"
                    required
                    min={2015}
                    max={2030}
                    value={uploadFY}
                    onChange={(e) => setUploadFY(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Filing Document Title</label>
                  <input
                    type="text"
                    value={uploadTitle}
                    onChange={(e) => setUploadTitle(e.target.value)}
                    placeholder="e.g. Annual Report 2023-24"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Source URL (Optional)</label>
                <input
                  type="url"
                  value={uploadSourceUrl}
                  onChange={(e) => setUploadSourceUrl(e.target.value)}
                  placeholder="https://www.bseindia.com/..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Select Annual Report PDF File</label>
                <input
                  type="file"
                  accept="application/pdf"
                  required
                  onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
                  className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer"
                />
              </div>

              {uploadError && (
                <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  {uploadError}
                </div>
              )}

              {uploadSuccess && (
                <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-xs space-y-1">
                  <div className="font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" /> Ingestion Completed!
                  </div>
                  <div>Indexed {uploadSuccess.page_count} pages and {uploadSuccess.total_chunks_indexed} semantic chunks.</div>
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsUploadOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUploading}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-xs font-semibold text-white rounded-lg transition-colors flex items-center gap-2"
                >
                  {isUploading ? 'Parsing & Indexing...' : 'Ingest & Index Filing'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
