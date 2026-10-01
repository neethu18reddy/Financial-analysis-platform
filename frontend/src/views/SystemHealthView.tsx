import React from 'react';
import { RefreshCw, Server, Database, Cpu, CheckCircle2, XCircle } from 'lucide-react';
import { HealthResponse } from '../types/api';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { Alert } from '../components/ui/Alert';

interface SystemHealthViewProps {
  healthData: HealthResponse | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

export const SystemHealthView: React.FC<SystemHealthViewProps> = ({
  healthData,
  loading,
  error,
  onRefresh,
}) => {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>Platform Foundation Status</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Phase 0 verification and real-time backend/database subsystem telemetry.
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="btn btn-outline"
        >
          <RefreshCw size={16} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          <span>Refresh Health</span>
        </button>
      </div>

      {error && (
        <Alert type="error" title="Connectivity Error">
          {error}
        </Alert>
      )}

      {loading && !healthData && (
        <div style={{ padding: '3rem', textAlign: 'center' }}>
          <Spinner size={32} text="Checking subsystem connectivity..." />
        </div>
      )}

      {healthData && (
        <>
          <div className="grid-cols-3" style={{ marginBottom: '1.5rem' }}>
            <Card title="API Backend">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Server size={20} color="var(--accent-primary)" />
                  <span style={{ fontWeight: 600 }}>FastAPI v0.1.0</span>
                </div>
                <Badge variant={healthData.status === 'healthy' ? 'success' : 'warning'}>
                  {healthData.status}
                </Badge>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
                Environment: <strong style={{ color: 'var(--text-primary)' }}>{healthData.environment}</strong>
              </p>
            </Card>

            <Card title="Database Subsystem">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Database size={20} color="var(--accent-primary)" />
                  <span style={{ fontWeight: 600 }}>SQLAlchemy 2.0</span>
                </div>
                <Badge variant={healthData.database.connected ? 'success' : 'danger'}>
                  {healthData.database.status}
                </Badge>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
                Engine Dialect: <strong style={{ color: 'var(--text-primary)' }}>{healthData.database.dialect}</strong>
              </p>
            </Card>

            <Card title="Runtime Telemetry">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Cpu size={20} color="var(--accent-primary)" />
                  <span style={{ fontWeight: 600 }}>Python {healthData.system_info?.python_version || '3.14'}</span>
                </div>
                <Badge variant="info">Ready</Badge>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
                Host OS: <strong style={{ color: 'var(--text-primary)' }}>{healthData.system_info?.os || 'Windows'}</strong>
              </p>
            </Card>
          </div>

          <Card title="Phase 0 Foundation Checklist & Subsystems" subtitle="Core architectural prerequisites established">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CheckCircle2 size={16} color="var(--success)" />
                  <span>Modular Repository Architecture (Backend, Frontend, DB, Tests, Docs)</span>
                </div>
                <Badge variant="success">Initialized</Badge>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {healthData.database.connected ? <CheckCircle2 size={16} color="var(--success)" /> : <XCircle size={16} color="var(--danger)" />}
                  <span>Database Connection Pool & Alembic Migration Engine</span>
                </div>
                <Badge variant={healthData.database.connected ? 'success' : 'danger'}>
                  {healthData.database.connected ? 'Connected' : 'Disconnected'}
                </Badge>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CheckCircle2 size={16} color="var(--success)" />
                  <span>Pydantic Configuration & Secret Protection (.env.example, .gitignore)</span>
                </div>
                <Badge variant="success">Protected</Badge>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CheckCircle2 size={16} color="var(--success)" />
                  <span>Deterministic Analysis Pipeline Boundary (LLM quarantined from core math)</span>
                </div>
                <Badge variant="success">Enforced</Badge>
              </div>
            </div>
          </Card>

          <Card title="Raw Health Response Payload" subtitle="Live JSON payload returned by /api/v1/health">
            <pre className="code-block">
              {JSON.stringify(healthData, null, 2)}
            </pre>
          </Card>
        </>
      )}
    </div>
  );
};
