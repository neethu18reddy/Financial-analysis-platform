import { Activity, Layers, Database, Lock, Terminal, Building2, TrendingUp, ShieldAlert, DollarSign, BookOpen } from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab }) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div style={{
          width: 32,
          height: 32,
          borderRadius: 6,
          backgroundColor: 'var(--accent-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 'bold',
          fontSize: '1.1rem'
        }}>
          ₹
        </div>
        <div>
          <div className="sidebar-title">ANTIGRAVITY</div>
          <div className="sidebar-subtitle">Equities Intelligence</div>
        </div>
      </div>

      <nav className="nav-links">
        <div style={{ padding: '0.5rem 0.75rem', fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
          Phase 0 Foundation
        </div>
        <div
          className={`nav-item ${currentTab === 'health' ? 'active' : ''}`}
          onClick={() => onSelectTab('health')}
        >
          <Activity size={18} />
          <span>System & Subsystems</span>
        </div>
        <div
          className={`nav-item ${currentTab === 'architecture' ? 'active' : ''}`}
          onClick={() => onSelectTab('architecture')}
        >
          <Layers size={18} />
          <span>Architecture & Rules</span>
        </div>
        <div
          className={`nav-item ${currentTab === 'pipeline' ? 'active' : ''}`}
          onClick={() => onSelectTab('pipeline')}
        >
          <Database size={18} />
          <span>Data Pipeline Spec</span>
        </div>

        <div style={{ marginTop: '1.25rem', padding: '0.5rem 0.75rem', fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
          Phase 1 Data Engine
        </div>
        <div
          className={`nav-item ${currentTab === 'financials' ? 'active' : ''}`}
          onClick={() => onSelectTab('financials')}
        >
          <Building2 size={18} />
          <span>Financial Data Engine</span>
        </div>

        <div style={{ marginTop: '1.25rem', padding: '0.5rem 0.75rem', fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
          Phase 2 Fundamental Engine
        </div>
        <div
          className={`nav-item ${currentTab === 'fundamental' ? 'active' : ''}`}
          onClick={() => onSelectTab('fundamental')}
        >
          <TrendingUp size={18} />
          <span>Fundamental Analysis</span>
        </div>

        <div style={{ marginTop: '1.25rem', padding: '0.5rem 0.75rem', fontSize: '0.7rem', color: 'var(--accent-primary)', fontWeight: 700, textTransform: 'uppercase' }}>
          Phase 3 Forensic Engine
        </div>
        <div
          className={`nav-item ${currentTab === 'forensics' ? 'active' : ''}`}
          onClick={() => onSelectTab('forensics')}
        >
          <ShieldAlert size={18} />
          <span>Forensic Intelligence</span>
        </div>

        <div style={{ marginTop: '1.25rem', padding: '0.5rem 0.75rem', fontSize: '0.7rem', color: 'var(--accent-primary)', fontWeight: 700, textTransform: 'uppercase' }}>
          Phase 4 Valuation Engine
        </div>
        <div
          className={`nav-item ${currentTab === 'valuation' ? 'active' : ''}`}
          onClick={() => onSelectTab('valuation')}
        >
          <DollarSign size={18} />
          <span>Valuation & DCF Engine</span>
        </div>

        <div style={{ marginTop: '1.25rem', padding: '0.5rem 0.75rem', fontSize: '0.7rem', color: 'var(--accent-primary)', fontWeight: 700, textTransform: 'uppercase' }}>
          Phase 6 Annual Reports (RAG)
        </div>
        <div
          className={`nav-item ${currentTab === 'annual_reports' ? 'active' : ''}`}
          onClick={() => onSelectTab('annual_reports')}
        >
          <BookOpen size={18} />
          <span>Annual Report Intelligence</span>
        </div>

        <div style={{ marginTop: '1.25rem', padding: '0.5rem 0.75rem', fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
          Future Phases (Locked)
        </div>
        <div className="nav-item" style={{ opacity: 0.45, cursor: 'not-allowed' }}>
          <Lock size={16} />
          <span>AI Multi-Agent Analyst (P7)</span>
        </div>
      </nav>

      <div style={{ padding: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.25rem' }}>
          <Terminal size={14} />
          <span>Target Market: NSE / BSE</span>
        </div>
        <div>Indian Listed Companies</div>
      </div>
    </aside>
  );
};
