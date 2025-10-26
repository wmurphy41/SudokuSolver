import { useState } from 'react';
import { solve } from '../services/api';
import type { SolveResponse, Grid } from '../types/api';
import ResultPanel from './ResultPanel';
import EditableGrid from './EditableGrid';

/**
 * SolveForm Component
 * 
 * Provides a form for users to input a sudoku puzzle and solve it.
 * Accepts puzzle as JSON grid or 81-character string (0-9).
 */

type Mode = 'edit' | 'result';

// Sample puzzles for testing
const SAMPLE_PUZZLES: Record<string, Grid> = {
  easy: [[5, 0, 0, 4, 3, 0, 1, 0, 0],[0, 0, 3, 1, 5, 0, 0, 4, 8],[1, 0, 0, 0, 2, 0, 0, 7, 0],[7, 0, 0, 6, 0, 0, 5, 1, 0],[0, 4, 0, 0, 0, 5, 7, 2, 9],[0, 5, 1, 9, 0, 4, 0, 0, 0],[6, 2, 0, 7, 0, 8, 0, 0, 1],[3, 9, 8, 0, 0, 0, 0, 0, 7],[0, 0, 7, 5, 0, 0, 9, 0, 2]],
  medium: [[0, 5, 0, 0, 4, 9, 3, 0, 0],[0, 0, 0, 0, 0, 0, 0, 7, 0],[0, 0, 0, 0, 1, 0, 6, 0, 0],[0, 0, 9, 0, 0, 0, 5, 0, 8],[0, 0, 3, 0, 9, 1, 0, 0, 0],[2, 0, 0, 0, 8, 5, 0, 0, 0],[0, 4, 0, 0, 5, 2, 0, 0, 0],[0, 0, 1, 6, 0, 0, 0, 4, 0],[6, 0, 0, 0, 0, 0, 0, 2, 0]],
  hard: [[0, 0, 0, 9, 3, 0, 4, 0, 0],[0, 4, 0, 0, 5, 0, 8, 0, 0],[5, 0, 0, 0, 0, 0, 0, 9, 6],[0, 0, 0, 4, 0, 1, 0, 6, 0],[0, 2, 0, 0, 0, 0, 0, 0, 8],[0, 0, 8, 0, 0, 6, 0, 0, 0],[0, 3, 0, 0, 2, 0, 0, 1, 0],[0, 0, 2, 0, 0, 0, 9, 7, 0],[0, 1, 0, 0, 0, 0, 0, 0, 0]],
};

// Empty grid for initialization and clear button
const EMPTY_GRID: Grid = Array.from({ length: 9 }, () => Array(9).fill(0));

export default function SolveForm() {
  const [grid, setGrid] = useState<Grid>(EMPTY_GRID);
  const [debugLevel, setDebugLevel] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [originalGrid, setOriginalGrid] = useState<Grid | null>(null);
  const [mode, setMode] = useState<Mode>('edit');

  /**
   * Load a sample puzzle or clear the grid
   */
  const loadSamplePuzzle = (type: 'clear' | 'easy' | 'medium' | 'hard') => {
    if (type === 'clear') {
      setGrid(EMPTY_GRID);
    } else {
      setGrid(SAMPLE_PUZZLES[type]);
    }
    // Clear any previous results/errors when loading a new sample
    setResult(null);
    setValidationError(null);
    setNetworkError(null);
    setOriginalGrid(null);
    setMode('edit');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clear all error states
    setValidationError(null);
    setNetworkError(null);
    setResult(null);
    
    // Check if grid has any non-zero values
    const hasValues = grid.some(row => row.some(cell => cell !== 0));
    if (!hasValues) {
      setValidationError('Please enter a puzzle (grid is empty)');
      return;
    }

    setLoading(true);

    try {
      // Store the original grid for display
      setOriginalGrid(grid.map(row => [...row])); // Deep copy
      
      // Call API with structured grid and debug level
      const response = await solve({ grid, debug_level: debugLevel });
      
      // Store result regardless of success/failure
      // The response.success field will determine how we display it
      setResult(response);
      
      // Switch to result mode after solving (success or failure)
      setMode('result');
      
    } catch (err) {
      // This is a network or API error
      setNetworkError(err instanceof Error ? err.message : 'Failed to solve puzzle');
      setResult(null);
      setOriginalGrid(null);
      setMode('result'); // Still switch to result mode to show the error
    } finally {
      setLoading(false);
    }
  };

  const handleNewPuzzle = () => {
    setGrid(EMPTY_GRID);
    setResult(null);
    setValidationError(null);
    setNetworkError(null);
    setOriginalGrid(null);
    setLoading(false);
    setMode('edit');
    
    // Focus first cell after state updates
    requestAnimationFrame(() => {
      const el = document.querySelector<HTMLInputElement>('[aria-label="r1 c1 entry"]');
      el?.focus();
    });
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
    fontWeight: 'bold',
    fontSize: '14px',
    color: '#333',
    textAlign: 'left',
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

  const newPuzzleButtonStyle: React.CSSProperties = {
    width: '100%',
    padding: '12px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    backgroundColor: '#28a745',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  };

  return (
    <div style={containerStyle}>
      {/* EDIT MODE: Show input form with grid, sample buttons, debug level, and solve button */}
      {mode === 'edit' && (
        <form onSubmit={handleSubmit}>
          <div style={formGroupStyle}>
            <label style={labelStyle}>
              Puzzle
            </label>
            <EditableGrid 
              value={grid} 
              onChange={setGrid} 
              disabled={loading}
            />
          </div>

          <div style={formGroupStyle}>
            <div style={sampleLoaderStyle}>
              <span style={{ fontWeight: 'bold', color: '#333' }}>Load Example:</span>
              <button
                type="button"
                style={sampleButtonStyle}
                onClick={() => loadSamplePuzzle('clear')}
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
                Clear
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
            disabled={loading}
            onMouseOver={(e) => {
              if (!loading) {
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
      )}

      {/* RESULT MODE: Show result panel and New Puzzle button */}
      {mode === 'result' && (
        <>
          <ResultPanel 
            result={result} 
            validationError={validationError}
            networkError={networkError}
            originalGrid={originalGrid} 
          />
          <div style={{ marginTop: '16px' }}>
            <button
              type="button"
              style={newPuzzleButtonStyle}
              onClick={handleNewPuzzle}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#218838';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#28a745';
              }}
            >
              New Puzzle
            </button>
          </div>
        </>
      )}
    </div>
  );
}

