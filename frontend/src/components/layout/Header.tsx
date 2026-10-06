import React from 'react';
import { ShieldCheck, Activity } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface HeaderProps {
  currentTab: string;
  systemStatus: string;
  version: string;
}

const TAB_TITLES: Record<string, { title: string; phase: string }> = {
  ai_analyst: { title: 'AI Analyst, Historical Validation & Research Product', phase: 'Phase 7' },
  annual_reports: { title: 'Document Intelligence & Statutory Annual Report RAG', phase: 'Phase 6' },
  valuation: { title: 'Valuation Modeling & Reverse DCF Workbench', phase: 'Phase 4' },
  forensics: { title: 'Forensic Intelligence & Manipulation Detection', phase: 'Phase 3' },
  fundamental: { title: 'Fundamental Analysis & DuPont Decomposition', phase: 'Phase 2' },
  financials: { title: 'Statutory Financial Data Engine & Provenance', phase: 'Phase 1' },
  health: { title: 'System Diagnostics & Engine Subsystems', phase: 'Phase 0' },
  architecture: { title: 'System Architecture & Deterministic Rules', phase: 'Phase 0' },
  pipeline: { title: 'Data Ingestion & Normalization Pipeline', phase: 'Phase 0' },
};

export const Header: React.FC<HeaderProps> = ({ currentTab, systemStatus, version }) => {
  const currentInfo = TAB_TITLES[currentTab] || { title: 'Financial Decision Intelligence', phase: 'Active' };

  return (
    <header className="top-bar">
      {/* Left: Active Module Title & Phase Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', letterSpacing: '-0.02em' }}>
          {currentInfo.title}
        </h2>
        <Badge variant="info">{currentInfo.phase}</Badge>
      </div>

      {/* Right: Market Status, Deterministic Verification & Health */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* Market Live Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', padding: '0.3rem 0.65rem', background: 'rgba(16, 185, 129, 0.08)', borderRadius: '6px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <span className="pulse-dot" />
          <span style={{ fontWeight: 600, color: 'var(--success)' }}>NSE / BSE LIVE</span>
        </div>

        {/* Deterministic Guarantee */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          <ShieldCheck size={16} color="var(--accent-primary)" />
          <span>Deterministic Core:</span>
          <span style={{ fontWeight: 600, color: '#ffffff' }}>Verified</span>
        </div>

        {/* System Health */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Activity size={15} color={systemStatus === 'healthy' ? 'var(--success)' : 'var(--warning)'} />
          <Badge variant={systemStatus === 'healthy' ? 'success' : 'warning'}>
            {systemStatus.toUpperCase()}
          </Badge>
        </div>

        {/* Version */}
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          v{version}
        </div>
      </div>
    </header>
  );
};
