import React from 'react';
import { Activity, ShieldCheck } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface HeaderProps {
  systemStatus: string;
  version: string;
}

export const Header: React.FC<HeaderProps> = ({ systemStatus, version }) => {
  return (
    <header className="top-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <h2 style={{ fontSize: '1.05rem', fontWeight: 600 }}>System Foundation & Architecture Control</h2>
        <Badge variant="info">Phase 0</Badge>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
          <ShieldCheck size={16} color="var(--accent-primary)" />
          <span style={{ color: 'var(--text-secondary)' }}>Deterministic Engine:</span>
          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Verified</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
          <Activity size={16} color={systemStatus === 'healthy' ? 'var(--success)' : 'var(--warning)'} />
          <Badge variant={systemStatus === 'healthy' ? 'success' : 'warning'}>
            {systemStatus.toUpperCase()}
          </Badge>
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          v{version}
        </div>
      </div>
    </header>
  );
};
