import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Info,
  Layers,
  Activity,
  X,
} from 'lucide-react';
import { ApiService } from '../services/api';
import {
  Company,
  CompanyForensicResponse,
  PeriodForensicScorecard,
  ForensicSignal,
  ForensicRiskLevel,
  AltmanZScoreResult,
} from '../types/api';

type ForensicTab = 'scoreboard' | 'beneish' | 'piotroski' | 'altman' | 'signals';

export const ForensicIntelligenceView: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string>('RELIANCE');
  const [statementType, setStatementType] = useState<'CONSOLIDATED' | 'STANDALONE'>('CONSOLIDATED');
  const [activeTab, setActiveTab] = useState<ForensicTab>('scoreboard');
  const [limitPeriods, setLimitPeriods] = useState<number>(5);

  const [forensicData, setForensicData] = useState<CompanyForensicResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Inspector Modal State
  const [inspectItem, setInspectItem] = useState<{
    title: string;
    category: string;
    riskLevel?: ForensicRiskLevel;
    formula?: string;
    inputs?: Record<string, any>;
    interpretation?: string;
    limitations?: string;
    methodologyVersion?: string;
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
        console.error('Failed to load companies for forensic analysis:', err);
      }
    }
    loadCompanies();
  }, []);

  // Fetch Forensic Intelligence Data
  const loadForensicData = useCallback(async () => {
    if (!selectedTicker) return;
    setLoading(true);
    setError(null);
    try {
      const res = await ApiService.getForensicSummary(selectedTicker, statementType, limitPeriods);
      setForensicData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load forensic intelligence report');
    } finally {
      setLoading(false);
    }
  }, [selectedTicker, statementType, limitPeriods]);

  useEffect(() => {
    loadForensicData();
  }, [loadForensicData]);

  const selectedCompany = companies.find(c => c.ticker === selectedTicker);
  const latestScorecard = forensicData?.latest_scorecard;
  const historical = forensicData?.historical_scorecards || [];

  const getRiskBadge = (level?: ForensicRiskLevel) => {
    switch (level) {
      case 'LOW':
        return <span className="badge badge-success" style={{ fontWeight: 700 }}>LOW RISK</span>;
      case 'MODERATE':
        return <span className="badge badge-warning" style={{ fontWeight: 700 }}>MODERATE WATCH</span>;
      case 'ELEVATED':
      case 'HIGH':
      case 'CRITICAL':
        return <span className="badge badge-danger" style={{ fontWeight: 700 }}>ELEVATED RISK</span>;
      case 'NOT_APPLICABLE':
        return <span className="badge" style={{ backgroundColor: 'rgba(255,255,255,0.08)', color: 'var(--text-muted)' }}>N/A (SECTOR)</span>;
      default:
        return <span className="badge" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }}>INFO</span>;
    }
  };

  return (
    <div className="view-container" style={{ padding: '1.5rem', maxWidth: '1440px', margin: '0 auto' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 800, margin: 0 }}>Forensic Intelligence Engine</h1>
            <span className="badge badge-success" style={{ fontSize: '0.75rem', fontWeight: 700 }}>PHASE 3 ACTIVE</span>
            <span className="badge" style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', fontSize: '0.75rem', fontWeight: 600 }}>
              Zero-Accusation Rule
            </span>
            <span className="badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.15)', color: 'var(--accent-primary)', fontSize: '0.75rem', fontWeight: 600 }}>
              Methodology v1.0.0
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.35rem', marginBottom: 0 }}>
            Empirical accounting anomaly detection, Beneish M-Score, Piotroski F-Score, Altman Z'' distress modeling, and working capital divergence signals.
          </p>
        </div>

        {/* Global Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
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

          <button
            onClick={loadForensicData}
            disabled={loading}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.45rem 0.85rem' }}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            <span>Rescan</span>
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
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block' }}>Sector & Industry</span>
              <span style={{ fontSize: '0.85rem' }}>{selectedCompany.sector} &bull; {selectedCompany.industry}</span>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block' }}>ISIN / Primary Exchange</span>
              <span style={{ fontSize: '0.85rem', fontFamily: 'monospace' }}>{selectedCompany.isin} ({selectedCompany.primary_exchange})</span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-primary)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
              Deterministic Forensic Rules Active
            </span>
          </div>
        </div>
      )}

      {/* Sector Notice if any */}
      {forensicData?.sector_applicability_notes && forensicData.sector_applicability_notes.length > 0 && (
        <div style={{
          backgroundColor: 'rgba(59, 130, 246, 0.05)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: '6px',
          padding: '0.6rem 1rem',
          marginBottom: '1.25rem',
          fontSize: '0.8rem',
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <Info size={14} style={{ color: 'var(--accent-primary)' }} />
          <span>{forensicData.sector_applicability_notes[0]}</span>
        </div>
      )}

      {/* Forensic Scoreboard Overview Cards (Latest Period) */}
      {latestScorecard && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {/* 1. Overall Forensic Stance */}
          <div style={{
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
                  Overall Forensic Stance
                </span>
                {getRiskBadge(latestScorecard.overall_risk_level)}
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, marginTop: '0.35rem' }}>
                {latestScorecard.overall_risk_level === 'LOW' ? 'Clean Profile' : latestScorecard.overall_risk_level === 'MODERATE' ? 'Moderate Watchlist' : 'Elevated Scrutiny'}
              </div>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.6rem' }}>
              {latestScorecard.risk_summary_text}
            </div>
          </div>

          {/* 2. Beneish M-Score Card */}
          {latestScorecard.beneish_m_score && (
            <div
              onClick={() => {
                const b = latestScorecard.beneish_m_score;
                if (b) {
                  setInspectItem({
                    title: 'Beneish 8-Variable M-Score',
                    category: 'Earnings Manipulation Risk',
                    riskLevel: b.risk_classification,
                    formula: b.formula_expression,
                    interpretation: b.interpretation,
                    limitations: b.limitations,
                    methodologyVersion: b.methodology_version
                  });
                }
              }}
              style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '1.25rem',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
                    Beneish M-Score
                  </span>
                  {getRiskBadge(latestScorecard.beneish_m_score.risk_classification)}
                </div>
                <div style={{
                  fontSize: '1.75rem',
                  fontWeight: 800,
                  color: latestScorecard.beneish_m_score.m_score !== null &&
                    latestScorecard.beneish_m_score.m_score !== undefined &&
                    latestScorecard.beneish_m_score.m_score > -1.78
                    ? '#ef4444'
                    : 'var(--accent-primary)'
                }}>
                  {latestScorecard.beneish_m_score.m_score !== null && latestScorecard.beneish_m_score.m_score !== undefined
                    ? latestScorecard.beneish_m_score.m_score.toFixed(2)
                    : 'N/A'}
                </div>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                Threshold: <strong>&le; -1.78 (Safe)</strong> &bull; Period: {latestScorecard.period_label}
              </div>
            </div>
          )}

          {/* 3. Piotroski F-Score Card */}
          {latestScorecard.piotroski_f_score && (
            <div
              onClick={() => {
                const p = latestScorecard.piotroski_f_score;
                if (p) {
                  setInspectItem({
                    title: 'Piotroski 9-Point F-Score',
                    category: 'Fundamental Health',
                    riskLevel: p.risk_classification,
                    formula: 'Sum of 9 binary fundamental tests (Profitability + Leverage + Efficiency)',
                    interpretation: p.interpretation,
                    limitations: p.limitations,
                    methodologyVersion: p.methodology_version
                  });
                }
              }}
              style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '1.25rem',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
                    Piotroski F-Score
                  </span>
                  {getRiskBadge(latestScorecard.piotroski_f_score.risk_classification)}
                </div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: latestScorecard.piotroski_f_score.f_score >= 8 ? '#10b981' : latestScorecard.piotroski_f_score.f_score >= 5 ? 'var(--accent-primary)' : '#ef4444' }}>
                  {latestScorecard.piotroski_f_score.f_score} / 9
                </div>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                {latestScorecard.piotroski_f_score.financial_health_label}
              </div>
            </div>
          )}

          {/* 4. Altman Z''-Score Card */}
          {latestScorecard.altman_z_score && (
            <div
              onClick={() => {
                const a = latestScorecard.altman_z_score;
                if (a) {
                  setInspectItem({
                    title: "Altman Z''-Score (Emerging Market)",
                    category: 'Solvency & Distress Risk',
                    riskLevel: a.risk_classification,
                    formula: a.formula_expression,
                    inputs: a.components,
                    interpretation: a.interpretation,
                    limitations: a.limitations,
                    methodologyVersion: a.methodology_version
                  });
                }
              }}
              style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '1.25rem',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
                    Altman Z''-Score
                  </span>
                  {getRiskBadge(latestScorecard.altman_z_score.risk_classification)}
                </div>
                <div style={{
                  fontSize: '1.75rem',
                  fontWeight: 800,
                  color: latestScorecard.altman_z_score.z_score !== null &&
                    latestScorecard.altman_z_score.z_score !== undefined &&
                    latestScorecard.altman_z_score.z_score > 2.60
                    ? '#10b981'
                    : latestScorecard.altman_z_score.z_score !== null &&
                      latestScorecard.altman_z_score.z_score !== undefined &&
                      latestScorecard.altman_z_score.z_score >= 1.10
                      ? 'var(--accent-primary)'
                      : '#ef4444'
                }}>
                  {latestScorecard.altman_z_score.z_score !== null && latestScorecard.altman_z_score.z_score !== undefined
                    ? latestScorecard.altman_z_score.z_score.toFixed(2)
                    : 'N/A'}
                </div>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                Zone: <strong>{latestScorecard.altman_z_score.zone}</strong> (Safe &gt; 2.60)
              </div>
            </div>
          )}
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
          { id: 'scoreboard', label: 'Forensic Scoreboard', icon: Activity },
          { id: 'beneish', label: 'Beneish M-Score (8-Variable)', icon: ShieldAlert },
          { id: 'piotroski', label: 'Piotroski 9-Point F-Score', icon: ShieldCheck },
          { id: 'altman', label: "Altman Z'' Distress Analyzer", icon: Layers },
          { id: 'signals', label: 'Granular Anomaly Signals', icon: AlertTriangle },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as ForensicTab)}
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
          <div>Evaluating forensic models and anomaly screening rules...</div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && historical.length === 0 && (
        <div style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '3rem',
          textAlign: 'center',
          color: 'var(--text-muted)'
        }}>
          <Info size={32} style={{ margin: '0 auto 1rem', display: 'block', color: 'var(--accent-primary)' }} />
          <h3>No financial period data available for {selectedTicker}</h3>
          <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
            Please select an ingested company from the dropdown to view forensic analytics.
          </p>
        </div>
      )}

      {/* Tab 1: Forensic Scoreboard */}
      {!loading && activeTab === 'scoreboard' && historical.length > 0 && (
        <ForensicScoreboardSection
          scorecards={historical}
          onInspectSignal={(sig) => setInspectItem({
            title: sig.signal_label,
            category: sig.category,
            riskLevel: sig.risk_level,
            formula: sig.formula_expression,
            inputs: sig.inputs,
            interpretation: sig.interpretation,
            limitations: sig.limitations,
            methodologyVersion: sig.methodology_version
          })}
        />
      )}

      {/* Tab 2: Beneish M-Score Deep Dive */}
      {!loading && activeTab === 'beneish' && historical.length > 0 && (
        <BeneishSection
          scorecards={historical}
          onInspectVariable={(v, label) => setInspectItem({
            title: `${v.name} (${v.key}) - ${label}`,
            category: 'Beneish Component Index',
            formula: v.formula,
            interpretation: v.interpretation,
            limitations: 'Coefficient contribution evaluated in 8-variable logistic regression.',
            methodologyVersion: 'v1.0.0'
          })}
        />
      )}

      {/* Tab 3: Piotroski 9-Point F-Score Matrix */}
      {!loading && activeTab === 'piotroski' && historical.length > 0 && (
        <PiotroskiSection
          scorecards={historical}
          onInspectSignal={(sig, label) => setInspectItem({
            title: `${sig.name} - ${label}`,
            category: `Piotroski Test: ${sig.category}`,
            formula: sig.formula,
            inputs: sig.inputs,
            interpretation: sig.description,
            limitations: 'Binary score metric.',
            methodologyVersion: 'v1.0.0'
          })}
        />
      )}

      {/* Tab 4: Altman Z'' Distress Analyzer */}
      {!loading && activeTab === 'altman' && historical.length > 0 && (
        <AltmanSection
          scorecards={historical}
          onInspectModel={(altman) => setInspectItem({
            title: `Altman Z''-Score - ${altman.period_label}`,
            category: 'Solvency & Default Probability',
            riskLevel: altman.risk_classification,
            formula: altman.formula_expression,
            inputs: altman.components,
            interpretation: altman.interpretation,
            limitations: altman.limitations,
            methodologyVersion: altman.methodology_version
          })}
        />
      )}

      {/* Tab 5: Granular Anomaly Signals */}
      {!loading && activeTab === 'signals' && historical.length > 0 && (
        <GranularSignalsSection
          scorecards={historical}
          onInspectSignal={(sig) => setInspectItem({
            title: sig.signal_label,
            category: sig.category,
            riskLevel: sig.risk_level,
            formula: sig.formula_expression,
            inputs: sig.inputs,
            interpretation: sig.interpretation,
            limitations: sig.limitations,
            methodologyVersion: sig.methodology_version
          })}
        />
      )}

      {/* Forensic Evidence & Lineage Modal */}
      {inspectItem && (
        <ForensicEvidenceModal
          data={inspectItem}
          onClose={() => setInspectItem(null)}
        />
      )}
    </div>
  );
};

// --------------------------------------------------------------------------------------
// SUB-SECTIONS
// --------------------------------------------------------------------------------------

const ForensicScoreboardSection: React.FC<{
  scorecards: PeriodForensicScorecard[];
  onInspectSignal: (sig: ForensicSignal) => void;
}> = ({ scorecards, onInspectSignal }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Historical Scorecard Matrix */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Historical Forensic Risk Evolution</h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Multi-period trajectory across core forensic models</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Forensic Dimension</th>
                {scorecards.map(sc => (
                  <th key={sc.period_id} style={{ textAlign: 'center', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>
                    {sc.period_label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem 1.25rem', fontWeight: 600 }}>Overall Forensic Stance</td>
                {scorecards.map(sc => (
                  <td key={sc.period_id} style={{ textAlign: 'center', padding: '0.75rem 1.25rem' }}>
                    <span className={`badge ${sc.overall_risk_level === 'LOW' ? 'badge-success' : sc.overall_risk_level === 'MODERATE' ? 'badge-warning' : 'badge-danger'}`}>
                      {sc.overall_risk_level}
                    </span>
                  </td>
                ))}
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Beneish M-Score (Threshold &le; -1.78)</td>
                {scorecards.map(sc => (
                  <td key={sc.period_id} style={{ textAlign: 'center', padding: '0.75rem 1.25rem', fontFamily: 'monospace', fontWeight: 700 }}>
                    {sc.beneish_m_score?.m_score !== null && sc.beneish_m_score?.m_score !== undefined
                      ? `${sc.beneish_m_score.m_score.toFixed(2)} (${sc.beneish_m_score.risk_classification})`
                      : 'N/A'}
                  </td>
                ))}
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Piotroski F-Score (Scale 0-9)</td>
                {scorecards.map(sc => (
                  <td key={sc.period_id} style={{ textAlign: 'center', padding: '0.75rem 1.25rem', fontFamily: 'monospace', fontWeight: 700 }}>
                    {sc.piotroski_f_score ? `${sc.piotroski_f_score.f_score} / 9` : '—'}
                  </td>
                ))}
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Altman Z''-Score (Safe &gt; 2.60)</td>
                {scorecards.map(sc => (
                  <td key={sc.period_id} style={{ textAlign: 'center', padding: '0.75rem 1.25rem', fontFamily: 'monospace', fontWeight: 700 }}>
                    {sc.altman_z_score?.z_score !== null && sc.altman_z_score?.z_score !== undefined
                      ? `${sc.altman_z_score.z_score.toFixed(2)} (${sc.altman_z_score.zone})`
                      : 'N/A'}
                  </td>
                ))}
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>Active Screening Anomalies Count</td>
                {scorecards.map(sc => (
                  <td key={sc.period_id} style={{ textAlign: 'center', padding: '0.75rem 1.25rem', fontFamily: 'monospace' }}>
                    <span className={`badge ${sc.anomalous_signals_count === 0 ? 'badge-success' : 'badge-warning'}`}>
                      {sc.anomalous_signals_count} active
                    </span>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Latest Period Active Signals List */}
      {scorecards[0] && (
        <div style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '1.25rem'
        }}>
          <h3 style={{ margin: '0 0 1rem', fontSize: '1rem', fontWeight: 700 }}>
            Active Screening Indicators ({scorecards[0].period_label})
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
            {scorecards[0].screening_signals.map(sig => (
              <div
                key={sig.signal_key}
                onClick={() => onInspectSignal(sig)}
                style={{
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '1rem',
                  cursor: 'pointer',
                  backgroundColor: sig.risk_level === 'HIGH' || sig.risk_level === 'ELEVATED'
                    ? 'rgba(239, 68, 68, 0.04)'
                    : 'transparent'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    {sig.category}
                  </span>
                  <span className={`badge ${sig.risk_level === 'LOW' ? 'badge-success' : sig.risk_level === 'MODERATE' ? 'badge-warning' : 'badge-danger'}`}>
                    {sig.risk_level}
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                  {sig.signal_label}
                </div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--accent-primary)', fontFamily: 'monospace' }}>
                  {sig.formatted_value}
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem', marginBottom: 0 }}>
                  {sig.interpretation}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const BeneishSection: React.FC<{
  scorecards: PeriodForensicScorecard[];
  onInspectVariable: (v: any, label: string) => void;
}> = ({ scorecards, onInspectVariable }) => {
  const latestBeneish = scorecards[0]?.beneish_m_score;

  if (!latestBeneish || !latestBeneish.is_applicable) {
    return (
      <div style={{ backgroundColor: 'var(--bg-card)', padding: '2rem', borderRadius: '8px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Info size={32} style={{ margin: '0 auto 1rem', display: 'block', color: 'var(--accent-primary)' }} />
        <h3>Beneish M-Score Not Applicable or Insufficient Historical Periods</h3>
        <p style={{ fontSize: '0.85rem' }}>{latestBeneish?.inapplicable_reason || 'Requires 2 consecutive periods.'}</p>
      </div>
    );
  }

  const varList = Object.values(latestBeneish.variables);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Formula & Threshold Card */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        padding: '1.25rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '0.75rem' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>Beneish 8-Variable Logistic Regression Model</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Calculates empirical probability of earnings manipulation</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>M-Score ({scorecards[0].period_label}):</span>
            <span style={{
              fontSize: '1.4rem',
              fontWeight: 800,
              color: latestBeneish.m_score !== null &&
                latestBeneish.m_score !== undefined &&
                latestBeneish.m_score > -1.78
                ? '#ef4444'
                : '#10b981'
            }}>
              {latestBeneish.m_score !== null && latestBeneish.m_score !== undefined ? latestBeneish.m_score.toFixed(2) : '—'}
            </span>
          </div>
        </div>
        <div style={{
          backgroundColor: 'rgba(0,0,0,0.3)',
          padding: '0.75rem 1rem',
          borderRadius: '6px',
          fontFamily: 'monospace',
          fontSize: '0.85rem',
          color: 'var(--accent-primary)',
          overflowX: 'auto'
        }}>
          {latestBeneish.formula_expression}
        </div>
      </div>

      {/* 8-Variable Contribution Breakdown Table */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>8-Variable Parameter Contributions ({scorecards[0].period_label})</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Variable</th>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Description</th>
                <th style={{ textAlign: 'right', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Resolved Value</th>
                <th style={{ textAlign: 'right', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Coefficient</th>
                <th style={{ textAlign: 'right', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Contribution</th>
              </tr>
            </thead>
            <tbody>
              {varList.map(v => (
                <tr
                  key={v.key}
                  onClick={() => onInspectVariable(v, scorecards[0].period_label)}
                  style={{ borderBottom: '1px solid var(--border-color)', cursor: 'pointer' }}
                >
                  <td style={{ padding: '0.75rem 1.25rem', fontWeight: 700, fontFamily: 'monospace' }}>{v.key}</td>
                  <td style={{ padding: '0.75rem 1.25rem' }}>{v.name}</td>
                  <td style={{ padding: '0.75rem 1.25rem', textAlign: 'right', fontFamily: 'monospace', fontWeight: 600 }}>
                    {v.value !== null && v.value !== undefined ? v.value.toFixed(3) : '—'}
                  </td>
                  <td style={{ padding: '0.75rem 1.25rem', textAlign: 'right', fontFamily: 'monospace', color: 'var(--text-muted)' }}>
                    {v.coefficient > 0 ? `+${v.coefficient}` : v.coefficient}
                  </td>
                  <td style={{ padding: '0.75rem 1.25rem', textAlign: 'right', fontFamily: 'monospace', fontWeight: 700, color: 'var(--accent-primary)' }}>
                    {v.contribution !== null && v.contribution !== undefined ? (v.contribution > 0 ? `+${v.contribution.toFixed(3)}` : v.contribution.toFixed(3)) : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const PiotroskiSection: React.FC<{
  scorecards: PeriodForensicScorecard[];
  onInspectSignal: (sig: any, label: string) => void;
}> = ({ scorecards, onInspectSignal }) => {
  const latest = scorecards[0]?.piotroski_f_score;

  if (!latest || !latest.is_applicable) {
    return (
      <div style={{ backgroundColor: 'var(--bg-card)', padding: '2rem', borderRadius: '8px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Info size={32} style={{ margin: '0 auto 1rem', display: 'block', color: 'var(--accent-primary)' }} />
        <h3>Piotroski F-Score Not Available</h3>
        <p style={{ fontSize: '0.85rem' }}>{latest?.inapplicable_reason || 'Requires 2 consecutive comparative periods.'}</p>
      </div>
    );
  }

  const profSignals = latest.signals.filter(s => s.category === 'Profitability');
  const levSignals = latest.signals.filter(s => s.category === 'Leverage & Liquidity');
  const effSignals = latest.signals.filter(s => s.category === 'Operating Efficiency');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Overview F-Score Banner */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        padding: '1.25rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>Piotroski 9-Point Fundamental Test Matrix</h3>
          <p style={{ margin: '0.25rem 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Binary evaluation of operating profitability, balance sheet liquidity, and asset productivity.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>PROFITABILITY</span>
            <strong style={{ fontSize: '1.1rem' }}>{latest.profitability_score} / 4</strong>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>LEVERAGE</span>
            <strong style={{ fontSize: '1.1rem' }}>{latest.leverage_liquidity_score} / 3</strong>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>EFFICIENCY</span>
            <strong style={{ fontSize: '1.1rem' }}>{latest.operating_efficiency_score} / 2</strong>
          </div>
          <div style={{ borderLeft: '1px solid var(--border-color)', paddingLeft: '1.25rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>TOTAL SCORE</span>
            <span style={{ fontSize: '1.6rem', fontWeight: 800, color: latest.f_score >= 8 ? '#10b981' : latest.f_score >= 5 ? 'var(--accent-primary)' : '#ef4444' }}>
              {latest.f_score} / 9
            </span>
          </div>
        </div>
      </div>

      {/* 9 Binary Tests List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {[
          { title: '1. Profitability Signals (4 Points)', list: profSignals },
          { title: '2. Leverage, Liquidity & Solvency Signals (3 Points)', list: levSignals },
          { title: '3. Operating Efficiency Signals (2 Points)', list: effSignals },
        ].map(group => (
          <div
            key={group.title}
            style={{
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              overflow: 'hidden'
            }}
          >
            <div style={{ padding: '0.75rem 1.25rem', backgroundColor: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-color)', fontWeight: 700, fontSize: '0.9rem' }}>
              {group.title}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {group.list.map(s => (
                <div
                  key={s.key}
                  onClick={() => onInspectSignal(s, scorecards[0].period_label)}
                  style={{
                    padding: '0.75rem 1.25rem',
                    borderBottom: '1px solid var(--border-color)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{s.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{s.description}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Score: {s.score}
                    </span>
                    <span className={`badge ${s.passed ? 'badge-success' : 'badge-danger'}`} style={{ fontWeight: 700, minWidth: '70px', textAlign: 'center' }}>
                      {s.passed ? 'PASSED (+1)' : 'FAILED (0)'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const AltmanSection: React.FC<{
  scorecards: PeriodForensicScorecard[];
  onInspectModel?: (altman: AltmanZScoreResult) => void;
}> = ({ scorecards, onInspectModel }) => {
  const latest = scorecards[0]?.altman_z_score;

  if (!latest || !latest.is_applicable) {
    return (
      <div style={{ backgroundColor: 'var(--bg-card)', padding: '2rem', borderRadius: '8px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Info size={32} style={{ margin: '0 auto 1rem', display: 'block', color: 'var(--accent-primary)' }} />
        <h3>Altman Z''-Score Not Applicable</h3>
        <p style={{ fontSize: '0.85rem' }}>{latest?.inapplicable_reason || 'Not applicable to banking or missing financial statements.'}</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Zone Threshold Indicator */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        padding: '1.25rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>Emerging Market Altman Z''-Score Distress Model</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Calibrated for Indian Corporates / Ind AS accounting structures</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Computed Z''-Score:</span>
            <span style={{
              fontSize: '1.6rem',
              fontWeight: 800,
              color: latest.z_score !== null &&
                latest.z_score !== undefined &&
                latest.z_score > 2.60
                ? '#10b981'
                : latest.z_score !== null &&
                  latest.z_score !== undefined &&
                  latest.z_score >= 1.10
                  ? 'var(--accent-primary)'
                  : '#ef4444'
            }}>
              {latest.z_score !== null && latest.z_score !== undefined ? latest.z_score.toFixed(2) : '—'}
            </span>
            <span className={`badge ${latest.zone === 'Safe Zone' ? 'badge-success' : latest.zone === 'Grey Zone' ? 'badge-warning' : 'badge-danger'}`} style={{ fontWeight: 700 }}>
              {latest.zone}
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.3)', padding: '0.75rem 1rem', borderRadius: '6px' }}>
          <div style={{
            fontFamily: 'monospace',
            fontSize: '0.85rem',
            color: 'var(--accent-primary)'
          }}>
            {latest.formula_expression}
          </div>
          {onInspectModel && (
            <button
              onClick={() => onInspectModel(latest)}
              className="btn btn-secondary"
              style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
            >
              <Info size={14} /> Lineage & Inputs
            </button>
          )}
        </div>
      </div>

      {/* Multi-Period Component Breakdown */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Historical Component Ratios</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Component Ratio</th>
                {scorecards.map(sc => (
                  <th key={sc.period_id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>
                    {sc.period_label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                { key: 'X1_Working_Capital_to_Assets', label: 'X1: Working Capital / Total Assets' },
                { key: 'X2_Retained_Earnings_to_Assets', label: 'X2: Retained Earnings / Total Assets' },
                { key: 'X3_EBIT_to_Assets', label: 'X3: Operating Profit (EBIT) / Total Assets' },
                { key: 'X4_Equity_to_Liabilities', label: 'X4: Book Value of Equity / Total Liabilities' },
              ].map(row => (
                <tr key={row.key} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem 1.25rem', fontWeight: 500 }}>{row.label}</td>
                  {scorecards.map(sc => {
                    const val = sc.altman_z_score?.components?.[row.key];
                    return (
                      <td key={sc.period_id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace' }}>
                        {val !== null && val !== undefined ? val.toFixed(4) : '—'}
                      </td>
                    );
                  })}
                </tr>
              ))}
              <tr style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'rgba(59, 130, 246, 0.05)' }}>
                <td style={{ padding: '0.75rem 1.25rem', fontWeight: 800, color: 'var(--accent-primary)' }}>Computed Z''-Score</td>
                {scorecards.map(sc => (
                  <td key={sc.period_id} style={{ textAlign: 'right', padding: '0.75rem 1.25rem', fontFamily: 'monospace', fontWeight: 800, color: 'var(--accent-primary)' }}>
                    {sc.altman_z_score?.z_score !== null && sc.altman_z_score?.z_score !== undefined ? sc.altman_z_score.z_score.toFixed(2) : '—'}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const GranularSignalsSection: React.FC<{
  scorecards: PeriodForensicScorecard[];
  onInspectSignal: (sig: ForensicSignal) => void;
}> = ({ scorecards, onInspectSignal }) => {
  const latestSignals = scorecards[0]?.screening_signals || [];

  return (
    <div style={{
      backgroundColor: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>Granular Accounting Screening Matrix ({scorecards[0]?.period_label})</h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Click any indicator to inspect mathematical formula and parameters</span>
        </div>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Category</th>
              <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Indicator</th>
              <th style={{ textAlign: 'right', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Resolved Value</th>
              <th style={{ textAlign: 'left', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Benchmark Threshold</th>
              <th style={{ textAlign: 'center', padding: '0.75rem 1.25rem', color: 'var(--text-muted)' }}>Risk Status</th>
            </tr>
          </thead>
          <tbody>
            {latestSignals.map(sig => (
              <tr
                key={sig.signal_key}
                onClick={() => onInspectSignal(sig)}
                style={{
                  borderBottom: '1px solid var(--border-color)',
                  cursor: 'pointer',
                  backgroundColor: sig.risk_level === 'HIGH' || sig.risk_level === 'ELEVATED' ? 'rgba(239, 68, 68, 0.03)' : 'transparent'
                }}
              >
                <td style={{ padding: '0.75rem 1.25rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem' }}>
                  {sig.category}
                </td>
                <td style={{ padding: '0.75rem 1.25rem', fontWeight: 600 }}>
                  {sig.signal_label}
                </td>
                <td style={{ padding: '0.75rem 1.25rem', textAlign: 'right', fontFamily: 'monospace', fontWeight: 700, color: 'var(--accent-primary)' }}>
                  {sig.formatted_value}
                </td>
                <td style={{ padding: '0.75rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {sig.benchmark_threshold}
                </td>
                <td style={{ padding: '0.75rem 1.25rem', textAlign: 'center' }}>
                  <span className={`badge ${sig.risk_level === 'LOW' ? 'badge-success' : sig.risk_level === 'MODERATE' ? 'badge-warning' : 'badge-danger'}`} style={{ fontWeight: 700 }}>
                    {sig.risk_level}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// --------------------------------------------------------------------------------------
// EVIDENCE & METHODOLOGY MODAL
// --------------------------------------------------------------------------------------

const ForensicEvidenceModal: React.FC<{
  data: {
    title: string;
    category: string;
    riskLevel?: ForensicRiskLevel;
    formula?: string;
    inputs?: Record<string, any>;
    interpretation?: string;
    limitations?: string;
    methodologyVersion?: string;
  };
  onClose: () => void;
}> = ({ data, onClose }) => {
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
        {/* Header */}
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
                {data.category}
              </span>
              {data.riskLevel && (
                <span className={`badge ${data.riskLevel === 'LOW' ? 'badge-success' : data.riskLevel === 'MODERATE' ? 'badge-warning' : 'badge-danger'}`} style={{ fontSize: '0.7rem' }}>
                  {data.riskLevel}
                </span>
              )}
            </div>
            <h2 style={{ margin: '0.35rem 0 0', fontSize: '1.2rem', fontWeight: 800 }}>{data.title}</h2>
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

        {/* Body */}
        <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Formula */}
          {data.formula && (
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
                Deterministic Mathematical Formula
              </label>
              <div style={{
                backgroundColor: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '0.85rem 1rem',
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                color: 'var(--accent-primary)'
              }}>
                {data.formula}
              </div>
            </div>
          )}

          {/* Inputs */}
          {data.inputs && Object.keys(data.inputs).length > 0 && (
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
                Input Parameter Values
              </label>
              <div style={{
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                overflow: 'hidden'
              }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                  <thead>
                    <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-color)' }}>
                      <th style={{ textAlign: 'left', padding: '0.5rem 0.75rem', color: 'var(--text-muted)' }}>Parameter</th>
                      <th style={{ textAlign: 'right', padding: '0.5rem 0.75rem', color: 'var(--text-muted)' }}>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(data.inputs).map(([k, v]) => (
                      <tr key={k} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '0.5rem 0.75rem', fontFamily: 'monospace' }}>{k}</td>
                        <td style={{ textAlign: 'right', padding: '0.5rem 0.75rem', fontFamily: 'monospace', fontWeight: 600 }}>
                          {typeof v === 'number' ? v.toLocaleString('en-IN', { maximumFractionDigits: 4 }) : String(v)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Interpretation */}
          {data.interpretation && (
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
                Screening Interpretation
              </label>
              <div style={{
                backgroundColor: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '0.85rem 1rem',
                fontSize: '0.85rem',
                lineHeight: 1.5
              }}>
                {data.interpretation}
              </div>
            </div>
          )}

          {/* Limitations */}
          {data.limitations && (
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
                Statistical & Accounting Limitations
              </label>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', lineHeight: 1.4 }}>
                {data.limitations}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
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
