import { useEffect, useState } from 'react';
import { getHealth } from '../services/api';

/**
 * HealthCheck Component
 * 
 * Displays the API health status as a small badge.
 * Checks the backend health endpoint on mount.
 */
export default function HealthCheck() {
  const [status, setStatus] = useState<'loading' | 'ok' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');

  useEffect(() => {
    // Check API health on component mount
    const checkHealth = async () => {
      try {
        const response = await getHealth();
        if (response.status === 'ok') {
          setStatus('ok');
        } else {
          setStatus('error');
          setErrorMessage('Unexpected status');
        }
      } catch (error) {
        setStatus('error');
        setErrorMessage(error instanceof Error ? error.message : 'Connection failed');
      }
    };

    checkHealth();
  }, []);

  // Styles for the badge
  const badgeStyle: React.CSSProperties = {
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '14px',
    fontWeight: '600',
    backgroundColor: status === 'ok' ? '#d4edda' : status === 'error' ? '#f8d7da' : '#e2e3e5',
    color: status === 'ok' ? '#155724' : status === 'error' ? '#721c24' : '#6c757d',
    border: `1px solid ${status === 'ok' ? '#c3e6cb' : status === 'error' ? '#f5c6cb' : '#d6d8db'}`,
  };

  return (
    <div style={badgeStyle}>
      {status === 'loading' && 'API: checking...'}
      {status === 'ok' && 'API: ✓ ok'}
      {status === 'error' && `API: ✗ ${errorMessage}`}
    </div>
  );
}

