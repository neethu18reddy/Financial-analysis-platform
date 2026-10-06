import React, { useState, useEffect, useCallback } from 'react';
import {
  DollarSign,
  Layers,
  Sliders,
  RefreshCw,
  Info,
  AlertTriangle,
  X,
  Target,
  BarChart3,
  Percent,
} from 'lucide-react';
import { ApiService } from '../services/api';
import {
  Company,
  ValuationSummaryResponse,
  DCFValuationResult,
  SensitivityMatrixResult,
  DCFValuationInputs,
} from '../types/api';

type ValuationTab = 'dcf' | 'reverse_dcf' | 'multiples' | 'scenarios' | 'sensitivity' | 'banking';

export const ValuationWorkspaceView: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string>('RELIANCE');
  const [activeTab, setActiveTab] = useState<ValuationTab>('dcf');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Valuation summary data
  const [summary, setSummary] = useState<ValuationSummaryResponse | null>(null);
  const [marketPriceOverride, setMarketPriceOverride] = useState<number | ''>('');

  // Interactive DCF Controls
  const [dcfGrowth, setDcfGrowth] = useState<number>(11.5);
  const [dcfMargin, setDcfMargin] = useState<number>(18.0);
  const [dcfWacc, setDcfWacc] = useState<number>(11.2);
  const [dcfTerminalGrowth, setDcfTerminalGrowth] = useState<number>(5.0);
  const [dcfYears, setDcfYears] = useState<number>(5);
  const [customDcfResult, setCustomDcfResult] = useState<DCFValuationResult | null>(null);
  const [dcfCalculating, setDcfCalculating] = useState<boolean>(false);

  // Sensitivity Matrix State
  const [sensitivityMode, setSensitivityMode] = useState<'wacc_tg' | 'growth_margin'>('wacc_tg');
  const [sensitivityData, setSensitivityData] = useState<SensitivityMatrixResult | null>(null);

  // Inspection Modal
  const [inspectModal, setInspectModal] = useState<{
    title: string;
    category: string;
    formula?: string;
    details: Record<string, any>;
    notes?: string[];
  } | null>(null);

  // Initial Load of Companies
  useEffect(() => {
    async function loadCompanies() {
      try {
        const list = await ApiService.getCompanies();
        setCompanies(list);
        if (list.length > 0 && !selectedTicker) {
          setSelectedTicker(list[0].ticker);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load companies.');
      }
    }
    loadCompanies();
  }, []);

  // Fetch full valuation summary
  const fetchValuation = useCallback(async () => {
    if (!selectedTicker) return;
    try {
      setLoading(true);
      setError(null);
      const priceParam = typeof marketPriceOverride === 'number' && marketPriceOverride > 0 ? marketPriceOverride : undefined;
      const data = await ApiService.getValuationSummary(selectedTicker, priceParam);
      setSummary(data);

      if (data.dcf_result) {
        setCustomDcfResult(data.dcf_result);
        setDcfGrowth(data.dcf_result.inputs_applied.constant_revenue_growth_pct);
        setDcfMargin(data.dcf_result.inputs_applied.target_ebit_margin_pct);
        setDcfWacc(data.dcf_result.inputs_applied.wacc_pct || 11.2);
        setDcfTerminalGrowth(data.dcf_result.inputs_applied.terminal_growth_rate_pct);
        setDcfYears(data.dcf_result.inputs_applied.forecast_years);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load valuation analysis.');
    } finally {
      setLoading(false);
    }
  }, [selectedTicker, marketPriceOverride]);

  useEffect(() => {
    fetchValuation();
  }, [fetchValuation]);

  // Recalculate DCF on parameter change
  const handleRecalculateDCF = async () => {
    if (!selectedTicker || !summary) return;
    try {
      setDcfCalculating(true);
      const inputs: DCFValuationInputs = {
        forecast_years: dcfYears,
        constant_revenue_growth_pct: dcfGrowth,
        target_ebit_margin_pct: dcfMargin,
        effective_tax_rate_pct: 25.17,
        reinvestment_rate_pct: 35.0,
        wacc_pct: dcfWacc,
        risk_free_rate_pct: 7.1,
        equity_risk_premium_pct: 6.0,
        beta: 1.05,
        pre_tax_cost_of_debt_pct: 8.5,
        debt_to_capital_pct: 25.0,
        terminal_value_method: 'GORDON_GROWTH',
        terminal_growth_rate_pct: dcfTerminalGrowth,
        exit_ev_ebitda_multiple: 15.0,
        shares_outstanding_crores: summary.shares_outstanding_crores,
        total_debt_crores: summary.dcf_result?.total_debt,
        cash_and_investments_crores: summary.dcf_result?.cash_and_investments,
      };
      const res = await ApiService.runCustomDCF(selectedTicker, inputs, summary.current_market_price);
      setCustomDcfResult(res);
    } catch (err: any) {
      setError(err.message || 'DCF calculation error.');
    } finally {
      setDcfCalculating(false);
    }
  };

  // Fetch 2D Sensitivity Matrix
  const fetchSensitivity = useCallback(async () => {
    if (!selectedTicker || !summary) return;
    try {
      if (sensitivityMode === 'wacc_tg') {
        const matrix = await ApiService.getSensitivityWACCTG(
          selectedTicker,
          dcfWacc,
          dcfTerminalGrowth,
          dcfGrowth,
          dcfMargin,
          summary.current_market_price
        );
        setSensitivityData(matrix);
      } else {
        const matrix = await ApiService.getSensitivityGrowthMargin(
          selectedTicker,
          dcfGrowth,
          dcfMargin,
          dcfWacc,
          dcfTerminalGrowth,
          summary.current_market_price
        );
        setSensitivityData(matrix);
      }
    } catch (err: any) {
      console.error(err);
    }
  }, [selectedTicker, summary, sensitivityMode, dcfWacc, dcfTerminalGrowth, dcfGrowth, dcfMargin]);

  useEffect(() => {
    if (activeTab === 'sensitivity') {
      fetchSensitivity();
    }
  }, [activeTab, sensitivityMode, fetchSensitivity]);

  return (
    <div className="view-container" style={{ padding: '1.5rem', maxWidth: '1440px', margin: '0 auto' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 800 }}>Institutional Valuation Engine</h1>
            <span className="badge badge-success" style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}>
              Phase 4 Ready
            </span>
          </div>
          <p style={{ margin: '0.25rem 0 0', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Multi-model intrinsic valuation, reverse DCF expectation solver, relative multiples, and scenario simulations.
          </p>
        </div>

        {/* Company & Price Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <select
            value={selectedTicker}
            onChange={(e) => setSelectedTicker(e.target.value)}
            className="input-select"
            style={{ minWidth: '180px', padding: '0.5rem 0.75rem', fontWeight: 600 }}
          >
            {companies.map((c) => (
              <option key={c.id} value={c.ticker}>
                {c.ticker} - {c.legal_name}
              </option>
            ))}
          </select>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', backgroundColor: 'var(--bg-card)', padding: '0.35rem 0.75rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>CMP (₹):</span>
            <input
              type="number"
              placeholder={summary?.current_market_price ? `${summary.current_market_price}` : 'Price'}
              value={marketPriceOverride}
              onChange={(e) => setMarketPriceOverride(e.target.value ? parseFloat(e.target.value) : '')}
              style={{ width: '90px', background: 'transparent', border: 'none', color: '#fff', fontWeight: 700, fontSize: '0.9rem', outline: 'none' }}
            />
          </div>

          <button
            onClick={fetchValuation}
            disabled={loading}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 0.85rem' }}
          >
            <RefreshCw size={15} className={loading ? 'spin' : ''} />
            Recalculate
          </button>
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '1rem', borderRadius: '8px', color: '#f87171', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Composite Fair Value Summary Banner */}
      {summary && !loading && (
        <div style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '10px',
          padding: '1.25rem 1.5rem',
          marginBottom: '1.5rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.5rem',
          alignItems: 'center',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
        }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Composite Central Fair Value
            </span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.75rem', marginTop: '0.25rem' }}>
              <span style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--accent-primary)' }}>
                ₹{summary.composite_central_fair_value.toLocaleString()}
              </span>
              <span style={{
                fontSize: '0.95rem',
                fontWeight: 700,
                color: summary.composite_upside_downside_pct >= 0 ? '#10b981' : '#ef4444'
              }}>
                {summary.composite_upside_downside_pct >= 0 ? '+' : ''}
                {summary.composite_upside_downside_pct.toFixed(1)}% vs CMP (₹{summary.current_market_price})
              </span>
            </div>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Intrinsic Valuation Band
            </span>
            <div style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '0.25rem', color: '#f3f4f6' }}>
              ₹{summary.composite_fair_value_range_low.toLocaleString()} – ₹{summary.composite_fair_value_range_high.toLocaleString()}
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Market Cap: ₹{(summary.market_cap_crores / 1000).toFixed(1)}k Cr | {summary.sector}
            </span>
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.45, borderLeft: '3px solid var(--accent-primary)', paddingLeft: '0.75rem' }}>
              {summary.valuation_summary_text}
            </p>
          </div>
        </div>
      )}

      {/* Valuation Workspace Navigation Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', marginBottom: '1.5rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
        {[
          { id: 'dcf', label: '1. DCF Modeler (FCFF)', icon: <Sliders size={16} /> },
          { id: 'reverse_dcf', label: '2. Reverse DCF (Expectations)', icon: <Target size={16} /> },
          { id: 'multiples', label: '3. Relative Multiples', icon: <BarChart3 size={16} /> },
          { id: 'scenarios', label: '4. Scenario Analysis', icon: <Layers size={16} /> },
          { id: 'sensitivity', label: '5. 2D Sensitivity Grid', icon: <Percent size={16} /> },
          { id: 'banking', label: '6. Bank DDM / Justified P/B', icon: <DollarSign size={16} /> },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as ValuationTab)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.65rem 1.1rem',
              borderRadius: '6px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '0.875rem',
              backgroundColor: activeTab === tab.id ? 'var(--accent-primary)' : 'rgba(255,255,255,0.04)',
              color: activeTab === tab.id ? '#fff' : 'var(--text-muted)',
              transition: 'all 0.2s',
              whiteSpace: 'nowrap',
            }}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: DCF MODELER */}
      {activeTab === 'dcf' && (
        <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.5rem', alignItems: 'start' }}>
          {/* Left: Real-time Controls */}
          <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem', fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sliders size={18} color="var(--accent-primary)" /> DCF Assumption Levers
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                  <span>Revenue Growth CAGR:</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>{dcfGrowth.toFixed(1)}%</span>
                </div>
                <input
                  type="range"
                  min="2"
                  max="35"
                  step="0.5"
                  value={dcfGrowth}
                  onChange={(e) => setDcfGrowth(parseFloat(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                  <span>Target EBIT Margin:</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>{dcfMargin.toFixed(1)}%</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="40"
                  step="0.5"
                  value={dcfMargin}
                  onChange={(e) => setDcfMargin(parseFloat(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                  <span>Discount Rate (WACC):</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>{dcfWacc.toFixed(1)}%</span>
                </div>
                <input
                  type="range"
                  min="8"
                  max="18"
                  step="0.2"
                  value={dcfWacc}
                  onChange={(e) => setDcfWacc(parseFloat(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                  <span>Perpetual Terminal Growth (g):</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>{dcfTerminalGrowth.toFixed(1)}%</span>
                </div>
                <input
                  type="range"
                  min="2"
                  max="7"
                  step="0.25"
                  value={dcfTerminalGrowth}
                  onChange={(e) => setDcfTerminalGrowth(parseFloat(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                  <span>Forecast Horizon:</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>{dcfYears} Years</span>
                </div>
                <input
                  type="range"
                  min="3"
                  max="10"
                  step="1"
                  value={dcfYears}
                  onChange={(e) => setDcfYears(parseInt(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              <button
                onClick={handleRecalculateDCF}
                disabled={dcfCalculating}
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '0.5rem', padding: '0.6rem' }}
              >
                {dcfCalculating ? 'Recalculating...' : 'Update Valuation'}
              </button>
            </div>
          </div>

          {/* Right: Projected Pro-Forma Schedule & Valuation Bridge */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {customDcfResult && (
              <>
                {/* Result Highlights */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
                  <div style={{ backgroundColor: 'var(--bg-card)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Estimated Fair Value</span>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#10b981' }}>
                      ₹{customDcfResult.estimated_fair_value_per_share.toFixed(2)}
                    </div>
                    <span style={{ fontSize: '0.75rem', color: customDcfResult.upside_downside_pct && customDcfResult.upside_downside_pct >= 0 ? '#10b981' : '#ef4444' }}>
                      {customDcfResult.upside_downside_pct ? `${customDcfResult.upside_downside_pct > 0 ? '+' : ''}${customDcfResult.upside_downside_pct.toFixed(1)}% vs CMP` : ''}
                    </span>
                  </div>

                  <div style={{ backgroundColor: 'var(--bg-card)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Enterprise Value</span>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f3f4f6' }}>
                      ₹{(customDcfResult.enterprise_value / 1000).toFixed(1)}k Cr
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      PV Explicit: ₹{(customDcfResult.pv_explicit_forecast / 1000).toFixed(1)}k Cr
                    </span>
                  </div>

                  <div style={{ backgroundColor: 'var(--bg-card)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Net Debt Bridge</span>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: customDcfResult.net_debt <= 0 ? '#10b981' : '#f59e0b' }}>
                      {customDcfResult.net_debt <= 0 ? 'Net Cash' : `₹${(customDcfResult.net_debt / 1000).toFixed(1)}k Cr`}
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Cash: ₹{(customDcfResult.cash_and_investments / 1000).toFixed(1)}k Cr
                    </span>
                  </div>

                  <div style={{ backgroundColor: 'var(--bg-card)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Terminal Value % of EV</span>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: customDcfResult.terminal_diagnostics.is_terminal_value_dominant ? '#f59e0b' : '#10b981' }}>
                      {customDcfResult.terminal_diagnostics.terminal_value_pct_of_ev.toFixed(1)}%
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {customDcfResult.terminal_diagnostics.is_terminal_value_dominant ? 'Heavy Terminal Dependence' : 'Balanced Forecast'}
                    </span>
                  </div>
                </div>

                {/* Projections Table */}
                <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', overflow: 'hidden' }}>
                  <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700 }}>Pro-Forma Cash Flow Forecast Schedule (₹ Crores)</h3>
                    <button
                      onClick={() => setInspectModal({
                        title: 'DCF Mathematical Lineage & WACC Breakdown',
                        category: 'Free Cash Flow to Firm (FCFF)',
                        formula: 'EV = Sum(PV_Explicit) + PV(TerminalValue)',
                        details: {
                          WACC_Breakdown: customDcfResult.wacc_breakdown,
                          Formulas: customDcfResult.formula_lineage,
                          Diagnostics: customDcfResult.terminal_diagnostics,
                        },
                      })}
                      className="btn btn-secondary"
                      style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
                    >
                      <Info size={13} /> Inspect WACC & Formulas
                    </button>
                  </div>

                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                      <thead>
                        <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-color)' }}>
                          <th style={{ textAlign: 'left', padding: '0.65rem 1rem', color: 'var(--text-muted)' }}>Metric</th>
                          {customDcfResult.projections.map((p) => (
                            <th key={p.year_index} style={{ textAlign: 'right', padding: '0.65rem 1rem', color: 'var(--text-muted)' }}>
                              FY{p.fiscal_year} (Yr {p.year_index})
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                          <td style={{ padding: '0.65rem 1rem', fontWeight: 600 }}>Projected Revenue</td>
                          {customDcfResult.projections.map((p) => (
                            <td key={p.year_index} style={{ textAlign: 'right', padding: '0.65rem 1rem', fontFamily: 'monospace' }}>
                              ₹{p.revenue.toLocaleString()}
                            </td>
                          ))}
                        </tr>
                        <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                          <td style={{ padding: '0.65rem 1rem' }}>Operating Profit (EBIT)</td>
                          {customDcfResult.projections.map((p) => (
                            <td key={p.year_index} style={{ textAlign: 'right', padding: '0.65rem 1rem', fontFamily: 'monospace' }}>
                              ₹{p.operating_profit_ebit.toLocaleString()}
                            </td>
                          ))}
                        </tr>
                        <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                          <td style={{ padding: '0.65rem 1rem' }}>NOPAT (EBIT × (1 - Tax))</td>
                          {customDcfResult.projections.map((p) => (
                            <td key={p.year_index} style={{ textAlign: 'right', padding: '0.65rem 1rem', fontFamily: 'monospace' }}>
                              ₹{p.nopat.toLocaleString()}
                            </td>
                          ))}
                        </tr>
                        <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                          <td style={{ padding: '0.65rem 1rem' }}>Reinvestment (Capex + ΔNWC)</td>
                          {customDcfResult.projections.map((p) => (
                            <td key={p.year_index} style={{ textAlign: 'right', padding: '0.65rem 1rem', fontFamily: 'monospace', color: '#f87171' }}>
                              -₹{(p.capital_expenditure + p.change_in_nwc - p.depreciation_amortization).toLocaleString()}
                            </td>
                          ))}
                        </tr>
                        <tr style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'rgba(59, 130, 246, 0.05)' }}>
                          <td style={{ padding: '0.65rem 1rem', fontWeight: 700, color: 'var(--accent-primary)' }}>Free Cash Flow (FCFF)</td>
                          {customDcfResult.projections.map((p) => (
                            <td key={p.year_index} style={{ textAlign: 'right', padding: '0.65rem 1rem', fontFamily: 'monospace', fontWeight: 700, color: 'var(--accent-primary)' }}>
                              ₹{p.free_cash_flow.toLocaleString()}
                            </td>
                          ))}
                        </tr>
                        <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                          <td style={{ padding: '0.65rem 1rem', color: 'var(--text-muted)' }}>Discount Factor ({dcfWacc.toFixed(1)}%)</td>
                          {customDcfResult.projections.map((p) => (
                            <td key={p.year_index} style={{ textAlign: 'right', padding: '0.65rem 1rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>
                              {p.discount_factor.toFixed(4)}
                            </td>
                          ))}
                        </tr>
                        <tr style={{ backgroundColor: 'rgba(16, 185, 129, 0.05)' }}>
                          <td style={{ padding: '0.65rem 1rem', fontWeight: 800, color: '#10b981' }}>Discounted PV of FCFF</td>
                          {customDcfResult.projections.map((p) => (
                            <td key={p.year_index} style={{ textAlign: 'right', padding: '0.65rem 1rem', fontFamily: 'monospace', fontWeight: 800, color: '#10b981' }}>
                              ₹{p.discounted_fcf.toLocaleString()}
                            </td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: REVERSE DCF (EXPECTATION SOLVER) */}
      {activeTab === 'reverse_dcf' && summary?.reverse_dcf_result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700 }}>Market Expectation Solver</h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Reverse engineered from Current Market Price ₹{summary.reverse_dcf_result.current_market_price}
                </span>
              </div>
              <span className={`badge ${summary.reverse_dcf_result.plausibility_assessment === 'REALISTIC' ? 'badge-success' : summary.reverse_dcf_result.plausibility_assessment === 'CONSERVATIVE' ? 'badge-info' : 'badge-danger'}`} style={{ fontWeight: 700, padding: '0.35rem 0.75rem', fontSize: '0.85rem' }}>
                {summary.reverse_dcf_result.plausibility_assessment} EXPECTATION
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
              <div style={{ backgroundColor: 'rgba(0,0,0,0.25)', padding: '1.25rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Implied 5-Year Revenue CAGR</span>
                <div style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--accent-primary)', marginTop: '0.25rem' }}>
                  {summary.reverse_dcf_result.implied_revenue_cagr_pct.toFixed(1)}%
                </div>
                {summary.reverse_dcf_result.historical_revenue_cagr_3yr && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Historical 3-Yr CAGR: {summary.reverse_dcf_result.historical_revenue_cagr_3yr.toFixed(1)}%
                  </span>
                )}
              </div>

              <div style={{ backgroundColor: 'rgba(0,0,0,0.25)', padding: '1.25rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Target 5-Year Revenue Required</span>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f3f4f6', marginTop: '0.25rem' }}>
                  ₹{(summary.reverse_dcf_result.implied_5yr_revenue_target / 1000).toFixed(1)}k Cr
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Assumed EBIT Margin: {summary.reverse_dcf_result.assumed_ebit_margin_pct.toFixed(1)}%
                </span>
              </div>

              <div style={{ backgroundColor: 'rgba(0,0,0,0.25)', padding: '1.25rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Target 5-Year FCF Required</span>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#10b981', marginTop: '0.25rem' }}>
                  ₹{(summary.reverse_dcf_result.implied_5yr_fcf_target / 1000).toFixed(1)}k Cr
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Annual Free Cash Flow Target
                </span>
              </div>
            </div>

            <div style={{ backgroundColor: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.25)', padding: '1rem 1.25rem', borderRadius: '8px', color: '#93c5fd', fontSize: '0.9rem', lineHeight: 1.5 }}>
              <strong>Analyst Interpretation:</strong> {summary.reverse_dcf_result.plausibility_reasoning}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: RELATIVE MULTIPLES */}
      {activeTab === 'multiples' && summary?.multiples_result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
            {summary.multiples_result.multiples.map((m) => (
              <div
                key={m.multiple_name}
                style={{
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '1.25rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700 }}>{m.multiple_name}</h4>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
                      {m.current_multiple ? `${m.current_multiple.toFixed(1)}x` : '—'}
                    </span>
                  </div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#10b981', margin: '0.5rem 0' }}>
                    ₹{m.implied_fair_value_per_share.toFixed(2)}
                  </div>
                  <span style={{ fontSize: '0.75rem', color: m.upside_downside_pct && m.upside_downside_pct >= 0 ? '#10b981' : '#ef4444' }}>
                    {m.upside_downside_pct ? `${m.upside_downside_pct > 0 ? '+' : ''}${m.upside_downside_pct.toFixed(1)}% vs CMP` : ''}
                  </span>
                </div>

                <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <div>Target Multiple: <strong>{m.target_multiple_applied.toFixed(1)}x</strong></div>
                  <div>3-Yr Median: {m.historical_3yr_median ? `${m.historical_3yr_median.toFixed(1)}x` : '—'}</div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem' }}>
            <h4 style={{ margin: '0 0 0.75rem', fontSize: '0.95rem', fontWeight: 700 }}>Methodology & Valuation Limitations</h4>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
              {summary.multiples_result.methodology_notes.map((n, i) => (
                <li key={i}>{n}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* TAB 4: SCENARIOS (BEAR / BASE / BULL) */}
      {activeTab === 'scenarios' && summary?.scenario_result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
            {summary.scenario_result.scenarios.map((sc) => (
              <div
                key={sc.scenario_type}
                style={{
                  backgroundColor: 'var(--bg-card)',
                  border: `2px solid ${sc.scenario_type === 'BEAR' ? '#ef4444' : sc.scenario_type === 'BULL' ? '#10b981' : 'var(--accent-primary)'}`,
                  borderRadius: '8px',
                  padding: '1.25rem',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <h4 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800 }}>{sc.scenario_type} CASE</h4>
                  <span className="badge" style={{ backgroundColor: 'rgba(255,255,255,0.1)' }}>{sc.probability_weight_pct}% Weight</span>
                </div>

                <div style={{ fontSize: '1.8rem', fontWeight: 900, color: sc.scenario_type === 'BEAR' ? '#f87171' : sc.scenario_type === 'BULL' ? '#34d399' : 'var(--accent-primary)', marginBottom: '0.5rem' }}>
                  ₹{sc.estimated_fair_value_per_share.toFixed(2)}
                </div>

                <div style={{ fontSize: '0.85rem', marginBottom: '1rem', color: sc.upside_downside_pct && sc.upside_downside_pct >= 0 ? '#10b981' : '#ef4444', fontWeight: 700 }}>
                  {sc.upside_downside_pct ? `${sc.upside_downside_pct > 0 ? '+' : ''}${sc.upside_downside_pct.toFixed(1)}% vs CMP` : ''}
                </div>

                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  <div>Revenue Growth: <strong>{sc.revenue_growth_pct.toFixed(1)}%</strong></div>
                  <div>EBIT Margin: <strong>{sc.ebit_margin_pct.toFixed(1)}%</strong></div>
                  <div>WACC: <strong>{sc.wacc_pct.toFixed(1)}%</strong></div>
                </div>

                <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {sc.key_assumptions[0]}
                </div>
              </div>
            ))}
          </div>

          <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Probability-Weighted Expected Value</span>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-primary)' }}>
                ₹{summary.scenario_result.probability_weighted_fair_value.toFixed(2)}
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Risk / Reward Asymmetry:</span>
              <span className={`badge ${summary.scenario_result.risk_reward_skew === 'FAVORABLE' ? 'badge-success' : summary.scenario_result.risk_reward_skew === 'UNFAVORABLE' ? 'badge-danger' : 'badge-info'}`} style={{ fontWeight: 700 }}>
                {summary.scenario_result.risk_reward_skew}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: 2D SENSITIVITY GRID */}
      {activeTab === 'sensitivity' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => setSensitivityMode('wacc_tg')}
                className={sensitivityMode === 'wacc_tg' ? 'btn btn-primary' : 'btn btn-secondary'}
                style={{ fontSize: '0.85rem' }}
              >
                WACC vs Terminal Growth
              </button>
              <button
                onClick={() => setSensitivityMode('growth_margin')}
                className={sensitivityMode === 'growth_margin' ? 'btn btn-primary' : 'btn btn-secondary'}
                style={{ fontSize: '0.85rem' }}
              >
                Revenue Growth vs EBIT Margin
              </button>
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Green = Upside vs CMP (₹{summary?.current_market_price}) | Red = Downside
            </span>
          </div>

          {sensitivityData && (
            <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', overflow: 'hidden', padding: '1rem' }}>
              <h3 style={{ margin: '0 0 1rem', fontSize: '1rem', fontWeight: 700 }}>{sensitivityData.matrix_name}</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'center' }}>
                  <thead>
                    <tr>
                      <th style={{ padding: '0.75rem', backgroundColor: 'rgba(0,0,0,0.3)', color: 'var(--text-muted)' }}>
                        {sensitivityData.row_parameter_name} ↓ / {sensitivityData.col_parameter_name} →
                      </th>
                      {sensitivityData.col_values.map((c) => (
                        <th key={c} style={{ padding: '0.75rem', backgroundColor: 'rgba(0,0,0,0.2)', color: 'var(--text-muted)' }}>
                          {c}{sensitivityData.col_parameter_unit}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {sensitivityData.grid.map((row, rIdx) => (
                      <tr key={rIdx}>
                        <td style={{ padding: '0.75rem', fontWeight: 700, backgroundColor: 'rgba(0,0,0,0.2)', color: 'var(--text-muted)' }}>
                          {sensitivityData.row_values[rIdx]}{sensitivityData.row_parameter_unit}
                        </td>
                        {row.map((cell, cIdx) => {
                          const isBase = sensitivityData.row_values[rIdx] === sensitivityData.base_row_value && sensitivityData.col_values[cIdx] === sensitivityData.base_col_value;
                          const isUpside = cell.upside_downside_pct && cell.upside_downside_pct >= 0;
                          return (
                            <td
                              key={cIdx}
                              style={{
                                padding: '0.75rem',
                                fontFamily: 'monospace',
                                fontWeight: isBase ? 900 : 600,
                                backgroundColor: isUpside ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                                color: isUpside ? '#34d399' : '#f87171',
                                border: isBase ? '2px solid var(--accent-primary)' : '1px solid var(--border-color)',
                              }}
                            >
                              ₹{cell.fair_value_per_share.toFixed(0)}
                              <div style={{ fontSize: '0.65rem', opacity: 0.8 }}>
                                {cell.upside_downside_pct ? `${cell.upside_downside_pct > 0 ? '+' : ''}${cell.upside_downside_pct.toFixed(0)}%` : ''}
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 6: BANKING / FINANCIAL INSTITUTIONS */}
      {activeTab === 'banking' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ backgroundColor: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.25)', padding: '1.25rem', borderRadius: '8px' }}>
            <h3 style={{ margin: '0 0 0.5rem', fontSize: '1rem', fontWeight: 700, color: '#93c5fd' }}>
              Financial Institutions Valuation Governance
            </h3>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#bfdbfe', lineHeight: 1.5 }}>
              Standard FCFF DCF models are structurally invalid for Banks and NBFCs because debt constitutes operating inventory (deposits/borrowings) and interest is a direct cost of goods sold. The platform employs a Multi-Stage Dividend Discount Model (DDM) constrained by RBI Tier-1 Capital Adequacy along with Gordon Justified P/B analysis.
            </p>
          </div>

          {summary?.bank_valuation_result && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
              <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>DDM Fair Value Per Share</span>
                <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#10b981', marginTop: '0.25rem' }}>
                  ₹{summary.bank_valuation_result.ddm_fair_value_per_share.toFixed(2)}
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Multi-Stage Dividend Discount Model
                </span>
              </div>

              <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Gordon Justified P/B Multiple</span>
                <div style={{ fontSize: '1.8rem', fontWeight: 900, color: 'var(--accent-primary)', marginTop: '0.25rem' }}>
                  {summary.bank_valuation_result.justified_pb_multiple.toFixed(2)}x
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  (ROE - g) / (Ke - g)
                </span>
              </div>

              <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Justified P/B Fair Value</span>
                <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#f3f4f6', marginTop: '0.25rem' }}>
                  ₹{summary.bank_valuation_result.justified_pb_fair_value_per_share.toFixed(2)}
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Book Value: ₹{summary.bank_valuation_result.current_book_value_per_share.toFixed(2)}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Forensic Lineage & Formula Inspector Modal */}
      {inspectModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.8)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000,
          padding: '1rem',
        }}>
          <div style={{
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '10px',
            width: '100%',
            maxWidth: '650px',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '1.5rem',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>{inspectModal.title}</h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{inspectModal.category}</span>
              </div>
              <button onClick={() => setInspectModal(null)} className="btn btn-secondary" style={{ padding: '0.35rem' }}>
                <X size={18} />
              </button>
            </div>

            {inspectModal.formula && (
              <div style={{ backgroundColor: 'rgba(0,0,0,0.3)', padding: '0.75rem 1rem', borderRadius: '6px', fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--accent-primary)', marginBottom: '1rem' }}>
                {inspectModal.formula}
              </div>
            )}

            <pre style={{ backgroundColor: 'rgba(0,0,0,0.4)', padding: '1rem', borderRadius: '6px', fontSize: '0.8rem', overflowX: 'auto', color: '#e5e7eb', maxHeight: '350px' }}>
              {JSON.stringify(inspectModal.details, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
