import type { SolveResponse, Grid } from '../types/api';

/**
 * ResultPanel Component
 * 
 * Displays the results of a sudoku solve request.
 * Shows success/fail status, original puzzle grid, solution grid, and detailed message.
 */

interface ResultPanelProps {
  result: SolveResponse | null;
  validationError?: string | null;
  networkError?: string | null;
  originalGrid?: Grid | null;
}

/**
 * Helper function to render a 9x9 grid as an HTML table
 */
function renderGridTable(grid: Grid): JSX.Element {
  return (
    <table className="solution-grid">
      <tbody>
        {grid.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {row.map((cell, colIndex) => (
              <td 
                key={colIndex}
                className={cell === 0 ? 'empty-cell' : 'filled-cell'}
              >
                {cell === 0 ? '' : cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function ResultPanel({ result, validationError, networkError, originalGrid }: ResultPanelProps) {
  // CONDITION 1: Validation Error (Invalid Input Data)
  if (validationError) {
    return (
      <div className="result-panel">
        {/* Status badge - invalid data */}
        <div className="status-badge status-invalid" role="status" aria-live="polite">
          Invalid Data
        </div>

        {/* NO GRIDS DISPLAYED */}

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
        {/* Status badge - network error */}
        <div className="status-badge status-fail" role="status" aria-live="polite">
          Network Error
        </div>

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
        {/* Status badge - solver failure */}
        <div className="status-badge status-fail" role="status" aria-live="polite">
          Fail
        </div>

        {/* SHOW BOTH GRIDS - User can see what couldn't be solved */}
        {originalGrid && (
          <div className="solution-grid-container" aria-label="Original puzzle grid">
            <div className="solution-label">Original Puzzle:</div>
            {renderGridTable(originalGrid)}
          </div>
        )}

        {result.solution && (
          <div className="solution-grid-container" aria-label="Attempted solution grid">
            <div className="solution-label">Attempted Solution:</div>
            {renderGridTable(result.solution)}
          </div>
        )}

        {/* Solver output message */}
        <div className="message-box" aria-label="Solver output">
          <div className="message-label">Solver Output:</div>
          <div className="message-content">
            {result.message || '(no message)'}
          </div>
        </div>
      </div>
    );
  }

  // Success case (result.success === true)
  if (result && result.success) {
    return (
      <div className="result-panel">
        {/* Status badge - success */}
        <div className="status-badge status-success" role="status" aria-live="polite">
          Success
        </div>

        {/* Original puzzle grid */}
        {originalGrid && (
          <div className="solution-grid-container" aria-label="Original puzzle grid">
            <div className="solution-label">Original Puzzle:</div>
            {renderGridTable(originalGrid)}
          </div>
        )}

        {/* Solution grid */}
        {result.solution && (
          <div className="solution-grid-container" aria-label="Solved puzzle grid">
            <div className="solution-label">Solution Grid:</div>
            {renderGridTable(result.solution)}
          </div>
        )}

        {/* Solver output message */}
        <div className="message-box" aria-label="Solver output">
          <div className="message-label">Solver Output:</div>
          <div className="message-content">
            {result.message || '(no message)'}
          </div>
        </div>
      </div>
    );
  }

  // Don't render anything if no result and no errors
  return null;
}

