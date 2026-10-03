import React, { useState, useEffect, useCallback } from 'react';
import {
  TrendingUp,
  RefreshCw,
  Info,
  DollarSign,
  Activity,
  Layers,
  ArrowUpRight,
  BarChart3,
  X,
} from 'lucide-react';
import { ApiService } from '../services/api';
import {
  Company,
  CompanyFundamentalResponse,
  CompanyDuPontResponse,
  CompanyCommonSizeResponse,
  CalculatedMetric,
  PeriodFundamentalAnalysis,
  DuPontDecompositionResult,
} from '../types/api';

type ActiveAnalysisTab = 'profitability' | 'growth' | 'working_capital' | 'cash_quality' | 'dupont' | 'common_size';

export const FundamentalAnalysisView: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string>('INFY');
  const [statementType, setStatementType] = useState<'CONSOLIDATED' | 'STANDALONE'>('CONSOLIDATED');
  const [activeTab, setActiveTab] = useState<ActiveAnalysisTab>('profitability');
  const [commonSizeKind, setCommonSizeKind] = useState<'INCOME_STATEMENT' | 'BALANCE_SHEET'>('INCOME_STATEMENT');
  const [limitPeriods, setLimitPeriods] = useState<number>(5);

  const [fundamentalData, setFundamentalData] = useState<CompanyFundamentalResponse | null>(null);
  const [dupontData, setDupontData] = useState<CompanyDuPontResponse | null>(null);
  const [commonSizeData, setCommonSizeData] = useState<CompanyCommonSizeResponse | null>(null);

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Lineage Drawer State
  const [inspectMetric, setInspectMetric] = useState<{
    metric: CalculatedMetric;
    periodLabel: string;
    category: string;
  } | null>(null);

  // Load Companies list
  useEffect(() => {
    async function loadCompanies() {
      try {
        const list = await ApiService.getCompanies();
        setCompanies(list);
        if (list.length > 0 && !list.find(c => c.ticker === selectedTicker)) {
          setSelectedTicker(list[0].ticker);
        }
      } catch (err: any) {
        console.error('Failed to load companies:', err);
      }
    }
    loadCompanies();
  }, []);

  // Fetch Analytical Data
  const loadAnalysisData = useCallback(async () => {
    if (!selectedTicker) return;
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'dupont') {
        const res = await ApiService.getDuPontAnalysis(selectedTicker, statementType, limitPeriods);
        setDupontData(res);
      } else if (activeTab === 'common_size') {
        const res = await ApiService.getCommonSizeStatements(selectedTicker, commonSizeKind, statementType, limitPeriods);
        setCommonSizeData(res);
      } else {
        const res = await ApiService.getFundamentalAnalysis(selectedTicker, statementType, limitPeriods);
        setFundamentalData(res);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load fundamental analytical data');
    } finally {
      setLoading(false);
    }
  }, [selectedTicker, statementType, limitPeriods, activeTab, commonSizeKind]);

  useEffect(() => {
    loadAnalysisData();
  }, [loadAnalysisData]);

  const selectedCompany = companies.find(c => c.ticker === selectedTicker);

  return (
    <div className="view-container" style={{ padding: '1.5rem', maxWidth: '1440px', margin: '0 auto' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 800, margin: 0 }}>Fundamental Analysis Engine</h1>
            <span className="badge badge-success" style={{ fontSize: '0.75rem', fontWeight: 700 }}>PHASE 2 ACTIVE</span>
            <span className="badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.15)', color: 'var(--accent-primary)', fontSize: '0.75rem', fontWeight: 600 }}>
              Methodology v1.0.0
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.35rem', marginBottom: 0 }}>
            Deterministic financial ratios, growth trajectories, DuPont ROE decomposition, and common-size analysis with mathematical lineage.
          </p>
        </div>

        {/* Global Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Company Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Company:</label>
            <select
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value)}
              style={{
                backgroundColor: 'var(--bg-card)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-color)',
                padding: '0.45rem 0.75rem',
                borderRadius: '6px',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              {companies.map(c => (
                <option key={c.ticker} value={c.ticker}>
                  {c.ticker} - {c.trade_name || c.legal_name}
                </option>
              ))}
            </select>
          </div>

          {/* Statement Type */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Type:</label>
            <select
              value={statementType}
              onChange={(e) => setStatementType(e.target.value as any)}
              style={{
                backgroundColor: 'var(--bg-card)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-color)',
                padding: '0.45rem 0.75rem',
                borderRadius: '6px',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <option value="CONSOLIDATED">Consolidated</option>
              <option value="STANDALONE">Standalone</option>
            </select>
          </div>

          {/* Period Count */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Periods:</label>
            <select
              value={limitPeriods}
              onChange={(e) => setLimitPeriods(Number(e.target.value))}
              style={{
                backgroundColor: 'var(--bg-card)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-color)',
                padding: '0.45rem 0.75rem',
                borderRadius: '6px',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <option value={3}>3 Periods</option>
              <option value={5}>5 Periods</option>
              <option value={10}>10 Periods</option>
            </select>
          </div>

          {/* Refresh Button */}
          <button
            onClick={loadAnalysisData}
            disabled={loading}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.45rem 0.85rem' }}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            <span>Recalculate</span>
          </button>
        </div>
      </div>

      {/* Selected Company Summary Bar */}
      {selectedCompany && (
        <div style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '0.75rem 1.25rem',
          marginBottom: '1.25rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block' }}>Company Name</span>
              <strong style={{ fontSize: '0.95rem' }}>{selectedCompany.legal_name}</strong>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block' }}>Sector / Industry</span>
              <span style={{ fontSize: '0.85rem' }}>{selectedCompany.sector} &bull; {selectedCompany.industry}</span>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block' }}>ISIN / CIN</span>
              <span style={{ fontSize: '0.85rem', fontFamily: 'monospace' }}>{selectedCompany.isin}</span>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block' }}>Exchange</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{selectedCompany.primary_exchange}</span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              Deterministic Engine Active
            </span>
          </div>
        </div>
      )}

      {/* Navigation Sub-Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border-color)',
        marginBottom: '1.5rem',
        gap: '0.5rem',
        overflowX: 'auto'
      }}>
        {[
          { id: 'profitability', label: 'Profitability & Returns', icon: TrendingUp },
          { id: 'growth', label: 'Growth & CAGR Trajectory', icon: ArrowUpRight },
          { id: 'working_capital', label: 'Working Capital & Efficiency', icon: Activity },
          { id: 'cash_quality', label: 'Cash Quality & Earnings Integrity', icon: DollarSign },
          { id: 'dupont', label: 'DuPont ROE Decomposition', icon: Layers },
          { id: 'common_size', label: 'Common-Size Statements', icon: BarChart3 },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as ActiveAnalysisTab)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                padding: '0.65rem 1rem',
                border: 'none',
                background: 'none',
                borderBottom: isActive ? '2px solid var(--accent-primary)' : '2px solid transparent',
                color: isActive ? 'var(--accent-primary)' : 'var(--text-muted)',
                fontWeight: isActive ? 700 : 500,
                fontSize: '0.875rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease'
              }}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Error Banner */}
      {error && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '1rem',
          color: '#ef4444',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <Info size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <RefreshCw size={32} className="spin" style={{ margin: '0 auto 1rem', display: 'block', color: 'var(--accent-primary)' }} />
          <div>Computing fundamental analytics & ratios...</div>
        </div>
      )}

      {/* Tab 1: Profitability & Returns */}
      {!loading && activeTab === 'profitability' && fundamentalData && (
        <ProfitabilitySection
          periodsData={fundamentalData.periods_data}
          onInspectMetric={(metric, periodLabel) => setInspectMetric({ metric, periodLabel, category: 'Profitability' })}
        />
      )}

      {/* Tab 2: Growth Trajectory */}
      {!loading && activeTab === 'growth' && fundamentalData && (
        <GrowthSection
          periodsData={fundamentalData.periods_data}
          onInspectMetric={(metric, periodLabel) => setInspectMetric({ metric, periodLabel, category: 'Growth' })}
        />
      )}

      {/* Tab 3: Working Capital & Efficiency */}
      {!loading && activeTab === 'working_capital' && fundamentalData && (
        <WorkingCapitalSection
          periodsData={fundamentalData.periods_data}
          onInspectMetric={(metric, periodLabel) => setInspectMetric({ metric, periodLabel, category: 'Working Capital' })}
        />
      )}

      {/* Tab 4: Cash Quality */}
      {!loading && activeTab === 'cash_quality' && fundamentalData && (
        <CashQualitySection
          periodsData={fundamentalData.periods_data}
          onInspectMetric={(metric, periodLabel) => setInspectMetric({ metric, periodLabel, category: 'Cash Quality' })}
        />
      )}

      {/* Tab 5: DuPont ROE Decomposition */}
      {!loading && activeTab === 'dupont' && dupontData && (
        <DuPontSection
          periodsDuPont={dupontData.periods_dupont}
          onInspectMetric={(metric, periodLabel) => setInspectMetric({ metric, periodLabel, category: 'DuPont Analysis' })}
        />
      )}

      {/* Tab 6: Common-Size Statements */}
      {!loading && activeTab === 'common_size' && commonSizeData && (
        <CommonSizeSection
          data={commonSizeData}
          kind={commonSizeKind}
          onKindChange={(k) => setCommonSizeKind(k)}
        />
      )}

      {/* Metric Formula & Lineage Inspector Drawer / Modal */}
      {inspectMetric && (
        <MetricLineageDrawer
          data={inspectMetric}
          onClose={() => setInspectMetric(null)}
        />
      )}
    </div>
  );
};

// --------------------------------------------------------------------------------------
// SUB-SECTIONS
// --------------------------------------------------------------------------------------

interface SectionProps {
  periodsData: PeriodFundamentalAnalysis[];
  onInspectMetric: (metric: CalculatedMetric, periodLabel: string) => void;
}

const ProfitabilitySection: React.FC<SectionProps> = ({ periodsData, onInspectMetric }) => {
  const metricKeys = [
    { key: 'GROSS_MARGIN', label: 'Gross Profit Margin', highlight: false },
    { key: 'EBITDA_MARGIN', label: 'EBITDA Margin', highlight: false },
    { key: 'EBIT_MARGIN', label: 'EBIT Margin', highlight: false },
    { key: 'PAT_MARGIN', label: 'Net Profit Margin (PAT)', highlight: true },
    { key: 'ROCE', label: 'Return on Capital Employed (ROCE)', highlight: true },
    { key: 'ROE', label: 'Return on Equity (ROE)', highlight: true },
    { key: 'ROIC', label: 'Return on Invested Capital (ROIC)', highlight: true },
    { key: 'ROA', label: 'Return on Assets (ROA)', highlight: false },
  ];

  return (
    <div>
      {/* Latest Period Snapshot Cards */}
      {periodsData.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {['ROCE', 'ROE', 'ROIC', 'PAT_MARGIN'].map(key => {
            const m = periodsData[0].profitability[key];
            if (!m) return null;
            return (
              <div
                key={key}
                onClick={() => onInspectMetric(m, periodsData[0].period_label)}
                style={{
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '1.25rem',
                  cursor: 'pointer',
                  transition: 'border-color 0.2s',
                  position: 'relative'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                    {m.metric_label}
                  </span>
                  <Info size={14} style={{ color: 'var(--text-muted)' }} />
                </div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-primary)' }}>
                  {m.formatted_value}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  Period: <strong>{periodsData[0].period_label}</strong>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Multi-Period Tabular View */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Historical Profitability & Return Ratios</h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Click any metric row to inspect mathematical derivation</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>Metric</th>
                {periodsData.map(p => (
                  <th key={p.period_id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    {p.period_label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {metricKeys.map(meta => (
                <tr
                  key={meta.key}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    backgroundColor: meta.highlight ? 'rgba(59, 130, 246, 0.03)' : 'transparent',
                  }}
                >
                  <td style={{ padding: '0.75rem 1.25rem', fontWeight: meta.highlight ? 700 : 500 }}>
                    {meta.label}
                  </td>
                  {periodsData.map(p => {
                    const m = p.profitability[meta.key];
                    return (
                      <td
                        key={p.period_id}
                        onClick={() => m && onInspectMetric(m, p.period_label)}
                        style={{
                          textAlign: 'right',
                          padding: '0.75rem 1.25rem',
                          fontFamily: 'monospace',
                          fontWeight: meta.highlight ? 700 : 500,
                          cursor: m ? 'pointer' : 'default',
                          color: m?.value !== null && m?.value !== undefined && m.value < 0 ? '#ef4444' : 'inherit'
                        }}
                        title={m ? `Click to inspect: ${m.formula_expression}` : undefined}
                      >
                        {m ? m.formatted_value : '—'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const GrowthSection: React.FC<SectionProps> = ({ periodsData, onInspectMetric }) => {
  const yoyMetrics = [
    { key: 'REVENUE_YOY', label: 'Revenue YoY Growth' },
    { key: 'EBITDA_YOY', label: 'EBITDA YoY Growth' },
    { key: 'EBIT_YOY', label: 'EBIT YoY Growth' },
    { key: 'PAT_YOY', label: 'Net Profit (PAT) YoY Growth' },
    { key: 'CFO_YOY', label: 'Operating Cash Flow (CFO) YoY' },
    { key: 'FCF_YOY', label: 'Free Cash Flow (FCF) YoY' },
  ];

  const cagrMetrics = [
    { key: 'REVENUE_CAGR_3Y', label: 'Revenue 3-Year CAGR' },
    { key: 'EBITDA_CAGR_3Y', label: 'EBITDA 3-Year CAGR' },
    { key: 'PAT_CAGR_3Y', label: 'PAT 3-Year CAGR' },
    { key: 'CFO_CAGR_3Y', label: 'CFO 3-Year CAGR' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* YoY Growth Table */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Year-over-Year (YoY) Growth Trajectory</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>Metric</th>
                {periodsData.map(p => (
                  <th key={p.period_id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    {p.period_label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {yoyMetrics.map(meta => (
                <tr key={meta.key} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>{meta.label}</td>
                  {periodsData.map(p => {
                    const m = p.growth[meta.key];
                    const val = m?.value;
                    const isPositive = val !== null && val !== undefined && val > 0;
                    const isNegative = val !== null && val !== undefined && val < 0;
                    return (
                      <td
                        key={p.period_id}
                        onClick={() => m && onInspectMetric(m, p.period_label)}
                        style={{
                          textAlign: 'right',
                          padding: '0.75rem 1.25rem',
                          fontFamily: 'monospace',
                          cursor: m ? 'pointer' : 'default',
                          color: isPositive ? '#10b981' : isNegative ? '#ef4444' : 'inherit'
                        }}
                      >
                        {m ? m.formatted_value : '—'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* CAGR Table */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Compound Annual Growth Rate (CAGR)</h3>
          <p style={{ margin: '0.25rem 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Strict boundary verification applied. If base year is negative or zero, CAGR is safely marked undefined.
          </p>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>Trajectory Metric</th>
                {periodsData.map(p => (
                  <th key={p.period_id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    End: {p.period_label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {cagrMetrics.map(meta => (
                <tr key={meta.key} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>{meta.label}</td>
                  {periodsData.map(p => {
                    const m = p.growth[meta.key];
                    return (
                      <td
                        key={p.period_id}
                        onClick={() => m && onInspectMetric(m, p.period_label)}
                        style={{
                          textAlign: 'right',
                          padding: '0.75rem 1.25rem',
                          fontFamily: 'monospace',
                          cursor: m ? 'pointer' : 'default'
                        }}
                      >
                        {m ? m.formatted_value : '—'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const WorkingCapitalSection: React.FC<SectionProps> = ({ periodsData, onInspectMetric }) => {
  const latest = periodsData[0]?.working_capital;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Cash Conversion Cycle Visual Breakdown */}
      {latest && (
        <div style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '1.25rem'
        }}>
          <h3 style={{ margin: '0 0 1rem', fontSize: '1rem', fontWeight: 700 }}>
            Cash Conversion Cycle Breakdown ({periodsData[0].period_label})
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
            <div style={{ border: '1px solid var(--border-color)', borderRadius: '6px', padding: '1rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Days Sales Outstanding (DSO)</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-primary)', marginTop: '0.25rem' }}>
                {latest.DSO?.formatted_value || '—'}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Receivables collection time</div>
            </div>

            <div style={{ border: '1px solid var(--border-color)', borderRadius: '6px', padding: '1rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Days Inventory Outstanding (DIO)</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-primary)', marginTop: '0.25rem' }}>
                {latest.DIO?.formatted_value || '—'}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Inventory holding time</div>
            </div>

            <div style={{ border: '1px solid var(--border-color)', borderRadius: '6px', padding: '1rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Days Payables Outstanding (DPO)</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                {latest.DPO?.formatted_value || '—'}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Supplier credit duration</div>
            </div>

            <div style={{ border: '1px solid var(--accent-primary)', borderRadius: '6px', padding: '1rem', backgroundColor: 'rgba(59, 130, 246, 0.05)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--accent-primary)', fontWeight: 700 }}>Cash Conversion Cycle (CCC)</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-primary)', marginTop: '0.25rem' }}>
                {latest.CASH_CONVERSION_CYCLE?.formatted_value || '—'}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>DSO + DIO - DPO</div>
            </div>
          </div>
        </div>
      )}

      {/* Multi-Period Efficiency Table */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Efficiency & Liquidity Ratios</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>Metric</th>
                {periodsData.map(p => (
                  <th key={p.period_id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    {p.period_label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                { key: 'DSO', label: 'Days Sales Outstanding (DSO)' },
                { key: 'DIO', label: 'Days Inventory Outstanding (DIO)' },
                { key: 'DPO', label: 'Days Payables Outstanding (DPO)' },
                { key: 'CASH_CONVERSION_CYCLE', label: 'Cash Conversion Cycle (CCC)' },
                { key: 'ASSET_TURNOVER', label: 'Total Asset Turnover (x)' },
                { key: 'CURRENT_RATIO', label: 'Current Ratio (x)' },
                { key: 'QUICK_RATIO', label: 'Quick / Acid Test Ratio (x)' },
              ].map(meta => (
                <tr key={meta.key} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>{meta.label}</td>
                  {periodsData.map(p => {
                    const m = p.working_capital[meta.key];
                    return (
                      <td
                        key={p.period_id}
                        onClick={() => m && onInspectMetric(m, p.period_label)}
                        style={{
                          textAlign: 'right',
                          padding: '0.75rem 1.25rem',
                          fontFamily: 'monospace',
                          cursor: m ? 'pointer' : 'default'
                        }}
                      >
                        {m ? m.formatted_value : '—'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const CashQualitySection: React.FC<SectionProps> = ({ periodsData, onInspectMetric }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Overview Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        {periodsData.slice(0, 2).map(p => {
          const cfoPat = p.cash_quality['CFO_TO_PAT'];
          const accrual = p.cash_quality['SLOAN_ACCRUAL_RATIO'];
          const isHighQuality = cfoPat?.value !== null && cfoPat?.value !== undefined && cfoPat.value >= 1.0;

          return (
            <div
              key={p.period_id}
              style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '1.25rem'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase' }}>Period: {p.period_label}</span>
                <span className={`badge ${isHighQuality ? 'badge-success' : 'badge-warning'}`}>
                  {isHighQuality ? 'Strong Cash Realization' : 'Accrual Scrutiny'}
                </span>
              </div>
              <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>CFO / PAT Ratio:</span>
                  <strong style={{ fontFamily: 'monospace' }}>{cfoPat?.formatted_value || '—'}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Sloan Accruals (% Assets):</span>
                  <strong style={{ fontFamily: 'monospace' }}>{accrual?.formatted_value || '—'}</strong>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Multi-Period Cash Quality Table */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Cash Flow Realization & Accrual Metrics</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>Metric</th>
                {periodsData.map(p => (
                  <th key={p.period_id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    {p.period_label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                { key: 'CFO_TO_PAT', label: 'CFO to Net Profit (CFO / PAT)' },
                { key: 'FCF_TO_PAT', label: 'FCF to Net Profit (FCF / PAT)' },
                { key: 'SLOAN_ACCRUAL_RATIO', label: 'Sloan Balance Sheet Accrual Ratio' },
                { key: 'CFO_TO_TOTAL_DEBT', label: 'Operating Cash Flow to Total Debt' },
              ].map(meta => (
                <tr key={meta.key} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>{meta.label}</td>
                  {periodsData.map(p => {
                    const m = p.cash_quality[meta.key];
                    return (
                      <td
                        key={p.period_id}
                        onClick={() => m && onInspectMetric(m, p.period_label)}
                        style={{
                          textAlign: 'right',
                          padding: '0.75rem 1.25rem',
                          fontFamily: 'monospace',
                          cursor: m ? 'pointer' : 'default'
                        }}
                      >
                        {m ? m.formatted_value : '—'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const DuPontSection: React.FC<{
  periodsDuPont: DuPontDecompositionResult[];
  onInspectMetric: (metric: CalculatedMetric, periodLabel: string) => void;
}> = ({ periodsDuPont, onInspectMetric }) => {
  const [stepMode, setStepMode] = useState<'3_STEP' | '5_STEP'>('3_STEP');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Mode Selector */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>DuPont ROE Multiplicative Decomposition</h3>
          <p style={{ margin: '0.25rem 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Explains the underlying operational, efficiency, and financial leverage drivers of Return on Equity.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => setStepMode('3_STEP')}
            className={`btn ${stepMode === '3_STEP' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}
          >
            3-Step DuPont
          </button>
          <button
            onClick={() => setStepMode('5_STEP')}
            className={`btn ${stepMode === '5_STEP' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}
          >
            5-Step DuPont
          </button>
        </div>
      </div>

      {/* Decomposition Formula Visualizer */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        padding: '1.25rem'
      }}>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600 }}>
          {stepMode === '3_STEP' ? '3-STEP MULTIPLICATIVE IDENTITY:' : '5-STEP EXTENDED MULTIPLICATIVE IDENTITY:'}
        </div>
        <div style={{
          backgroundColor: 'var(--bg-subtle, rgba(255,255,255,0.03))',
          padding: '0.75rem 1rem',
          borderRadius: '6px',
          fontFamily: 'monospace',
          fontSize: '0.9rem',
          color: 'var(--accent-primary)',
          fontWeight: 700
        }}>
          {stepMode === '3_STEP'
            ? 'ROE = Net Profit Margin × Asset Turnover × Equity Multiplier'
            : 'ROE = Tax Burden × Interest Burden × Operating Margin × Asset Turnover × Equity Multiplier'}
        </div>
      </div>

      {/* Multi-Period Decomposition Table */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                  Decomposition Component
                </th>
                {periodsDuPont.map(p => (
                  <th key={p.period_id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    {p.period_label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {stepMode === '3_STEP' ? (
                <>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Net Profit Margin (%)</td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => onInspectMetric(p.step_3.net_profit_margin, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', cursor: 'pointer' }}
                      >
                        {p.step_3.net_profit_margin.formatted_value}
                      </td>
                    ))}
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Asset Turnover (x)</td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => onInspectMetric(p.step_3.asset_turnover, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', cursor: 'pointer' }}
                      >
                        {p.step_3.asset_turnover.formatted_value}
                      </td>
                    ))}
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Financial Leverage (Equity Multiplier x)</td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => onInspectMetric(p.step_3.equity_multiplier, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', cursor: 'pointer' }}
                      >
                        {p.step_3.equity_multiplier.formatted_value}
                      </td>
                    ))}
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'rgba(59, 130, 246, 0.05)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 800, color: 'var(--accent-primary)' }}>
                      Computed Return on Equity (ROE %)
                    </td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => onInspectMetric(p.step_3.computed_roe, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', fontWeight: 800, color: 'var(--accent-primary)', cursor: 'pointer' }}
                      >
                        {p.step_3.computed_roe.formatted_value}
                      </td>
                    ))}
                  </tr>
                </>
              ) : (
                <>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Tax Burden (PAT / EBT)</td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => p.step_5 && onInspectMetric(p.step_5.tax_burden, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', cursor: 'pointer' }}
                      >
                        {p.step_5?.tax_burden.formatted_value || '—'}
                      </td>
                    ))}
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Interest Burden (EBT / EBIT)</td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => p.step_5 && onInspectMetric(p.step_5.interest_burden, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', cursor: 'pointer' }}
                      >
                        {p.step_5?.interest_burden.formatted_value || '—'}
                      </td>
                    ))}
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Operating Margin (EBIT / Revenue %)</td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => p.step_5 && onInspectMetric(p.step_5.operating_margin, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', cursor: 'pointer' }}
                      >
                        {p.step_5?.operating_margin.formatted_value || '—'}
                      </td>
                    ))}
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Asset Turnover (x)</td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => p.step_5 && onInspectMetric(p.step_5.asset_turnover, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', cursor: 'pointer' }}
                      >
                        {p.step_5?.asset_turnover.formatted_value || '—'}
                      </td>
                    ))}
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Equity Multiplier (x)</td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => p.step_5 && onInspectMetric(p.step_5.equity_multiplier, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', cursor: 'pointer' }}
                      >
                        {p.step_5?.equity_multiplier.formatted_value || '—'}
                      </td>
                    ))}
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'rgba(59, 130, 246, 0.05)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 800, color: 'var(--accent-primary)' }}>
                      5-Step Computed ROE (%)
                    </td>
                    {periodsDuPont.map(p => (
                      <td
                        key={p.period_id}
                        onClick={() => p.step_5 && onInspectMetric(p.step_5.computed_roe, p.period_label)}
                        style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', fontWeight: 800, color: 'var(--accent-primary)', cursor: 'pointer' }}
                      >
                        {p.step_5?.computed_roe.formatted_value || '—'}
                      </td>
                    ))}
                  </tr>
                </>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const CommonSizeSection: React.FC<{
  data: CompanyCommonSizeResponse;
  kind: 'INCOME_STATEMENT' | 'BALANCE_SHEET';
  onKindChange: (k: 'INCOME_STATEMENT' | 'BALANCE_SHEET') => void;
}> = ({ data, kind, onKindChange }) => {
  const periods = data.periods_common_size;
  if (periods.length === 0) {
    return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No common-size data available.</div>;
  }

  const firstPeriodItems = periods[0].items;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Statement Switcher */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>Vertical Common-Size Financial Statement</h3>
          <p style={{ margin: '0.25rem 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {kind === 'INCOME_STATEMENT'
              ? 'Every revenue and expense line item standardized as a % of Total Revenue (100.0%).'
              : 'Every asset, liability, and equity component standardized as a % of Total Assets (100.0%).'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => onKindChange('INCOME_STATEMENT')}
            className={`btn ${kind === 'INCOME_STATEMENT' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}
          >
            Income Statement (% Rev)
          </button>
          <button
            onClick={() => onKindChange('BALANCE_SHEET')}
            className={`btn ${kind === 'BALANCE_SHEET' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}
          >
            Balance Sheet (% Assets)
          </button>
        </div>
      </div>

      {/* Common Size Multi-Period Table */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                  Line Item
                </th>
                {periods.map(p => (
                  <th key={p.period_id} colSpan={2} style={{ textAlign: 'center', padding: '0.75rem 0.5rem', fontWeight: 600, color: 'var(--text-muted)', borderLeft: '1px solid var(--border-color)' }}>
                    {p.period_label}
                  </th>
                ))}
              </tr>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.01)', borderBottom: '1px solid var(--border-color)', fontSize: '0.75rem' }}>
                <th style={{ padding: '0.35rem 1.25rem' }}></th>
                {periods.map(p => (
                  <React.Fragment key={p.period_id}>
                    <th style={{ textAlign: 'right', padding: '0.35rem 0.5rem', color: 'var(--text-muted)', borderLeft: '1px solid var(--border-color)' }}>
                      ₹ Cr
                    </th>
                    <th style={{ textAlign: 'right', padding: '0.35rem 0.5rem', color: 'var(--text-muted)' }}>
                      % of Base
                    </th>
                  </React.Fragment>
                ))}
              </tr>
            </thead>
            <tbody>
              {firstPeriodItems.map((item, idx) => {
                const isH = item.is_header;
                return (
                  <tr
                    key={item.item_key}
                    style={{
                      borderBottom: '1px solid var(--border-color)',
                      backgroundColor: isH ? 'rgba(59, 130, 246, 0.04)' : 'transparent',
                      fontWeight: isH ? 700 : 400
                    }}
                  >
                    <td style={{
                      padding: '0.65rem 1.25rem',
                      paddingLeft: `${1.25 + item.level * 1}rem`,
                      color: isH ? 'var(--accent-primary)' : 'inherit'
                    }}>
                      {item.item_label}
                    </td>
                    {periods.map(p => {
                      const curItem = p.items[idx] || item;
                      return (
                        <React.Fragment key={p.period_id}>
                          <td style={{
                            textAlign: 'right',
                            padding: '0.65rem 0.5rem',
                            fontFamily: 'monospace',
                            borderLeft: '1px solid var(--border-color)',
                            color: 'var(--text-muted)'
                          }}>
                            {curItem.raw_value.toLocaleString('en-IN', { maximumFractionDigits: 1 })}
                          </td>
                          <td style={{
                            textAlign: 'right',
                            padding: '0.65rem 0.75rem',
                            fontFamily: 'monospace',
                            fontWeight: isH ? 700 : 500,
                            color: isH ? 'var(--accent-primary)' : 'inherit'
                          }}>
                            {curItem.percent_of_base.toFixed(2)}%
                          </td>
                        </React.Fragment>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// --------------------------------------------------------------------------------------
// FORMULA & LINEAGE INSPECTOR MODAL
// --------------------------------------------------------------------------------------

const MetricLineageDrawer: React.FC<{
  data: {
    metric: CalculatedMetric;
    periodLabel: string;
    category: string;
  };
  onClose: () => void;
}> = ({ data, onClose }) => {
  const { metric, periodLabel, category } = data;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.65)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1.5rem',
      backdropFilter: 'blur(3px)'
    }}>
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '620px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        maxHeight: '90vh'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-primary)', fontSize: '0.7rem' }}>
                {category}
              </span>
              <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                {metric.methodology_version}
              </span>
            </div>
            <h2 style={{ margin: '0.35rem 0 0', fontSize: '1.2rem', fontWeight: 800 }}>{metric.metric_label}</h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '0.25rem',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Computed Value & Period */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>COMPUTED VALUE</span>
              <span style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--accent-primary)' }}>{metric.formatted_value}</span>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>PERIOD APPLIED</span>
              <span style={{ fontSize: '1rem', fontWeight: 700 }}>{periodLabel}</span>
            </div>
          </div>

          {/* Mathematical Formula Expression */}
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
              Deterministic Mathematical Formula
            </label>
            <div style={{
              backgroundColor: 'var(--bg-subtle, rgba(0,0,0,0.3))',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '0.85rem 1rem',
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              color: 'var(--accent-primary)'
            }}>
              {metric.formula_expression}
            </div>
          </div>

          {/* Exact Inputs Breakdown */}
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
              Input Parameters Lineage
            </label>
            <div style={{
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              overflow: 'hidden'
            }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                <thead>
                  <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                    <th style={{ textAlign: 'left', padding: '0.5rem 0.75rem', color: 'var(--text-muted)' }}>Input Parameter</th>
                    <th style={{ textAlign: 'right', padding: '0.5rem 0.75rem', color: 'var(--text-muted)' }}>Resolved Value</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(metric.inputs).map(([key, val]) => (
                    <tr key={key} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '0.5rem 0.75rem', fontFamily: 'monospace' }}>{key}</td>
                      <td style={{ textAlign: 'right', padding: '0.5rem 0.75rem', fontFamily: 'monospace', fontWeight: 600 }}>
                        {typeof val === 'number' ? val.toLocaleString('en-IN', { maximumFractionDigits: 2 }) : String(val)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Validation & Notes */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Calculation State:</span>
              <span className={`badge ${metric.is_valid ? 'badge-success' : 'badge-danger'}`} style={{ fontSize: '0.7rem' }}>
                {metric.is_valid ? 'Deterministic Validation PASSED' : 'Validation Check FAILED'}
              </span>
            </div>
            {metric.notes && (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                Note: {metric.notes}
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '0.85rem 1.5rem',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'flex-end',
          backgroundColor: 'rgba(255,255,255,0.01)'
        }}>
          <button
            onClick={onClose}
            className="btn btn-primary"
            style={{ fontSize: '0.85rem', padding: '0.45rem 1.25rem' }}
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
