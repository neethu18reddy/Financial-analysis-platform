import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-color)',
      padding: '1.25rem 2rem',
      backgroundColor: 'var(--bg-secondary)',
      fontSize: '0.8rem',
      color: 'var(--text-muted)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div>
        <span>Deterministic Rule: </span>
        <strong style={{ color: 'var(--text-secondary)' }}>
          DATA → VALIDATION → CALCULATIONS → ANALYTICS → EVIDENCE → AI EXPLANATION
        </strong>
      </div>
      <div>
        <span>Institutional Grade Financial Platform · Phase 0 Foundation</span>
      </div>
    </footer>
  );
};
