import React from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Database, FileText, CheckSquare, Layers } from 'lucide-react';

export const DataPipelineView: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>Indian Equities Data Pipeline Specification</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Documented architectural strategy for market data, XBRL filings, and corporate governance records.
        </p>
      </div>

      <div className="grid-cols-2">
        <Card title="Target Data Sources (Indian Equities)">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <Database size={18} color="var(--accent-primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '0.9rem', color: '#fff' }}>NSE & BSE Exchange Filings</strong>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  Quarterly financial results, annual balance sheets, cash flow statements, and shareholding patterns filed with National Stock Exchange of India (NSE) and Bombay Stock Exchange (BSE).
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <FileText size={18} color="var(--accent-primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '0.9rem', color: '#fff' }}>XBRL Structured Statements</strong>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  Standardized XBRL taxonomies matching MCA (Ministry of Corporate Affairs) and SEBI guidelines to prevent parsing ambiguity.
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <Layers size={18} color="var(--accent-primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '0.9rem', color: '#fff' }}>Annual Reports & Auditor Disclosures</strong>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  Auditor notes, qualification remarks, contingent liabilities, related-party transactions (RPT), and CARO reports.
                </p>
              </div>
            </div>
          </div>
        </Card>

        <Card title="Validation Engine Rules (Phase 1 Target)">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckSquare size={16} color="var(--accent-primary)" />
                <span style={{ fontSize: '0.85rem' }}>Balance Sheet Identity: Assets = Liabilities + Equity</span>
              </div>
              <Badge variant="info">Spec Defined</Badge>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckSquare size={16} color="var(--accent-primary)" />
                <span style={{ fontSize: '0.85rem' }}>Cash Flow Reconciliation: CFO + CFI + CFF = Net Cash Δ</span>
              </div>
              <Badge variant="info">Spec Defined</Badge>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckSquare size={16} color="var(--accent-primary)" />
                <span style={{ fontSize: '0.85rem' }}>Restatement and Prior-Period Adjustment Tracing</span>
              </div>
              <Badge variant="info">Spec Defined</Badge>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.4rem 0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckSquare size={16} color="var(--accent-primary)" />
                <span style={{ fontSize: '0.85rem' }}>Standalone vs. Consolidated Entity Differentiation</span>
              </div>
              <Badge variant="info">Spec Defined</Badge>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
