import { useState } from 'react';
import { solve } from '../services/api';
import type { SolveResponse } from '../types/api';
import ResultPanel from './ResultPanel';

/**
 * SolveForm Component
 * 
 * Provides a form for users to input a sudoku puzzle and solve it.
 * Accepts puzzle as an 81-character string or JSON string.
 */
export default function SolveForm() {
  const [puzzle, setPuzzle] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!puzzle.trim()) {
      setError('Please enter a puzzle');
      setResult(null);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await solve({ puzzle });
      setResult(response);
      setError(null); // Clear any previous errors on success
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to solve puzzle');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  // Styles
  const containerStyle: React.CSSProperties = {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '20px',
  };

  const formGroupStyle: React.CSSProperties = {
    marginBottom: '16px',
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    marginBottom: '8px',
    fontWeight: '600',
    fontSize: '14px',
    color: '#333',
  };

  const textareaStyle: React.CSSProperties = {
    width: '100%',
    minHeight: '120px',
    padding: '10px',
    fontSize: '14px',
    fontFamily: 'monospace',
    border: '1px solid #ccc',
    borderRadius: '4px',
    resize: 'vertical',
  };

  const buttonStyle: React.CSSProperties = {
    width: '100%',
    padding: '12px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    backgroundColor: loading ? '#6c757d' : '#007bff',
    border: 'none',
    borderRadius: '4px',
    cursor: loading ? 'not-allowed' : 'pointer',
    transition: 'background-color 0.2s',
  };

  return (
    <div style={containerStyle}>
      <form onSubmit={handleSubmit}>
        <div style={formGroupStyle}>
          <label htmlFor="puzzle" style={labelStyle}>
            Puzzle
          </label>
          <textarea
            id="puzzle"
            style={textareaStyle}
            value={puzzle}
            onChange={(e) => setPuzzle(e.target.value)}
            placeholder="Enter puzzle as 81-character string (e.g., '000000000123...') or JSON string. Use 0 for empty cells."
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          style={buttonStyle}
          disabled={loading || !puzzle.trim()}
          onMouseOver={(e) => {
            if (!loading && puzzle.trim()) {
              e.currentTarget.style.backgroundColor = '#0056b3';
            }
          }}
          onMouseOut={(e) => {
            if (!loading) {
              e.currentTarget.style.backgroundColor = '#007bff';
            }
          }}
        >
          {loading ? 'Solving...' : 'Solve Puzzle'}
        </button>
      </form>

      {/* Result panel - shows success/fail status, solution, and message */}
      <ResultPanel result={result} error={error} />
    </div>
  );
}

