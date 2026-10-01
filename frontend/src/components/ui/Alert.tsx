import React from 'react';
import { AlertCircle, CheckCircle2, Info, AlertTriangle } from 'lucide-react';

interface AlertProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: React.ReactNode;
}

export const Alert: React.FC<AlertProps> = ({ type = 'info', title, children }) => {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle2 size={18} color="var(--success)" />;
      case 'warning':
        return <AlertTriangle size={18} color="var(--warning)" />;
      case 'error':
        return <AlertCircle size={18} color="var(--danger)" />;
      default:
        return <Info size={18} color="var(--accent-primary)" />;
    }
  };

  const getBorderColor = () => {
    switch (type) {
      case 'success': return 'var(--success)';
      case 'warning': return 'var(--warning)';
      case 'error': return 'var(--danger)';
      default: return 'var(--accent-primary)';
    }
  };

  return (
    <div style={{
      display: 'flex',
      gap: '0.75rem',
      padding: '1rem',
      borderRadius: '6px',
      backgroundColor: 'var(--bg-secondary)',
      borderLeft: `4px solid ${getBorderColor()}`,
      marginBottom: '1rem'
    }}>
      <div style={{ paddingTop: '2px' }}>{getIcon()}</div>
      <div>
        {title && <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.25rem', color: '#fff' }}>{title}</h4>}
        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{children}</div>
      </div>
    </div>
  );
};
