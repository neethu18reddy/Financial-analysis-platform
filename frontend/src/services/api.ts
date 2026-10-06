import {
  HealthResponse,
  Company,
  CompanyDetail,
  FinancialPeriod,
  CompanyStatementsResponse,
  ValidationAuditReport,
  DataProvenance,
  CorporateAction,
  SourceProviderMetadata,
  CompanyFundamentalResponse,
  CompanyDuPontResponse,
  CompanyCommonSizeResponse,
  CompanyForensicResponse,
  ValuationSummaryResponse,
  DCFValuationInputs,
  DCFValuationResult,
  ReverseDCFInputs,
  ReverseDCFResult,
  MultiplesValuationResult,
  ScenarioAnalysisResult,
  SensitivityMatrixResult,
  BankValuationResult,
  SOTPSegment,
  SOTPValuationResult,
  DocumentMetadataDTO,
  DocumentDetailDTO,
  DocumentPageDTO,
  DocumentRetrievalQuery,
  DocumentRetrievalResponse,
  IngestionUploadResponse,
  AIAnalystQuery,
  AIAnalystResponse,
  ManagementSaidVsDidResponse,
  PointInTimeAnalysisRequest,
  PointInTimeAnalysisResponse,
  CompanyResearchReport,
  WatchlistItemDTO,
} from '../types/api';

const API_BASE_URL = 'http://localhost:8000/api/v1';

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const message = errorBody?.error?.message || errorBody?.detail || `HTTP Error ${response.status}: ${response.statusText}`;
    throw new Error(message);
  }

  return response.json();
}

export const ApiService = {
  async getHealth(): Promise<HealthResponse> {
    return fetchJson<HealthResponse>('/health');
  },

  async getCompanies(search?: string, sector?: string): Promise<Company[]> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (sector) params.append('sector', sector);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<Company[]>(`/companies${qs}`);
  },

  async getCompanyDetail(identifier: string): Promise<CompanyDetail> {
    return fetchJson<CompanyDetail>(`/companies/${encodeURIComponent(identifier)}`);
  },

  async getCompanyPeriods(identifier: string): Promise<FinancialPeriod[]> {
    return fetchJson<FinancialPeriod[]>(`/companies/${encodeURIComponent(identifier)}/periods`);
  },

  async getFinancialStatements(
    identifier: string,
    statementType: 'CONSOLIDATED' | 'STANDALONE' = 'CONSOLIDATED',
    limitPeriods: number = 5
  ): Promise<CompanyStatementsResponse> {
    const params = new URLSearchParams({
      statement_type: statementType,
      limit_periods: limitPeriods.toString(),
    });
    return fetchJson<CompanyStatementsResponse>(
      `/companies/${encodeURIComponent(identifier)}/statements?${params.toString()}`
    );
  },

  async getValidationReport(identifier: string): Promise<ValidationAuditReport> {
    return fetchJson<ValidationAuditReport>(
      `/companies/${encodeURIComponent(identifier)}/validation-report`
    );
  },

  async getProvenance(entityType: string, entityId: number): Promise<DataProvenance[]> {
    return fetchJson<DataProvenance[]>(
      `/provenance/${encodeURIComponent(entityType)}/${entityId}`
    );
  },

  async getCorporateActions(identifier: string): Promise<CorporateAction[]> {
    return fetchJson<CorporateAction[]>(
      `/companies/${encodeURIComponent(identifier)}/corporate-actions`
    );
  },

  async getSources(): Promise<SourceProviderMetadata[]> {
    return fetchJson<SourceProviderMetadata[]>('/sources');
  },

  async getFundamentalAnalysis(
    identifier: string,
    statementType: 'CONSOLIDATED' | 'STANDALONE' = 'CONSOLIDATED',
    limitPeriods: number = 5
  ): Promise<CompanyFundamentalResponse> {
    const params = new URLSearchParams({
      statement_type: statementType,
      limit_periods: limitPeriods.toString(),
    });
    return fetchJson<CompanyFundamentalResponse>(
      `/companies/${encodeURIComponent(identifier)}/analysis/full?${params.toString()}`
    );
  },

  async getDuPontAnalysis(
    identifier: string,
    statementType: 'CONSOLIDATED' | 'STANDALONE' = 'CONSOLIDATED',
    limitPeriods: number = 5
  ): Promise<CompanyDuPontResponse> {
    const params = new URLSearchParams({
      statement_type: statementType,
      limit_periods: limitPeriods.toString(),
    });
    return fetchJson<CompanyDuPontResponse>(
      `/companies/${encodeURIComponent(identifier)}/analysis/dupont?${params.toString()}`
    );
  },

  async getCommonSizeStatements(
    identifier: string,
    statementKind: 'INCOME_STATEMENT' | 'BALANCE_SHEET' = 'INCOME_STATEMENT',
    statementType: 'CONSOLIDATED' | 'STANDALONE' = 'CONSOLIDATED',
    limitPeriods: number = 5
  ): Promise<CompanyCommonSizeResponse> {
    const params = new URLSearchParams({
      statement_kind: statementKind,
      statement_type: statementType,
      limit_periods: limitPeriods.toString(),
    });
    return fetchJson<CompanyCommonSizeResponse>(
      `/companies/${encodeURIComponent(identifier)}/analysis/common-size?${params.toString()}`
    );
  },

  async getForensicSummary(
    identifier: string,
    statementType: 'CONSOLIDATED' | 'STANDALONE' = 'CONSOLIDATED',
    limitPeriods: number = 5
  ): Promise<CompanyForensicResponse> {
    const params = new URLSearchParams({
      statement_type: statementType,
      limit_periods: limitPeriods.toString(),
    });
    return fetchJson<CompanyForensicResponse>(
      `/companies/${encodeURIComponent(identifier)}/forensics/summary?${params.toString()}`
    );
  },

  async getBeneishAnalysis(
    identifier: string,
    statementType: 'CONSOLIDATED' | 'STANDALONE' = 'CONSOLIDATED',
    limitPeriods: number = 5
  ): Promise<any> {
    const params = new URLSearchParams({
      statement_type: statementType,
      limit_periods: limitPeriods.toString(),
    });
    return fetchJson<any>(
      `/companies/${encodeURIComponent(identifier)}/forensics/beneish?${params.toString()}`
    );
  },

  async getPiotroskiAnalysis(
    identifier: string,
    statementType: 'CONSOLIDATED' | 'STANDALONE' = 'CONSOLIDATED',
    limitPeriods: number = 5
  ): Promise<any> {
    const params = new URLSearchParams({
      statement_type: statementType,
      limit_periods: limitPeriods.toString(),
    });
    return fetchJson<any>(
      `/companies/${encodeURIComponent(identifier)}/forensics/piotroski?${params.toString()}`
    );
  },

  async getAltmanAnalysis(
    identifier: string,
    statementType: 'CONSOLIDATED' | 'STANDALONE' = 'CONSOLIDATED',
    limitPeriods: number = 5
  ): Promise<any> {
    const params = new URLSearchParams({
      statement_type: statementType,
      limit_periods: limitPeriods.toString(),
    });
    return fetchJson<any>(
      `/companies/${encodeURIComponent(identifier)}/forensics/altman?${params.toString()}`
    );
  },

  async getForensicSignals(
    identifier: string,
    statementType: 'CONSOLIDATED' | 'STANDALONE' = 'CONSOLIDATED',
    limitPeriods: number = 5
  ): Promise<any> {
    const params = new URLSearchParams({
      statement_type: statementType,
      limit_periods: limitPeriods.toString(),
    });
    return fetchJson<any>(
      `/companies/${encodeURIComponent(identifier)}/forensics/signals?${params.toString()}`
    );
  },

  // ==========================================================================
  // PHASE 4: VALUATION ENGINE CALLS
  // ==========================================================================

  async getValuationSummary(
    identifier: string,
    marketPrice?: number
  ): Promise<ValuationSummaryResponse> {
    const params = new URLSearchParams();
    if (marketPrice !== undefined) params.append('market_price', marketPrice.toString());
    return fetchJson<ValuationSummaryResponse>(
      `/companies/${encodeURIComponent(identifier)}/valuation/summary${params.toString() ? `?${params.toString()}` : ''}`
    );
  },

  async runCustomDCF(
    identifier: string,
    inputs: DCFValuationInputs,
    marketPrice?: number
  ): Promise<DCFValuationResult> {
    const params = new URLSearchParams();
    if (marketPrice !== undefined) params.append('market_price', marketPrice.toString());
    return fetchJson<DCFValuationResult>(
      `/companies/${encodeURIComponent(identifier)}/valuation/dcf${params.toString() ? `?${params.toString()}` : ''}`,
      {
        method: 'POST',
        body: JSON.stringify(inputs),
      }
    );
  },

  async runReverseDCF(
    identifier: string,
    inputs: ReverseDCFInputs
  ): Promise<ReverseDCFResult> {
    return fetchJson<ReverseDCFResult>(
      `/companies/${encodeURIComponent(identifier)}/valuation/reverse-dcf`,
      {
        method: 'POST',
        body: JSON.stringify(inputs),
      }
    );
  },

  async getValuationMultiples(
    identifier: string,
    marketPrice?: number,
    targetPe?: number,
    targetEvEbitda?: number,
    targetPb?: number
  ): Promise<MultiplesValuationResult> {
    const params = new URLSearchParams();
    if (marketPrice !== undefined) params.append('market_price', marketPrice.toString());
    if (targetPe !== undefined) params.append('target_pe', targetPe.toString());
    if (targetEvEbitda !== undefined) params.append('target_ev_ebitda', targetEvEbitda.toString());
    if (targetPb !== undefined) params.append('target_pb', targetPb.toString());
    return fetchJson<MultiplesValuationResult>(
      `/companies/${encodeURIComponent(identifier)}/valuation/multiples${params.toString() ? `?${params.toString()}` : ''}`
    );
  },

  async runScenarioAnalysis(
    identifier: string,
    marketPrice?: number,
    baseGrowth?: number,
    baseMargin?: number,
    baseWacc?: number,
    baseTerminalGrowth?: number
  ): Promise<ScenarioAnalysisResult> {
    const params = new URLSearchParams();
    if (marketPrice !== undefined) params.append('market_price', marketPrice.toString());
    if (baseGrowth !== undefined) params.append('base_growth_pct', baseGrowth.toString());
    if (baseMargin !== undefined) params.append('base_margin_pct', baseMargin.toString());
    if (baseWacc !== undefined) params.append('base_wacc_pct', baseWacc.toString());
    if (baseTerminalGrowth !== undefined) params.append('base_terminal_growth_pct', baseTerminalGrowth.toString());
    return fetchJson<ScenarioAnalysisResult>(
      `/companies/${encodeURIComponent(identifier)}/valuation/scenarios?${params.toString()}`,
      { method: 'POST' }
    );
  },

  async getSensitivityWACCTG(
    identifier: string,
    baseWacc: number = 11.2,
    baseTg: number = 5.0,
    baseGrowth: number = 11.5,
    baseMargin: number = 18.0,
    marketPrice?: number
  ): Promise<SensitivityMatrixResult> {
    const params = new URLSearchParams({
      base_wacc_pct: baseWacc.toString(),
      base_terminal_growth_pct: baseTg.toString(),
      base_growth_pct: baseGrowth.toString(),
      base_margin_pct: baseMargin.toString(),
    });
    if (marketPrice !== undefined) params.append('market_price', marketPrice.toString());
    return fetchJson<SensitivityMatrixResult>(
      `/companies/${encodeURIComponent(identifier)}/valuation/sensitivity/wacc-terminal-growth?${params.toString()}`,
      { method: 'POST' }
    );
  },

  async getSensitivityGrowthMargin(
    identifier: string,
    baseGrowth: number = 11.5,
    baseMargin: number = 18.0,
    baseWacc: number = 11.2,
    baseTg: number = 5.0,
    marketPrice?: number
  ): Promise<SensitivityMatrixResult> {
    const params = new URLSearchParams({
      base_growth_pct: baseGrowth.toString(),
      base_margin_pct: baseMargin.toString(),
      base_wacc_pct: baseWacc.toString(),
      base_terminal_growth_pct: baseTg.toString(),
    });
    if (marketPrice !== undefined) params.append('market_price', marketPrice.toString());
    return fetchJson<SensitivityMatrixResult>(
      `/companies/${encodeURIComponent(identifier)}/valuation/sensitivity/growth-margin?${params.toString()}`,
      { method: 'POST' }
    );
  },

  async getBankValuation(
    identifier: string,
    marketPrice?: number
  ): Promise<BankValuationResult> {
    const params = new URLSearchParams();
    if (marketPrice !== undefined) params.append('market_price', marketPrice.toString());
    return fetchJson<BankValuationResult>(
      `/companies/${encodeURIComponent(identifier)}/valuation/financial-institution${params.toString() ? `?${params.toString()}` : ''}`
    );
  },

  async runSOTPValuation(
    identifier: string,
    segments: SOTPSegment[],
    netDebt: number = 0,
    holdingDiscount: number = 15.0,
    marketPrice?: number
  ): Promise<SOTPValuationResult> {
    const params = new URLSearchParams({
      net_debt_crores: netDebt.toString(),
      holding_company_discount_pct: holdingDiscount.toString(),
    });
    if (marketPrice !== undefined) params.append('market_price', marketPrice.toString());
    return fetchJson<SOTPValuationResult>(
      `/companies/${encodeURIComponent(identifier)}/valuation/sotp?${params.toString()}`,
      {
        method: 'POST',
        body: JSON.stringify(segments),
      }
    );
  },

  // ---------------------------------------------------------------------------
  // Phase 6: Document Intelligence & Annual Report RAG
  // ---------------------------------------------------------------------------

  async getDocuments(ticker?: string): Promise<DocumentMetadataDTO[]> {
    const params = new URLSearchParams();
    if (ticker) params.append('ticker', ticker);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<DocumentMetadataDTO[]>(`/documents${qs}`);
  },

  async getCanonicalSections(): Promise<string[]> {
    return fetchJson<string[]>('/documents/sections/canonical');
  },

  async getDocumentDetail(documentId: number): Promise<DocumentDetailDTO> {
    return fetchJson<DocumentDetailDTO>(`/documents/${documentId}`);
  },

  async getDocumentPage(documentId: number, pageNumber: number): Promise<DocumentPageDTO> {
    return fetchJson<DocumentPageDTO>(`/documents/${documentId}/pages/${pageNumber}`);
  },

  async searchDocuments(query: DocumentRetrievalQuery): Promise<DocumentRetrievalResponse> {
    return fetchJson<DocumentRetrievalResponse>('/documents/search', {
      method: 'POST',
      body: JSON.stringify(query),
    });
  },

  async uploadDocument(
    file: File,
    ticker: string,
    fiscalYear: number,
    title?: string,
    sourceUrl?: string
  ): Promise<IngestionUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('ticker', ticker);
    formData.append('fiscal_year', fiscalYear.toString());
    if (title) formData.append('title', title);
    if (sourceUrl) formData.append('source_url', sourceUrl);

    const url = `${API_BASE_URL}/documents/upload`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      const message = errorBody?.error?.message || errorBody?.detail || `HTTP Error ${response.status}: ${response.statusText}`;
      throw new Error(message);
    }

    return response.json();
  },

  // ---------------------------------------------------------------------------
  // Phase 7: AI Analyst, Grounding, PIT, Research Reports, & Watchlist
  // ---------------------------------------------------------------------------

  async queryAIAnalyst(query: AIAnalystQuery): Promise<AIAnalystResponse> {
    return fetchJson<AIAnalystResponse>('/ai/query', {
      method: 'POST',
      body: JSON.stringify(query),
    });
  },

  async getSaidVsDid(ticker: string): Promise<ManagementSaidVsDidResponse> {
    return fetchJson<ManagementSaidVsDidResponse>(`/ai/said-vs-did/${encodeURIComponent(ticker)}`);
  },

  async runPointInTime(request: PointInTimeAnalysisRequest): Promise<PointInTimeAnalysisResponse> {
    return fetchJson<PointInTimeAnalysisResponse>('/ai/point-in-time', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async getResearchReport(companyId: number): Promise<CompanyResearchReport> {
    return fetchJson<CompanyResearchReport>(`/ai/research-report/${companyId}`);
  },

  async getWatchlist(): Promise<WatchlistItemDTO[]> {
    return fetchJson<WatchlistItemDTO[]>('/watchlist');
  },

  async addToWatchlist(ticker: string, notes?: string): Promise<WatchlistItemDTO> {
    const params = new URLSearchParams({ ticker });
    if (notes) params.append('notes', notes);
    return fetchJson<WatchlistItemDTO>(`/watchlist?${params.toString()}`, {
      method: 'POST',
    });
  },

  async removeFromWatchlist(ticker: string): Promise<{ success: boolean; ticker: string; message: string }> {
    return fetchJson<{ success: boolean; ticker: string; message: string }>(`/watchlist/${encodeURIComponent(ticker)}`, {
      method: 'DELETE',
    });
  },
};

export const api = ApiService;
export default ApiService;




