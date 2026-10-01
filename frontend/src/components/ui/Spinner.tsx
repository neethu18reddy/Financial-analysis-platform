import React from 'react';
import { Loader2 } from 'lucide-react';

interface SpinnerProps {
  size?: number;
  text?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 20, text }) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
      <Loader2 size={size} style={{ animation: 'spin 1s linear infinite' }} />
      {text && <span style={{ fontSize: '0.875rem' }}>{text}</span>}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
