import type { SolveResponse, Grid } from '../types/api';

/**
 * ResultPanel Component
 * 
 * Displays the results of a sudoku solve request.
 * Shows success/fail status, original puzzle grid, solution grid, and detailed message.
 */

interface ResultPanelProps {
  result: SolveResponse | null;
  error?: string | null;
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

export default function ResultPanel({ result, error, originalGrid }: ResultPanelProps) {
  // Don't render anything if no result and no error
  if (!result && !error) {
    return null;
  }

  // Handle error state
  if (error) {
    return (
      <div className="result-panel">
        {/* Status badge - error */}
        <div className="status-badge status-fail" role="status" aria-live="polite">
          Fail
        </div>

        {/* Error message box */}
        <div className="message-box" aria-label="Error message">
          {error}
        </div>
      </div>
    );
  }

  // Handle successful result
  if (result) {
    return (
      <div className="result-panel">
        {/* Status badge - success or fail based on result.success */}
        <div 
          className={`status-badge ${result.success ? 'status-success' : 'status-fail'}`}
          role="status"
          aria-live="polite"
        >
          {result.success ? 'Success' : 'Fail'}
        </div>

        {/* Original puzzle grid - only show on success */}
        {result.success && originalGrid && (
          <div className="solution-grid-container" aria-label="Original puzzle grid">
            <div className="solution-label">Original Puzzle:</div>
            {renderGridTable(originalGrid)}
          </div>
        )}

        {/* Solution grid table view - visual representation */}
        {result.solution && (
          <div className="solution-grid-container" aria-label="Solved puzzle grid">
            <div className="solution-label">Solution Grid:</div>
            {renderGridTable(result.solution)}
          </div>
        )}

        {/* Message box - scrollable for long messages */}
        <div className="message-box" aria-label="Solver message">
          <div className="message-label">Message:</div>
          <div className="message-content">
            {result.message || '(no message)'}
          </div>
        </div>
      </div>
    );
  }

  return null;
}

