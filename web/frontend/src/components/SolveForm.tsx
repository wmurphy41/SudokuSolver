import { useState } from 'react';
import { solve } from '../services/api';
import type { SolveResponse, Grid } from '../types/api';
import ResultPanel from './ResultPanel';

/**
 * SolveForm Component
 * 
 * Provides a form for users to input a sudoku puzzle and solve it.
 * Accepts puzzle as JSON grid or 81-character string (0-9).
 */
export default function SolveForm() {
  const [puzzle, setPuzzle] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [originalGrid, setOriginalGrid] = useState<Grid | null>(null);

  /**
   * Parse user input into a 9x9 grid
   * Supports JSON array format or 81-character string
   */
  const parseInputToGrid = (input: string): Grid => {
    const trimmed = input.trim();

    // Try parsing as JSON first
    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed) && parsed.length === 9) {
        // Validate it's a proper 9x9 grid
        if (parsed.every(row => Array.isArray(row) && row.length === 9)) {
          return parsed as Grid;
        }
      }
    } catch {
      // Not JSON, try other formats
    }

    // Try parsing as 81-character string (digits only)
    const digitsOnly = trimmed.replace(/[^0-9]/g, '');
    if (digitsOnly.length === 81) {
      const grid: Grid = [];
      for (let i = 0; i < 9; i++) {
        const row: number[] = [];
        for (let j = 0; j < 9; j++) {
          row.push(parseInt(digitsOnly[i * 9 + j]));
        }
        grid.push(row);
      }
      return grid;
    }

    throw new Error('Invalid puzzle format. Expected JSON grid or 81 digits (0-9).');
  };

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
      // Parse input into grid
      const grid = parseInputToGrid(puzzle);
      
      // Store the original grid for display
      setOriginalGrid(grid);
      
      // Call API with structured grid
      const response = await solve({ grid, debug_level: 0 });
      setResult(response);
      setError(null); // Clear any previous errors on success
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to solve puzzle');
      setResult(null);
      setOriginalGrid(null);
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
            placeholder="Enter puzzle as:
• JSON array: [[5,3,0,...],[6,0,0,...],...]
• 81 digits: 530070000600195000098000060800060003400803001700020006060000280000419005000080079
Use 0 for empty cells."
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

      {/* Result panel - shows success/fail status, original puzzle, solution, and message */}
      <ResultPanel result={result} error={error} originalGrid={originalGrid} />
    </div>
  );
}

