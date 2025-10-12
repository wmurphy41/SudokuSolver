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

// Sample puzzles for testing
const SAMPLE_PUZZLES = {
  empty: [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
  easy: [[5, 0, 0, 4, 3, 0, 1, 0, 0],[0, 0, 3, 1, 5, 0, 0, 4, 8],[1, 0, 0, 0, 2, 0, 0, 7, 0],[7, 0, 0, 6, 0, 0, 5, 1, 0],[0, 4, 0, 0, 0, 5, 7, 2, 9],[0, 5, 1, 9, 0, 4, 0, 0, 0],[6, 2, 0, 7, 0, 8, 0, 0, 1],[3, 9, 8, 0, 0, 0, 0, 0, 7],[0, 0, 7, 5, 0, 0, 9, 0, 2]],
  medium: [[0, 5, 0, 0, 4, 9, 3, 0, 0],[0, 0, 0, 0, 0, 0, 0, 7, 0],[0, 0, 0, 0, 1, 0, 6, 0, 0],[0, 0, 9, 0, 0, 0, 5, 0, 8],[0, 0, 3, 0, 9, 1, 0, 0, 0],[2, 0, 0, 0, 8, 5, 0, 0, 0],[0, 4, 0, 0, 5, 2, 0, 0, 0],[0, 0, 1, 6, 0, 0, 0, 4, 0],[6, 0, 0, 0, 0, 0, 0, 2, 0]],
  hard: [[0, 0, 0, 9, 3, 0, 4, 0, 0],[0, 4, 0, 0, 5, 0, 8, 0, 0],[5, 0, 0, 0, 0, 0, 0, 9, 6],[0, 0, 0, 4, 0, 1, 0, 6, 0],[0, 2, 0, 0, 0, 0, 0, 0, 8],[0, 0, 8, 0, 0, 6, 0, 0, 0],[0, 3, 0, 0, 2, 0, 0, 1, 0],[0, 0, 2, 0, 0, 0, 9, 7, 0],[0, 1, 0, 0, 0, 0, 0, 0, 0]],
};

export default function SolveForm() {
  const [puzzle, setPuzzle] = useState<string>('');
  const [debugLevel, setDebugLevel] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [originalGrid, setOriginalGrid] = useState<Grid | null>(null);

  /**
   * Load a sample puzzle into the input textarea
   * Formats with line breaks after each row for better readability
   */
  const loadSamplePuzzle = (difficulty: 'empty' | 'easy' | 'medium' | 'hard') => {
    const sampleGrid = SAMPLE_PUZZLES[difficulty];
    // Format with each row on its own line
    const formatted = '[' + 
      sampleGrid.map(row => '\n  ' + JSON.stringify(row)).join(',') + 
      '\n]';
    setPuzzle(formatted);
    // Clear any previous results/errors when loading a new sample
    setResult(null);
    setValidationError(null);
    setNetworkError(null);
    setOriginalGrid(null);
  };

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
    
    // Clear all error states
    setValidationError(null);
    setNetworkError(null);
    setResult(null);
    
    // Basic validation - empty input
    if (!puzzle.trim()) {
      setValidationError('Please enter a puzzle');
      return;
    }

    setLoading(true);

    try {
      // Parse input into grid - this can throw validation errors
      const grid = parseInputToGrid(puzzle);
      
      // Store the original grid for display
      setOriginalGrid(grid);
      
      // Call API with structured grid and debug level
      const response = await solve({ grid, debug_level: debugLevel });
      
      // Store result regardless of success/failure
      // The response.success field will determine how we display it
      setResult(response);
      
    } catch (err) {
      // Determine error type based on error message
      if (err instanceof Error && err.message.includes('Invalid puzzle format')) {
        // This is a validation error from parseInputToGrid()
        setValidationError(err.message);
      } else {
        // This is a network or other error
        setNetworkError(err instanceof Error ? err.message : 'Failed to solve puzzle');
      }
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
    fontWeight: 'bold',  // Changed to bold
    fontSize: '14px',
    color: '#333',
    textAlign: 'left',  // Left justified
  };

  const textareaStyle: React.CSSProperties = {
    width: '100%',
    minHeight: '240px',  // Increased to fit 11 rows (9 puzzle rows + opening/closing brackets)
    padding: '10px',
    fontSize: '14px',
    fontFamily: 'monospace',
    border: '1px solid #ccc',
    borderRadius: '4px',
    resize: 'vertical',
  };

  const radioGroupStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'row',  // Changed to row for horizontal layout
    gap: '16px',  // Increased gap for better spacing
    flexWrap: 'wrap',  // Allow wrapping on small screens
  };

  const radioLabelStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    fontSize: '14px',
    color: '#333',
    cursor: loading ? 'not-allowed' : 'pointer',
  };

  const radioInputStyle: React.CSSProperties = {
    marginRight: '8px',
    cursor: loading ? 'not-allowed' : 'pointer',
  };

  const sampleLoaderStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
  };

  const sampleButtonStyle: React.CSSProperties = {
    padding: '6px 12px',
    fontSize: '13px',
    fontWeight: '500',
    color: '#007bff',
    backgroundColor: 'white',
    border: '1px solid #007bff',
    borderRadius: '4px',
    cursor: loading ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s',
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

        <div style={formGroupStyle}>
          <div style={sampleLoaderStyle}>
            <span style={{ fontWeight: 'bold', color: '#333' }}>Load Example:</span>
            <button
              type="button"
              style={sampleButtonStyle}
              onClick={() => loadSamplePuzzle('empty')}
              disabled={loading}
              onMouseOver={(e) => {
                if (!loading) {
                  e.currentTarget.style.backgroundColor = '#007bff';
                  e.currentTarget.style.color = 'white';
                }
              }}
              onMouseOut={(e) => {
                if (!loading) {
                  e.currentTarget.style.backgroundColor = 'white';
                  e.currentTarget.style.color = '#007bff';
                }
              }}
            >
              Empty
            </button>
            <button
              type="button"
              style={sampleButtonStyle}
              onClick={() => loadSamplePuzzle('easy')}
              disabled={loading}
              onMouseOver={(e) => {
                if (!loading) {
                  e.currentTarget.style.backgroundColor = '#007bff';
                  e.currentTarget.style.color = 'white';
                }
              }}
              onMouseOut={(e) => {
                if (!loading) {
                  e.currentTarget.style.backgroundColor = 'white';
                  e.currentTarget.style.color = '#007bff';
                }
              }}
            >
              Easy
            </button>
            <button
              type="button"
              style={sampleButtonStyle}
              onClick={() => loadSamplePuzzle('medium')}
              disabled={loading}
              onMouseOver={(e) => {
                if (!loading) {
                  e.currentTarget.style.backgroundColor = '#007bff';
                  e.currentTarget.style.color = 'white';
                }
              }}
              onMouseOut={(e) => {
                if (!loading) {
                  e.currentTarget.style.backgroundColor = 'white';
                  e.currentTarget.style.color = '#007bff';
                }
              }}
            >
              Medium
            </button>
            <button
              type="button"
              style={sampleButtonStyle}
              onClick={() => loadSamplePuzzle('hard')}
              disabled={loading}
              onMouseOver={(e) => {
                if (!loading) {
                  e.currentTarget.style.backgroundColor = '#007bff';
                  e.currentTarget.style.color = 'white';
                }
              }}
              onMouseOut={(e) => {
                if (!loading) {
                  e.currentTarget.style.backgroundColor = 'white';
                  e.currentTarget.style.color = '#007bff';
                }
              }}
            >
              Hard
            </button>
          </div>
        </div>

        <div style={formGroupStyle}>
          <label style={labelStyle}>
            Debug Level
          </label>
          <div style={radioGroupStyle}>
            <label style={radioLabelStyle}>
              <input
                type="radio"
                name="debugLevel"
                value="0"
                checked={debugLevel === 0}
                onChange={(e) => setDebugLevel(parseInt(e.target.value))}
                disabled={loading}
                style={radioInputStyle}
              />
              <span>0 - Silent</span>
            </label>
            <label style={radioLabelStyle}>
              <input
                type="radio"
                name="debugLevel"
                value="1"
                checked={debugLevel === 1}
                onChange={(e) => setDebugLevel(parseInt(e.target.value))}
                disabled={loading}
                style={radioInputStyle}
              />
              <span>1 - Informational</span>
            </label>
            <label style={radioLabelStyle}>
              <input
                type="radio"
                name="debugLevel"
                value="2"
                checked={debugLevel === 2}
                onChange={(e) => setDebugLevel(parseInt(e.target.value))}
                disabled={loading}
                style={radioInputStyle}
              />
              <span>2 - Basic</span>
            </label>
            <label style={radioLabelStyle}>
              <input
                type="radio"
                name="debugLevel"
                value="3"
                checked={debugLevel === 3}
                onChange={(e) => setDebugLevel(parseInt(e.target.value))}
                disabled={loading}
                style={radioInputStyle}
              />
              <span>3 - Detailed</span>
            </label>
          </div>
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
      <ResultPanel 
        result={result} 
        validationError={validationError}
        networkError={networkError}
        originalGrid={originalGrid} 
      />
    </div>
  );
}

