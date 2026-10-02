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
};
