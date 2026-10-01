import React from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { ShieldCheck, ArrowRight } from 'lucide-react';

export const ArchitectureView: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>Platform Architecture & Core Principles</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Strict computational hierarchy and boundaries for financial intelligence.
        </p>
      </div>

      <Card title="The Cardinal Law of Financial Computing" subtitle="Absolute segregation of data, deterministic calculations, and AI explanations">
        <div className="pipeline-diagram">
          <div className="pipeline-step">
            <div className="pipeline-step-box">1. DATA</div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>NSE / BSE / XBRL</span>
          </div>
          <ArrowRight className="pipeline-arrow" size={18} />
          <div className="pipeline-step">
            <div className="pipeline-step-box">2. VALIDATION</div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Pydantic / Rules</span>
          </div>
          <ArrowRight className="pipeline-arrow" size={18} />
          <div className="pipeline-step">
            <div className="pipeline-step-box">3. CALCULATIONS</div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Deterministic Python</span>
          </div>
          <ArrowRight className="pipeline-arrow" size={18} />
          <div className="pipeline-step">
            <div className="pipeline-step-box">4. ANALYTICS</div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Forensic / Health</span>
          </div>
          <ArrowRight className="pipeline-arrow" size={18} />
          <div className="pipeline-step">
            <div className="pipeline-step-box">5. EVIDENCE</div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Audit Trail & Citations</span>
          </div>
          <ArrowRight className="pipeline-arrow" size={18} />
          <div className="pipeline-step">
            <div className="pipeline-step-box" style={{ borderColor: 'var(--accent-primary)', color: '#38bdf8' }}>6. AI EXPLANATION</div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Synthesized Synthesis</span>
          </div>
        </div>

        <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.75rem', padding: '1rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '6px' }}>
            <ShieldCheck size={20} color="var(--success)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong style={{ color: '#fff' }}>Rule 1: LLM is Never a Calculator</strong>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                All financial ratios (ROCE, ROE, Piotroski F-Score, Altman Z-Score, DuPont breakdown, Working Capital Cycles, Debt-to-Equity) are computed strictly via deterministic code formulas. The LLM is never prompted to compute mathematical figures.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', padding: '1rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '6px' }}>
            <ShieldCheck size={20} color="var(--success)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong style={{ color: '#fff' }}>Rule 2: Traceable Evidence & Citations</strong>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                Every qualitative assertion and quantitative metric must reference exact source line items, filings, financial statements, or regulatory submissions with complete timestamps and audit metadata.
              </p>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid-cols-2">
        <Card title="Technology Stack Decisions">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem' }}>Backend: FastAPI + Async Python</span>
              <Badge variant="info">Chosen</Badge>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem' }}>ORM & Migrations: SQLAlchemy 2.0 + Alembic</span>
              <Badge variant="info">Chosen</Badge>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem' }}>Database: PostgreSQL (Primary) / SQLite (Dev)</span>
              <Badge variant="info">Configured</Badge>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem' }}>Frontend: React 18 + TypeScript + Vite</span>
              <Badge variant="info">Chosen</Badge>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem' }}>Testing: Pytest (Backend) + Typecheck/Build (UI)</span>
              <Badge variant="info">Chosen</Badge>
            </div>
          </div>
        </Card>

        <Card title="Phase Roadmap Boundaries">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem' }}>Phase 0: Foundation & Architecture</span>
              <Badge variant="success">Completed</Badge>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: 0.6 }}>
              <span style={{ fontSize: '0.9rem' }}>Phase 1: Indian Equities Data Ingestion</span>
              <Badge variant="warning">Locked</Badge>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: 0.6 }}>
              <span style={{ fontSize: '0.9rem' }}>Phase 2: Deterministic Financial Analytics</span>
              <Badge variant="warning">Locked</Badge>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: 0.6 }}>
              <span style={{ fontSize: '0.9rem' }}>Phase 3: AI Explanation & Decision Engine</span>
              <Badge variant="warning">Locked</Badge>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
