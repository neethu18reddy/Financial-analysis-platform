import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2,
  FileCheck2,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  Info,
  Search,
  ExternalLink,
  Split,
  Database,
  ArrowRightLeft,
  X,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';
import { ApiService } from '../services/api';
import {
  Company,
  CompanyDetail,
  CompanyStatementsResponse,
  MultiPeriodFinancialSet,
  ValidationAuditReport,
  DataProvenance,
  CorporateAction,
  SourceProviderMetadata,
} from '../types/api';

type StatementTab = 'income' | 'balance' | 'cashflow' | 'actions' | 'sources';
type DisplayUnit = 'CRORES' | 'LAKHS' | 'MILLIONS';

export const FinancialDataEngineView: React.FC = () => {
  // State
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string>('RELIANCE');
  const [companyDetail, setCompanyDetail] = useState<CompanyDetail | null>(null);
  const [statementsData, setStatementsData] = useState<CompanyStatementsResponse | null>(null);
  const [statementType, setStatementType] = useState<'CONSOLIDATED' | 'STANDALONE'>('CONSOLIDATED');
  const [activeTab, setActiveTab] = useState<StatementTab>('income');
  const [displayUnit, setDisplayUnit] = useState<DisplayUnit>('CRORES');
  const [validationReport, setValidationReport] = useState<ValidationAuditReport | null>(null);
  const [corporateActions, setCorporateActions] = useState<CorporateAction[]>([]);
  const [sourcesList, setSourcesList] = useState<SourceProviderMetadata[]>([]);
  
  // Drawers & Modals
  const [selectedProvenance, setSelectedProvenance] = useState<DataProvenance[] | null>(null);
  const [provenanceFieldName, setProvenanceFieldName] = useState<string>('');
  const [isValidationDrawerOpen, setIsValidationDrawerOpen] = useState<boolean>(false);
  
  // Search & Loading
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Load Companies list
  useEffect(() => {
    async function loadCompanies() {
      try {
        const list = await ApiService.getCompanies();
        setCompanies(list);
        if (list.length > 0 && !selectedTicker) {
          setSelectedTicker(list[0].ticker);
        }
      } catch (err: any) {
        console.error('Failed to load companies:', err);
      }
    }
    loadCompanies();
  }, []);

  // Load Company Data & Statements
  const fetchCompanyFinancials = useCallback(async (ticker: string, stType: 'CONSOLIDATED' | 'STANDALONE') => {
    setLoading(true);
    setError(null);
    try {
      const [detail, stmts, valRep, actions, sources] = await Promise.all([
        ApiService.getCompanyDetail(ticker),
        ApiService.getFinancialStatements(ticker, stType, 5),
        ApiService.getValidationReport(ticker),
        ApiService.getCorporateActions(ticker),
        ApiService.getSources(),
      ]);
      setCompanyDetail(detail);
      setStatementsData(stmts);
      setValidationReport(valRep);
      setCorporateActions(actions);
      setSourcesList(sources);
    } catch (err: any) {
      setError(err.message || 'Failed to load financial statements');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedTicker) {
      fetchCompanyFinancials(selectedTicker, statementType);
    }
  }, [selectedTicker, statementType, fetchCompanyFinancials]);

  // Unit conversion helper
  const formatVal = (valInCrores: number | null | undefined): string => {
    if (valInCrores === null || valInCrores === undefined) return '-';
    let scaled = valInCrores;
    if (displayUnit === 'LAKHS') scaled = valInCrores * 100;
    else if (displayUnit === 'MILLIONS') scaled = valInCrores * 10;
    return scaled.toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  // Open Provenance drawer for entity
  const handleInspectProvenance = async (entityType: string, entityId: number, fieldName: string) => {
    try {
      const provs = await ApiService.getProvenance(entityType, entityId);
      const filtered = provs.filter((p) => !fieldName || p.field_name === fieldName);
      setSelectedProvenance(filtered.length > 0 ? filtered : provs);
      setProvenanceFieldName(fieldName);
    } catch (err) {
      console.error('Failed to load provenance:', err);
    }
  };

  const filteredCompanies = companies.filter(
    (c) =>
      c.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.legal_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.sector.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const periods = statementsData?.periods_data || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Header & Search Bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          backgroundColor: 'var(--bg-card)',
          padding: '1.25rem 1.5rem',
          borderRadius: 8,
          border: '1px solid var(--border-color)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 8,
              backgroundColor: 'rgba(59, 130, 246, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-primary)',
            }}
          >
            <Building2 size={24} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0 }}>
                {companyDetail?.legal_name || selectedTicker}
              </h2>
              <span
                style={{
                  fontSize: '0.75rem',
                  padding: '0.2rem 0.6rem',
                  backgroundColor: 'rgba(59, 130, 246, 0.2)',
                  color: 'var(--accent-primary)',
                  borderRadius: 4,
                  fontWeight: 600,
                }}
              >
                {companyDetail?.primary_exchange}:{companyDetail?.ticker}
              </span>
              <span
                style={{
                  fontSize: '0.75rem',
                  padding: '0.2rem 0.6rem',
                  backgroundColor: 'var(--bg-dark)',
                  color: 'var(--text-muted)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 4,
                }}
              >
                ISIN: {companyDetail?.isin}
              </span>
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.35rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <span>Sector: <strong style={{ color: 'var(--text-primary)' }}>{companyDetail?.sector}</strong></span>
              <span>•</span>
              <span>CIN: {companyDetail?.cin}</span>
              <span>•</span>
              <span>State: {companyDetail?.registered_state || 'India'}</span>
            </div>
          </div>
        </div>

        {/* Company Quick Selector Dropdown & Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search ticker, sector..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                padding: '0.45rem 0.75rem 0.45rem 2.2rem',
                backgroundColor: 'var(--bg-dark)',
                border: '1px solid var(--border-color)',
                borderRadius: 6,
                color: 'var(--text-primary)',
                fontSize: '0.85rem',
                width: 180,
              }}
            />
          </div>

          <select
            value={selectedTicker}
            onChange={(e) => setSelectedTicker(e.target.value)}
            style={{
              padding: '0.45rem 0.75rem',
              backgroundColor: 'var(--bg-dark)',
              border: '1px solid var(--border-color)',
              borderRadius: 6,
              color: 'var(--text-primary)',
              fontSize: '0.85rem',
              cursor: 'pointer',
            }}
          >
            {filteredCompanies.map((c) => (
              <option key={c.ticker} value={c.ticker}>
                {c.ticker} - {c.legal_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Control Toolbar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          backgroundColor: 'var(--bg-card)',
          padding: '0.75rem 1.25rem',
          borderRadius: 8,
          border: '1px solid var(--border-color)',
        }}
      >
        {/* Navigation Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => setActiveTab('income')}
            className={`btn ${activeTab === 'income' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <TrendingUp size={16} />
            Income Statement
          </button>
          <button
            onClick={() => setActiveTab('balance')}
            className={`btn ${activeTab === 'balance' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <FileSpreadsheet size={16} />
            Balance Sheet
          </button>
          <button
            onClick={() => setActiveTab('cashflow')}
            className={`btn ${activeTab === 'cashflow' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <ArrowRightLeft size={16} />
            Cash Flows
          </button>
          <button
            onClick={() => setActiveTab('actions')}
            className={`btn ${activeTab === 'actions' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <Split size={16} />
            Corporate Actions ({corporateActions.length})
          </button>
          <button
            onClick={() => setActiveTab('sources')}
            className={`btn ${activeTab === 'sources' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <Database size={16} />
            Sources & Compliance
          </button>
        </div>

        {/* View Configs: Consolidated/Standalone & Units */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Statement Type Toggle */}
          <div
            style={{
              display: 'flex',
              backgroundColor: 'var(--bg-dark)',
              padding: '0.2rem',
              borderRadius: 6,
              border: '1px solid var(--border-color)',
            }}
          >
            <button
              onClick={() => setStatementType('CONSOLIDATED')}
              style={{
                padding: '0.3rem 0.65rem',
                fontSize: '0.75rem',
                fontWeight: 600,
                borderRadius: 4,
                backgroundColor: statementType === 'CONSOLIDATED' ? 'var(--accent-primary)' : 'transparent',
                color: statementType === 'CONSOLIDATED' ? '#fff' : 'var(--text-muted)',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              Consolidated
            </button>
            <button
              onClick={() => setStatementType('STANDALONE')}
              style={{
                padding: '0.3rem 0.65rem',
                fontSize: '0.75rem',
                fontWeight: 600,
                borderRadius: 4,
                backgroundColor: statementType === 'STANDALONE' ? 'var(--accent-primary)' : 'transparent',
                color: statementType === 'STANDALONE' ? '#fff' : 'var(--text-muted)',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              Standalone
            </button>
          </div>

          {/* Unit Toggle */}
          <select
            value={displayUnit}
            onChange={(e) => setDisplayUnit(e.target.value as DisplayUnit)}
            style={{
              padding: '0.35rem 0.65rem',
              backgroundColor: 'var(--bg-dark)',
              border: '1px solid var(--border-color)',
              borderRadius: 6,
              color: 'var(--text-primary)',
              fontSize: '0.8rem',
              cursor: 'pointer',
            }}
          >
            <option value="CRORES">Units: INR Crores (₹ Cr)</option>
            <option value="LAKHS">Units: INR Lakhs (₹ L)</option>
            <option value="MILLIONS">Units: INR Millions</option>
          </select>

          {/* Validation Inspector Trigger */}
          <button
            onClick={() => setIsValidationDrawerOpen(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.35rem 0.75rem',
              borderRadius: 6,
              border: 'none',
              backgroundColor:
                validationReport?.is_fully_reconciled
                  ? 'rgba(16, 185, 129, 0.15)'
                  : 'rgba(239, 68, 68, 0.15)',
              color: validationReport?.is_fully_reconciled ? 'var(--status-healthy)' : 'var(--status-error)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            {validationReport?.is_fully_reconciled ? (
              <CheckCircle2 size={16} />
            ) : (
              <AlertTriangle size={16} />
            )}
            {validationReport?.is_fully_reconciled
              ? `Reconciled (${validationReport?.passed_checks}/${validationReport?.total_checks})`
              : `Discrepancy (${validationReport?.failed_checks} failed)`}
          </button>
        </div>
      </div>

      {/* Main Financial Tables Content */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          Loading deterministic financial statements...
        </div>
      ) : error ? (
        <div
          style={{
            padding: '1.5rem',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid var(--status-error)',
            borderRadius: 8,
            color: 'var(--status-error)',
          }}
        >
          {error}
        </div>
      ) : (
        <div
          style={{
            backgroundColor: 'var(--bg-card)',
            borderRadius: 8,
            border: '1px solid var(--border-color)',
            overflow: 'hidden',
          }}
        >
          {/* Income Statement View */}
          {activeTab === 'income' && (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--bg-dark)', borderBottom: '1px solid var(--border-color)' }}>
                    <th style={{ textAlign: 'left', padding: '0.85rem 1.25rem', width: '35%' }}>
                      Line Item (Click row to trace provenance)
                    </th>
                    {periods.map((p) => (
                      <th key={p.period.id} style={{ textAlign: 'right', padding: '0.85rem 1.25rem' }}>
                        <div>{p.period.period_label}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>
                          Ended {p.period.end_date}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {/* Revenue Section */}
                  <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)', fontWeight: 700 }}>
                    <td colSpan={periods.length + 1} style={{ padding: '0.65rem 1.25rem', color: 'var(--accent-primary)' }}>
                      REVENUE & OPERATING INCOME
                    </td>
                  </tr>
                  <TableRowClickable
                    label="Revenue from Operations"
                    fieldName="revenue_from_operations"
                    periods={periods}
                    getter={(p) => p.income_statement?.revenue_from_operations}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'revenue_from_operations')}
                  />
                  <TableRowClickable
                    label="Other Income"
                    fieldName="other_income"
                    periods={periods}
                    getter={(p) => p.income_statement?.other_income}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'other_income')}
                  />
                  <TableRowClickable
                    label="Total Revenue"
                    fieldName="total_revenue"
                    periods={periods}
                    getter={(p) => p.income_statement?.total_revenue}
                    formatter={formatVal}
                    isBold
                    isHighlight
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'total_revenue')}
                  />

                  {/* Expenses Section */}
                  <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)', fontWeight: 700 }}>
                    <td colSpan={periods.length + 1} style={{ padding: '0.65rem 1.25rem', color: 'var(--accent-primary)' }}>
                      EXPENSES & OPERATING COSTS
                    </td>
                  </tr>
                  <TableRowClickable
                    label="Cost of Materials Consumed"
                    fieldName="cost_of_materials_consumed"
                    periods={periods}
                    getter={(p) => p.income_statement?.cost_of_materials_consumed}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'cost_of_materials_consumed')}
                  />
                  <TableRowClickable
                    label="Purchases of Stock-in-Trade"
                    fieldName="purchases_of_stock_in_trade"
                    periods={periods}
                    getter={(p) => p.income_statement?.purchases_of_stock_in_trade}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'purchases_of_stock_in_trade')}
                  />
                  <TableRowClickable
                    label="Employee Benefit Expenses"
                    fieldName="employee_benefit_expenses"
                    periods={periods}
                    getter={(p) => p.income_statement?.employee_benefit_expenses}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'employee_benefit_expenses')}
                  />
                  <TableRowClickable
                    label="Finance Costs"
                    fieldName="finance_costs"
                    periods={periods}
                    getter={(p) => p.income_statement?.finance_costs}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'finance_costs')}
                  />
                  <TableRowClickable
                    label="Depreciation & Amortization"
                    fieldName="depreciation_and_amortization"
                    periods={periods}
                    getter={(p) => p.income_statement?.depreciation_and_amortization}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'depreciation_and_amortization')}
                  />
                  <TableRowClickable
                    label="Other Expenses"
                    fieldName="other_expenses"
                    periods={periods}
                    getter={(p) => p.income_statement?.other_expenses}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'other_expenses')}
                  />
                  <TableRowClickable
                    label="Total Expenses"
                    fieldName="total_expenses"
                    periods={periods}
                    getter={(p) => p.income_statement?.total_expenses}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'total_expenses')}
                  />

                  {/* Profitability Section */}
                  <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)', fontWeight: 700 }}>
                    <td colSpan={periods.length + 1} style={{ padding: '0.65rem 1.25rem', color: 'var(--accent-primary)' }}>
                      PROFITABILITY & TAX
                    </td>
                  </tr>
                  <TableRowClickable
                    label="Profit Before Tax (PBT)"
                    fieldName="profit_before_tax"
                    periods={periods}
                    getter={(p) => p.income_statement?.profit_before_tax}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'profit_before_tax')}
                  />
                  <TableRowClickable
                    label="Total Tax Expense"
                    fieldName="total_tax_expense"
                    periods={periods}
                    getter={(p) => p.income_statement?.total_tax_expense}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'total_tax_expense')}
                  />
                  <TableRowClickable
                    label="Profit After Tax (PAT)"
                    fieldName="profit_after_tax"
                    periods={periods}
                    getter={(p) => p.income_statement?.profit_after_tax}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'profit_after_tax')}
                  />
                  <TableRowClickable
                    label="Net Profit Attributable to Owners"
                    fieldName="net_profit_attributable_to_owners"
                    periods={periods}
                    getter={(p) => p.income_statement?.net_profit_attributable_to_owners}
                    formatter={formatVal}
                    isBold
                    isHighlight
                    onInspect={(pId) => handleInspectProvenance('income_statements', pId, 'net_profit_attributable_to_owners')}
                  />

                  {/* EPS */}
                  <tr style={{ borderTop: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontWeight: 600 }}>Basic EPS (₹ / Share)</td>
                    {periods.map((p) => (
                      <td key={p.period.id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontWeight: 600 }}>
                        ₹{p.income_statement?.basic_eps?.toFixed(2) || '-'}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {/* Balance Sheet View */}
          {activeTab === 'balance' && (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--bg-dark)', borderBottom: '1px solid var(--border-color)' }}>
                    <th style={{ textAlign: 'left', padding: '0.85rem 1.25rem', width: '35%' }}>
                      Line Item (Ind AS Schedule III Format)
                    </th>
                    {periods.map((p) => (
                      <th key={p.period.id} style={{ textAlign: 'right', padding: '0.85rem 1.25rem' }}>
                        <div>{p.period.period_label}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>
                          As on {p.period.end_date}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {/* Non Current Assets */}
                  <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)', fontWeight: 700 }}>
                    <td colSpan={periods.length + 1} style={{ padding: '0.65rem 1.25rem', color: 'var(--accent-primary)' }}>
                      NON-CURRENT ASSETS
                    </td>
                  </tr>
                  <TableRowClickable
                    label="Property, Plant and Equipment"
                    fieldName="property_plant_equipment"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.property_plant_equipment}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'property_plant_equipment')}
                  />
                  <TableRowClickable
                    label="Capital Work-in-Progress (CWIP)"
                    fieldName="capital_work_in_progress"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.capital_work_in_progress}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'capital_work_in_progress')}
                  />
                  <TableRowClickable
                    label="Goodwill & Intangible Assets"
                    fieldName="goodwill_and_intangibles"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.goodwill_and_intangibles}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'goodwill_and_intangibles')}
                  />
                  <TableRowClickable
                    label="Non-Current Investments"
                    fieldName="non_current_investments"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.non_current_investments}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'non_current_investments')}
                  />
                  <TableRowClickable
                    label="Total Non-Current Assets"
                    fieldName="total_non_current_assets"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.total_non_current_assets}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'total_non_current_assets')}
                  />

                  {/* Current Assets */}
                  <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)', fontWeight: 700 }}>
                    <td colSpan={periods.length + 1} style={{ padding: '0.65rem 1.25rem', color: 'var(--accent-primary)' }}>
                      CURRENT ASSETS
                    </td>
                  </tr>
                  <TableRowClickable
                    label="Inventories"
                    fieldName="inventories"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.inventories}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'inventories')}
                  />
                  <TableRowClickable
                    label="Trade Receivables"
                    fieldName="trade_receivables"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.trade_receivables}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'trade_receivables')}
                  />
                  <TableRowClickable
                    label="Cash & Cash Equivalents"
                    fieldName="cash_and_cash_equivalents"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.cash_and_cash_equivalents}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'cash_and_cash_equivalents')}
                  />
                  <TableRowClickable
                    label="Total Current Assets"
                    fieldName="total_current_assets"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.total_current_assets}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'total_current_assets')}
                  />

                  {/* TOTAL ASSETS */}
                  <TableRowClickable
                    label="TOTAL ASSETS"
                    fieldName="total_assets"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.total_assets}
                    formatter={formatVal}
                    isBold
                    isHighlight
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'total_assets')}
                  />

                  {/* EQUITY */}
                  <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)', fontWeight: 700 }}>
                    <td colSpan={periods.length + 1} style={{ padding: '0.65rem 1.25rem', color: 'var(--accent-primary)' }}>
                      EQUITY & SHAREHOLDERS' FUNDS
                    </td>
                  </tr>
                  <TableRowClickable
                    label="Equity Share Capital"
                    fieldName="equity_share_capital"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.equity_share_capital}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'equity_share_capital')}
                  />
                  <TableRowClickable
                    label="Other Equity & Reserves"
                    fieldName="other_equity_and_reserves"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.other_equity_and_reserves}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'other_equity_and_reserves')}
                  />
                  <TableRowClickable
                    label="Total Equity"
                    fieldName="total_equity"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.total_equity}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'total_equity')}
                  />

                  {/* LIABILITIES */}
                  <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)', fontWeight: 700 }}>
                    <td colSpan={periods.length + 1} style={{ padding: '0.65rem 1.25rem', color: 'var(--accent-primary)' }}>
                      LIABILITIES (NON-CURRENT & CURRENT)
                    </td>
                  </tr>
                  <TableRowClickable
                    label="Non-Current Borrowings (Long Term Debt)"
                    fieldName="non_current_borrowings"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.non_current_borrowings}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'non_current_borrowings')}
                  />
                  <TableRowClickable
                    label="Total Non-Current Liabilities"
                    fieldName="total_non_current_liabilities"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.total_non_current_liabilities}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'total_non_current_liabilities')}
                  />
                  <TableRowClickable
                    label="Current Borrowings (Short Term Debt)"
                    fieldName="current_borrowings"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.current_borrowings}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'current_borrowings')}
                  />
                  <TableRowClickable
                    label="Trade Payables"
                    fieldName="trade_payables"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.trade_payables}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'trade_payables')}
                  />
                  <TableRowClickable
                    label="Total Current Liabilities"
                    fieldName="total_current_liabilities"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.total_current_liabilities}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'total_current_liabilities')}
                  />

                  {/* TOTAL EQUITY AND LIABILITIES */}
                  <TableRowClickable
                    label="TOTAL EQUITY & LIABILITIES"
                    fieldName="total_equity_and_liabilities"
                    periods={periods}
                    getter={(p) => p.balance_sheet?.total_equity_and_liabilities}
                    formatter={formatVal}
                    isBold
                    isHighlight
                    onInspect={(pId) => handleInspectProvenance('balance_sheets', pId, 'total_equity_and_liabilities')}
                  />
                </tbody>
              </table>
            </div>
          )}

          {/* Cash Flow Statement View */}
          {activeTab === 'cashflow' && (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--bg-dark)', borderBottom: '1px solid var(--border-color)' }}>
                    <th style={{ textAlign: 'left', padding: '0.85rem 1.25rem', width: '35%' }}>
                      Cash Flow Activity (Ind AS 7)
                    </th>
                    {periods.map((p) => (
                      <th key={p.period.id} style={{ textAlign: 'right', padding: '0.85rem 1.25rem' }}>
                        <div>{p.period.period_label}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>
                          Ended {p.period.end_date}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <TableRowClickable
                    label="Cash from Operating Activities (CFO)"
                    fieldName="cash_from_operating_activities"
                    periods={periods}
                    getter={(p) => p.cash_flow?.cash_from_operating_activities}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('cash_flow_statements', pId, 'cash_from_operating_activities')}
                  />
                  <TableRowClickable
                    label="Cash from Investing Activities (CFI)"
                    fieldName="cash_from_investing_activities"
                    periods={periods}
                    getter={(p) => p.cash_flow?.cash_from_investing_activities}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('cash_flow_statements', pId, 'cash_from_investing_activities')}
                  />
                  <TableRowClickable
                    label="Cash from Financing Activities (CFF)"
                    fieldName="cash_from_financing_activities"
                    periods={periods}
                    getter={(p) => p.cash_flow?.cash_from_financing_activities}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('cash_flow_statements', pId, 'cash_from_financing_activities')}
                  />
                  <TableRowClickable
                    label="Net Increase / (Decrease) in Cash"
                    fieldName="net_increase_in_cash"
                    periods={periods}
                    getter={(p) => p.cash_flow?.net_increase_in_cash}
                    formatter={formatVal}
                    isBold
                    isHighlight
                    onInspect={(pId) => handleInspectProvenance('cash_flow_statements', pId, 'net_increase_in_cash')}
                  />
                  <TableRowClickable
                    label="Cash at Beginning of Period"
                    fieldName="cash_beginning_of_period"
                    periods={periods}
                    getter={(p) => p.cash_flow?.cash_beginning_of_period}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('cash_flow_statements', pId, 'cash_beginning_of_period')}
                  />
                  <TableRowClickable
                    label="Cash at End of Period"
                    fieldName="cash_end_of_period"
                    periods={periods}
                    getter={(p) => p.cash_flow?.cash_end_of_period}
                    formatter={formatVal}
                    isBold
                    isHighlight
                    onInspect={(pId) => handleInspectProvenance('cash_flow_statements', pId, 'cash_end_of_period')}
                  />

                  {/* Free Cash Flow & Capex */}
                  <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)', fontWeight: 700 }}>
                    <td colSpan={periods.length + 1} style={{ padding: '0.65rem 1.25rem', color: 'var(--accent-primary)' }}>
                      ANALYTICAL METRICS (DERIVED)
                    </td>
                  </tr>
                  <TableRowClickable
                    label="Capital Expenditure (CapEx)"
                    fieldName="capital_expenditure"
                    periods={periods}
                    getter={(p) => p.cash_flow?.capital_expenditure}
                    formatter={formatVal}
                    onInspect={(pId) => handleInspectProvenance('cash_flow_statements', pId, 'capital_expenditure')}
                  />
                  <TableRowClickable
                    label="Free Cash Flow (FCF = CFO - CapEx)"
                    fieldName="free_cash_flow"
                    periods={periods}
                    getter={(p) => p.cash_flow?.free_cash_flow}
                    formatter={formatVal}
                    isBold
                    onInspect={(pId) => handleInspectProvenance('cash_flow_statements', pId, 'free_cash_flow')}
                  />
                </tbody>
              </table>
            </div>
          )}

          {/* Corporate Actions View */}
          {activeTab === 'actions' && (
            <div style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Split size={20} color="var(--accent-primary)" />
                Historical Corporate Actions & Per-Share Lineage
              </h3>
              {corporateActions.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', padding: '1rem 0' }}>
                  No corporate actions recorded for this security.
                </div>
              ) : (
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ backgroundColor: 'var(--bg-dark)', borderBottom: '1px solid var(--border-color)' }}>
                      <th style={{ textAlign: 'left', padding: '0.75rem 1rem' }}>Action Type</th>
                      <th style={{ textAlign: 'left', padding: '0.75rem 1rem' }}>Ex-Date</th>
                      <th style={{ textAlign: 'left', padding: '0.75rem 1rem' }}>Ratio / Rate</th>
                      <th style={{ textAlign: 'right', padding: '0.75rem 1rem' }}>Adjustment Factor</th>
                      <th style={{ textAlign: 'left', padding: '0.75rem 1rem' }}>Description / Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {corporateActions.map((ca) => (
                      <tr key={ca.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>
                          <span
                            style={{
                              padding: '0.2rem 0.5rem',
                              borderRadius: 4,
                              backgroundColor:
                                ca.action_type === 'BONUS_ISSUE'
                                  ? 'rgba(16, 185, 129, 0.2)'
                                  : ca.action_type === 'STOCK_SPLIT'
                                  ? 'rgba(59, 130, 246, 0.2)'
                                  : 'rgba(234, 179, 8, 0.2)',
                              color:
                                ca.action_type === 'BONUS_ISSUE'
                                  ? 'var(--status-healthy)'
                                  : ca.action_type === 'STOCK_SPLIT'
                                  ? 'var(--accent-primary)'
                                  : '#eab308',
                            }}
                          >
                            {ca.action_type}
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem 1rem' }}>{ca.ex_date}</td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          {ca.dividend_per_share
                            ? `₹${ca.dividend_per_share} / share`
                            : ca.ratio_numerator
                            ? `${ca.ratio_numerator}:${ca.ratio_denominator}`
                            : '-'}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', textAlign: 'right', fontWeight: 600 }}>
                          {ca.adjustment_factor.toFixed(2)}x
                        </td>
                        <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                          {ca.notes || 'Statutory disclosure'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {/* Sources & Compliance View */}
          {activeTab === 'sources' && (
            <div style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldCheck size={20} color="var(--accent-primary)" />
                Indian Equities Data Source Registry & Statutory Compliance
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                {sourcesList.map((src) => (
                  <div
                    key={src.provider_id}
                    style={{
                      backgroundColor: 'var(--bg-dark)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 8,
                      padding: '1.25rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.5rem',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700 }}>{src.provider_name}</h4>
                      <span
                        style={{
                          fontSize: '0.7rem',
                          padding: '0.15rem 0.4rem',
                          borderRadius: 4,
                          backgroundColor: 'rgba(59, 130, 246, 0.2)',
                          color: 'var(--accent-primary)',
                        }}
                      >
                        {src.source_type}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <strong>Access Method:</strong> {src.access_method}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <strong>Terms & License:</strong> {src.terms_and_license}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <strong>Redistribution:</strong> {src.redistribution_restrictions}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <strong>Rate Limits:</strong> {src.rate_limits}
                    </div>
                    <div style={{ marginTop: 'auto', paddingTop: '0.5rem' }}>
                      <a
                        href={src.primary_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.3rem',
                          fontSize: '0.8rem',
                          color: 'var(--accent-primary)',
                          textDecoration: 'none',
                        }}
                      >
                        Visit Provider Portal <ExternalLink size={12} />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Field Provenance & Traceability Drawer ("Where did this number come from?") */}
      {selectedProvenance && (
        <div
          style={{
            position: 'fixed',
            right: 0,
            top: 0,
            bottom: 0,
            width: 480,
            maxWidth: '90vw',
            backgroundColor: 'var(--bg-card)',
            borderLeft: '1px solid var(--border-color)',
            boxShadow: '-4px 0 24px rgba(0,0,0,0.5)',
            zIndex: 1000,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Drawer Header */}
          <div
            style={{
              padding: '1.25rem 1.5rem',
              borderBottom: '1px solid var(--border-color)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileCheck2 size={20} color="var(--accent-primary)" />
              <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>Data Provenance Lineage</h3>
            </div>
            <button
              onClick={() => setSelectedProvenance(null)}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              <X size={20} />
            </button>
          </div>

          {/* Drawer Content */}
          <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div
              style={{
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                padding: '0.75rem 1rem',
                borderRadius: 6,
                fontSize: '0.85rem',
              }}
            >
              <strong>Metric:</strong> {provenanceFieldName || 'Financial Value'}
            </div>

            {selectedProvenance.map((p) => (
              <div
                key={p.id}
                style={{
                  backgroundColor: 'var(--bg-dark)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 8,
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.6rem',
                  fontSize: '0.85rem',
                }}
              >
                <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                  Reported As: "{p.reported_label}"
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <div>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Raw Reported Value</span>
                    <div style={{ fontWeight: 600 }}>{p.reported_currency} {p.reported_value_raw} {p.reported_unit}</div>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Normalized Stored Value</span>
                    <div style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>
                      ₹ {p.normalized_value.toLocaleString('en-IN')} {p.normalized_unit}
                    </div>
                  </div>
                </div>

                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.6rem', marginTop: '0.2rem' }}>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Source Document</div>
                  <div style={{ fontWeight: 600, marginTop: '0.1rem' }}>
                    {p.source_document?.document_name || 'Audited Annual Filing'}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    Page: {p.page_number || 'N/A'} • Table: {p.table_reference || 'Primary Statements'}
                  </div>
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <strong>Confidence:</strong> {(p.confidence_score * 100).toFixed(0)}% • <strong>Method:</strong> {p.extraction_method}
                </div>

                {p.source_document?.file_path_or_url && (
                  <a
                    href={p.source_document.file_path_or_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.3rem',
                      fontSize: '0.8rem',
                      color: 'var(--accent-primary)',
                      textDecoration: 'none',
                      marginTop: '0.25rem',
                    }}
                  >
                    View Statutory Filing PDF / Link <ExternalLink size={12} />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Validation Discrepancy & Audit Report Drawer */}
      {isValidationDrawerOpen && (
        <div
          style={{
            position: 'fixed',
            right: 0,
            top: 0,
            bottom: 0,
            width: 540,
            maxWidth: '92vw',
            backgroundColor: 'var(--bg-card)',
            borderLeft: '1px solid var(--border-color)',
            boxShadow: '-4px 0 24px rgba(0,0,0,0.5)',
            zIndex: 1000,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '1.25rem 1.5rem',
              borderBottom: '1px solid var(--border-color)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ShieldCheck size={22} color="var(--accent-primary)" />
              <div>
                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>Deterministic Audit Report</h3>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Accounting Identity & Balance Sheet Reconciliations
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsValidationDrawerOpen(false)}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              <X size={20} />
            </button>
          </div>

          {/* Body */}
          <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '0.75rem',
                backgroundColor: 'var(--bg-dark)',
                padding: '1rem',
                borderRadius: 8,
                textAlign: 'center',
              }}
            >
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Checks</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{validationReport?.total_checks}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--status-healthy)' }}>Passed Checks</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--status-healthy)' }}>
                  {validationReport?.passed_checks}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--status-error)' }}>Failed Checks</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--status-error)' }}>
                  {validationReport?.failed_checks}
                </div>
              </div>
            </div>

            <h4 style={{ margin: '0.5rem 0 0', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              Individual Accounting Invariant Checks
            </h4>

            {validationReport?.results.map((vr) => (
              <div
                key={vr.id}
                style={{
                  backgroundColor: 'var(--bg-dark)',
                  border: `1px solid ${
                    vr.status === 'PASSED' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.5)'
                  }`,
                  borderRadius: 6,
                  padding: '0.85rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.4rem',
                  fontSize: '0.82rem',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{vr.rule_name}</span>
                  <span
                    style={{
                      padding: '0.15rem 0.5rem',
                      borderRadius: 4,
                      fontWeight: 600,
                      fontSize: '0.7rem',
                      backgroundColor:
                        vr.status === 'PASSED'
                          ? 'rgba(16, 185, 129, 0.2)'
                          : 'rgba(239, 68, 68, 0.2)',
                      color: vr.status === 'PASSED' ? 'var(--status-healthy)' : 'var(--status-error)',
                    }}
                  >
                    {vr.status}
                  </span>
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                  <strong>Formula:</strong> {vr.formula_checked}
                </div>
                <div style={{ color: vr.status === 'PASSED' ? 'var(--text-primary)' : 'var(--status-error)' }}>
                  {vr.message}
                </div>
                {vr.discrepancy !== null && vr.discrepancy !== undefined && vr.discrepancy > 0 && (
                  <div style={{ color: 'var(--status-error)', fontSize: '0.75rem' }}>
                    Variance Discrepancy: ₹ {vr.discrepancy} Cr (Tolerance: {vr.tolerance} Cr)
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Sub-component for interactive clickable table row with field provenance trigger
interface TableRowClickableProps {
  label: string;
  fieldName: string;
  periods: MultiPeriodFinancialSet[];
  getter: (p: MultiPeriodFinancialSet) => number | null | undefined;
  formatter: (v: number | null | undefined) => string;
  isBold?: boolean;
  isHighlight?: boolean;
  onInspect: (periodId: number) => void;
}

const TableRowClickable: React.FC<TableRowClickableProps> = ({
  label,
  periods,
  getter,
  formatter,
  isBold,
  isHighlight,
  onInspect,
}) => {
  return (
    <tr
      style={{
        borderBottom: '1px solid var(--border-color)',
        backgroundColor: isHighlight ? 'rgba(59, 130, 246, 0.04)' : 'transparent',
        fontWeight: isBold ? 600 : 400,
      }}
    >
      <td
        onClick={() => periods.length > 0 && onInspect(periods[0].period.id)}
        style={{
          padding: '0.65rem 1.25rem',
          cursor: 'pointer',
          color: isBold ? 'var(--text-primary)' : 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
        }}
        title="Click to view statutory source provenance and filing page"
      >
        <span>{label}</span>
        <Info size={13} style={{ opacity: 0.35 }} />
      </td>
      {periods.map((p) => {
        const val = getter(p);
        return (
          <td
            key={p.period.id}
            onClick={() => onInspect(p.period.id)}
            style={{
              textAlign: 'right',
              padding: '0.65rem 1.25rem',
              cursor: 'pointer',
              fontVariantNumeric: 'tabular-nums',
            }}
            title="Click to view field lineage"
          >
            {formatter(val)}
          </td>
        );
      })}
    </tr>
  );
};
