import type { SolveResponse } from '../types/api';

/**
 * ResultPanel Component
 * 
 * Displays the results of a sudoku solve request.
 * Shows success/fail status, solution, and detailed message.
 */

interface ResultPanelProps {
  result: SolveResponse | null;
  error?: string | null;
}

export default function ResultPanel({ result, error }: ResultPanelProps) {
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

        {/* Solution box */}
        <div className="solution-box" aria-label="Solved puzzle">
          <div className="solution-label">Solution:</div>
          <div className="solution-content">
            {result.solution || '(no solution returned)'}
          </div>
        </div>

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

