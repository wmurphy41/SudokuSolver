import type { SolveResponse, Grid } from '../types/api';
import SolutionGrid from './SolutionGrid';

/**
 * ResultPanel Component
 * 
 * Displays the results of a sudoku solve request.
 * Shows success/fail status, original puzzle grid, solution grid, and detailed message.
 */

function formatFullSolveStatusMessage(success: boolean): string {
  if (success) {
    return "Solving Status: Solved";
  } else {
    return "Solving Status: Stuck\nPuzzle may be unsolvable";
  }
}

interface ResultPanelProps {
  result: SolveResponse | null;
  validationError?: string | null;
  networkError?: string | null;
  originalGrid?: Grid | null;
  showOriginal?: boolean;
  onToggleShowOriginal?: () => void;
}

export default function ResultPanel({ result, validationError, networkError, originalGrid, showOriginal = false, onToggleShowOriginal }: ResultPanelProps) {
  // CONDITION 1: Validation Error (Invalid Input Data)
  if (validationError) {
    return (
      <div className="result-panel">
        {/* Validation error message box */}
        <div className="message-box" aria-label="Validation error message">
          <div className="message-label">Validation Error:</div>
          <div className="message-content">
            {validationError}
          </div>
        </div>
      </div>
    );
  }

  // Network Error (separate from validation)
  if (networkError) {
    return (
      <div className="result-panel">
        {/* Network error message box */}
        <div className="message-box" aria-label="Network error message">
          <div className="message-label">Error:</div>
          <div className="message-content">
            {networkError}
          </div>
        </div>
      </div>
    );
  }

  // CONDITION 2: Valid Data but Solver Failed (success: false)
  if (result && !result.success) {
    return (
      <div className="result-panel">
        {(showOriginal ? originalGrid : result.solution) && (
          <div aria-label={showOriginal ? "Original puzzle grid" : "Attempted solution grid"}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div className="solution-label">
                {showOriginal ? 'Original Puzzle:' : 'Solving Puzzle (Full Solve Mode)'}
              </div>
              {onToggleShowOriginal && (
                <button
                  type="button"
                  onClick={onToggleShowOriginal}
                  style={{
                    padding: '6px 12px',
                    fontSize: '13px',
                    fontWeight: '500',
                    color: showOriginal ? 'white' : '#007bff',
                    backgroundColor: showOriginal ? '#007bff' : 'white',
                    border: '1px solid #007bff',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  {showOriginal ? 'Show Original ✓' : 'Show Original'}
                </button>
              )}
            </div>
            <SolutionGrid
              grid={showOriginal && originalGrid ? originalGrid : result.solution!}
              showCandidates={!showOriginal}
              candidates={!showOriginal ? result.candidates ?? null : null}
            />
          </div>
        )}

        {/* Solver output message */}
        <div className="message-box" aria-label="Solver output">
          <div className="message-label">Solver Output:</div>
          <div className="message-content">
            {formatFullSolveStatusMessage(false)}
          </div>
        </div>
      </div>
    );
  }

  // Success case (result.success === true)
  if (result && result.success) {
    return (
      <div className="result-panel">
        {/* Solution grid */}
        {(showOriginal ? originalGrid : result.solution) && (
          <div aria-label={showOriginal ? "Original puzzle grid" : "Solved puzzle grid"}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div className="solution-label">
                {showOriginal ? 'Original Puzzle:' : 'Solving Puzzle (Full Solve Mode)'}
              </div>
              {onToggleShowOriginal && (
                <button
                  type="button"
                  onClick={onToggleShowOriginal}
                  style={{
                    padding: '6px 12px',
                    fontSize: '13px',
                    fontWeight: '500',
                    color: showOriginal ? 'white' : '#007bff',
                    backgroundColor: showOriginal ? '#007bff' : 'white',
                    border: '1px solid #007bff',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  {showOriginal ? 'Show Original ✓' : 'Show Original'}
                </button>
              )}
            </div>
            <SolutionGrid
              grid={showOriginal && originalGrid ? originalGrid : result.solution!}
              showCandidates={!showOriginal}
              candidates={!showOriginal ? result.candidates ?? null : null}
            />
          </div>
        )}

        {/* Solver output message */}
        <div className="message-box" aria-label="Solver output">
          <div className="message-label">Solver Output:</div>
          <div className="message-content">
            {formatFullSolveStatusMessage(result.success)}
          </div>
        </div>
      </div>
    );
  }

  // Don't render anything if no result and no errors
  return null;
}

