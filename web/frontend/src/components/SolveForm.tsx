import { useState } from 'react';
import { solve } from '../services/api';
import type { Difficulty } from '../types/api';

/**
 * SolveForm Component
 * 
 * Provides a form for users to input a sudoku puzzle and solve it.
 * Accepts puzzle as an 81-character string or JSON string.
 */
export default function SolveForm() {
  const [puzzle, setPuzzle] = useState<string>('');
  const [difficulty, setDifficulty] = useState<Difficulty>('easy');
  const [loading, setLoading] = useState<boolean>(false);
  const [solution, setSolution] = useState<string>('');
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!puzzle.trim()) {
      setError('Please enter a puzzle');
      return;
    }

    setLoading(true);
    setError('');
    setSolution('');
    setMessage('');

    try {
      const response = await solve({ puzzle, difficulty });
      
      if (response.success) {
        setSolution(response.solution);
        setMessage(response.message);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to solve puzzle');
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

  const selectStyle: React.CSSProperties = {
    width: '100%',
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ccc',
    borderRadius: '4px',
    backgroundColor: 'white',
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

  const resultBoxStyle: React.CSSProperties = {
    marginTop: '20px',
    padding: '16px',
    borderRadius: '4px',
    backgroundColor: '#f8f9fa',
    border: '1px solid #dee2e6',
  };

  const errorBoxStyle: React.CSSProperties = {
    ...resultBoxStyle,
    backgroundColor: '#f8d7da',
    border: '1px solid #f5c6cb',
    color: '#721c24',
  };

  const successBoxStyle: React.CSSProperties = {
    ...resultBoxStyle,
    backgroundColor: '#d4edda',
    border: '1px solid #c3e6cb',
    color: '#155724',
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

        <div style={formGroupStyle}>
          <label htmlFor="difficulty" style={labelStyle}>
            Difficulty
          </label>
          <select
            id="difficulty"
            style={selectStyle}
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value as Difficulty)}
            disabled={loading}
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
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

      {/* Error message */}
      {error && (
        <div style={errorBoxStyle}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Success message and solution */}
      {solution && (
        <div style={successBoxStyle}>
          <div style={{ marginBottom: '12px' }}>
            <strong>Status:</strong> {message}
          </div>
          <div>
            <strong>Solution:</strong>
            <pre style={{ 
              marginTop: '8px', 
              padding: '10px', 
              backgroundColor: 'white',
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '12px',
            }}>
              {solution}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

