import { useState } from 'react';
import { solve, createSession, stepSession, deleteSession } from '../services/api';
import type { SolveResponse, Grid, StepInfo, ChangeRecord } from '../types/api';
import ResultPanel from './ResultPanel';
import SolutionGrid from './SolutionGrid';
import EditableGrid from './EditableGrid';
import {
  containerStyle,
  formGroupStyle,
  labelStyle,
  radioGroupStyle,
  getRadioLabelStyle,
  getRadioInputStyle,
  sampleLoaderStyle,
  getSampleButtonStyle,
  getButtonStyle,
  newPuzzleButtonStyle,
} from './solveformCSS';

/**
 * SolveForm Component
 * 
 * Provides a form for users to input a sudoku puzzle and solve it.
 * Accepts puzzle as JSON grid or 81-character string (0-9).
 */

type Mode = 'edit' | 'result';
type SolveMode = 'full' | 'step';

// Sample puzzles for testing
const SAMPLE_PUZZLES: Record<string, Grid> = {
  easy: [[5, 0, 0, 4, 3, 0, 1, 0, 0],[0, 0, 3, 1, 5, 0, 0, 4, 8],[1, 0, 0, 0, 2, 0, 0, 7, 0],[7, 0, 0, 6, 0, 0, 5, 1, 0],[0, 4, 0, 0, 0, 5, 7, 2, 9],[0, 5, 1, 9, 0, 4, 0, 0, 0],[6, 2, 0, 7, 0, 8, 0, 0, 1],[3, 9, 8, 0, 0, 0, 0, 0, 7],[0, 0, 7, 5, 0, 0, 9, 0, 2]],
  medium: [[0, 5, 0, 0, 4, 9, 3, 0, 0],[0, 0, 0, 0, 0, 0, 0, 7, 0],[0, 0, 0, 0, 1, 0, 6, 0, 0],[0, 0, 9, 0, 0, 0, 5, 0, 8],[0, 0, 3, 0, 9, 1, 0, 0, 0],[2, 0, 0, 0, 8, 5, 0, 0, 0],[0, 4, 0, 0, 5, 2, 0, 0, 0],[0, 0, 1, 6, 0, 0, 0, 4, 0],[6, 0, 0, 0, 0, 0, 0, 2, 0]],
  hard:   [[0, 7, 6, 2, 0, 0, 0, 5, 0],[0, 0, 0, 8, 7, 0, 3, 0, 0],[3, 0, 0, 0, 0, 1, 0, 0, 0],[1, 0, 0, 0, 0, 0, 6, 0, 0],[0, 0, 4, 0, 0, 0, 0, 3, 9],[5, 0, 0, 0, 4, 0, 0, 2, 0],[0, 0, 0, 0, 2, 0, 0, 0, 0],[0, 0, 2, 9, 0, 0, 0, 4, 7],[0, 9, 0, 0, 8, 0, 0, 0, 0]]
  // hard: [[0, 0, 0, 9, 3, 0, 4, 0, 0],[0, 4, 0, 0, 5, 0, 8, 0, 0],[5, 0, 0, 0, 0, 0, 0, 9, 6],[0, 0, 0, 4, 0, 1, 0, 6, 0],[0, 2, 0, 0, 0, 0, 0, 0, 8],[0, 0, 8, 0, 0, 6, 0, 0, 0],[0, 3, 0, 0, 2, 0, 0, 1, 0],[0, 0, 2, 0, 0, 0, 9, 7, 0],[0, 1, 0, 0, 0, 0, 0, 0, 0]],
};

// Empty grid for initialization and clear button
const EMPTY_GRID: Grid = Array.from({ length: 9 }, () => Array(9).fill(0));

/**
 * Format a change record into a human-readable string
 */
function formatChangeRecord(change: ChangeRecord): string {
  const parts: string[] = [];
  
  if (change.cells_filled.length > 0) {
    const filledStr = change.cells_filled
      .map(cf => `${cf.value} at (${cf.row},${cf.col})`)
      .join(', ');
    parts.push(`Filled ${change.cells_filled.length} cell(s): ${filledStr}`);
  }
  
  if (change.candidates_pruned.length > 0) {
    const prunedList = change.candidates_pruned.slice(0, 10);
    const prunedStr = prunedList
      .map(cp => `${cp.value} from (${cp.row},${cp.col})`)
      .join(', ');
    const moreText = change.candidates_pruned.length > 10 
      ? ` and ${change.candidates_pruned.length - 10} more`
      : '';
    parts.push(`Pruned ${change.candidates_pruned.length} candidate(s): ${prunedStr}${moreText}`);
  }
  
  if (parts.length === 0) {
    return 'No changes made.';
  }
  
  return parts.join('. ');
}

function formatStepStatusMessage(
  stepState: "solving" | "solved" | "stuck",
  stepChangeRecord: ChangeRecord | null,
  hasStepsBeenTaken: boolean
): string {
  if (!hasStepsBeenTaken) {
    return "Solving Status: Not started\nClick 'Next Step' to begin.";
  }
  
  if (stepState === "stuck") {
    return "Solving Status: Stuck\nPuzzle may be unsolvable.";
  }
  
  if (stepState === "solved") {
    if (stepChangeRecord) {
      const cellsFilled = stepChangeRecord.cells_filled.length;
      const candidatesPruned = stepChangeRecord.candidates_pruned.length;
      return `Solving Status: Solved\nRan ${stepChangeRecord.technique} rule: ${cellsFilled} cells filled, ${candidatesPruned} candidates pruned`;
    }
    return "Solving Status: Solved";
  }
  
  // stepState === "solving"
  if (stepChangeRecord) {
    const cellsFilled = stepChangeRecord.cells_filled.length;
    const candidatesPruned = stepChangeRecord.candidates_pruned.length;
    if (cellsFilled === 0 && candidatesPruned === 0) {
      return `Solving Status: In Progress\nRan ${stepChangeRecord.technique} rule: attempted but nothing found.`;
    }
    return `Solving Status: In Progress\nRan ${stepChangeRecord.technique} rule: ${cellsFilled} cells filled, ${candidatesPruned} candidates pruned`;
  }
  return "Solving Status: In Progress";
}

export default function SolveForm() {
  const [grid, setGrid] = useState<Grid>(EMPTY_GRID);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [originalGrid, setOriginalGrid] = useState<Grid | null>(null);
  const [mode, setMode] = useState<Mode>('edit');
  const [solveMode, setSolveMode] = useState<SolveMode>('full');
  
  // Step session state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [stepInfo, setStepInfo] = useState<StepInfo | null>(null);
  const [stepDone, setStepDone] = useState<boolean>(false);
  const [stepState, setStepState] = useState<"solving" | "stuck" | "solved">("solving");
  const [stepCandidates, setStepCandidates] = useState<number[][][] | null>(null);
  const [stepChangeRecord, setStepChangeRecord] = useState<ChangeRecord | null>(null);
  
  // Toggle state for showing original puzzle
  const [showOriginal, setShowOriginal] = useState<boolean>(false);

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

    // Check solve mode
    if (solveMode === 'step') {
      setLoading(true);
      setResult(null);
      setOriginalGrid(grid.map(row => [...row])); // Deep copy for step mode
      setStepInfo(null);
      setStepDone(false);
      setStepState("solving"); // Initialize state to "solving"
      setStepCandidates(null);
      setStepChangeRecord(null);
      setShowOriginal(false); // Reset toggle to default

      try {
        const session = await createSession(grid);
        setSessionId(session.session_id);
        // Store initial candidates if provided
        if (session.candidates) {
          setStepCandidates(session.candidates);
        }
        // Go to result view for step mode
        setMode('result');
      } catch (err) {
        setNetworkError(err instanceof Error ? err.message : 'Failed to start step session');
        setSessionId(null);
        setMode('result');
      } finally {
        setLoading(false);
      }
      return;
    }

    // Full solve mode
    setLoading(true);

    try {
      // Store the original grid for display
      setOriginalGrid(grid.map(row => [...row])); // Deep copy
      setShowOriginal(false); // Reset toggle to default
      
      // Call API with structured grid
      const response = await solve({ grid });
      
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

  const handleNextStep = async () => {
    if (!sessionId) return;
    setLoading(true);
    setValidationError(null);
    setNetworkError(null);

    try {
      const response = await stepSession(sessionId);
      // Update the grid with the latest state from backend
      if (response.solution) {
        setGrid(response.solution);
      }
      // Update step info - use changes if available, otherwise use message
      let stepMessage = response.message || 'Step completed';
      if (response.changes && response.changes.length > 0) {
        // Format the change record(s) for display
        const formattedChanges = response.changes.map(change => {
          return `${change.technique}: ${formatChangeRecord(change)}`;
        }).join('\n');
        stepMessage = formattedChanges;
      }
      setStepInfo({
        rule: stepMessage,
        row: null,
        col: null,
        value: null,
      });
      // Update state from response
      setStepState(response.state || "solving");
      setStepDone(response.state === "solved");
      setStepCandidates(response.candidates ?? null);
      // Store the latest change record
      if (response.changes && response.changes.length > 0) {
        setStepChangeRecord(response.changes[0]); // Store first (and only) change record
      } else {
        setStepChangeRecord(null);
      }
      // If Show Original is ON, switch it OFF when taking a step
      if (showOriginal) {
        setShowOriginal(false);
      }
    } catch (err) {
      setNetworkError(err instanceof Error ? err.message : 'Failed to apply next step');
      setStepInfo(null);
    } finally {
      setLoading(false);
    }
  };

  const handleEndSession = async () => {
    if (sessionId) {
      try {
        await deleteSession(sessionId);
      } catch {
        // Ignore errors on delete; we are resetting state anyway
      }
    }
    // Reuse existing new-puzzle behavior for full reset (already clears session state)
    handleNewPuzzle();
  };

  const handleNewPuzzle = () => {
    setGrid(EMPTY_GRID);
    setResult(null);
    setValidationError(null);
    setNetworkError(null);
    setOriginalGrid(null);
    setLoading(false);
    setMode('edit');
    setSolveMode('full'); // reset to Full Solve
    setSessionId(null);
    setStepInfo(null);
    setStepDone(false);
    setStepState("solving"); // Reset state to "solving"
    setStepCandidates(null);
    setStepChangeRecord(null);
    setShowOriginal(false); // Reset toggle to default
    
    // Focus first cell after state updates
    requestAnimationFrame(() => {
      const el = document.querySelector<HTMLInputElement>('[aria-label="r1 c1 entry"]');
      el?.focus();
    });
  };


  return (
    <div style={containerStyle}>
      {/* EDIT MODE: Show input form with grid, sample buttons, and solve button */}
      {mode === 'edit' && (
        <form onSubmit={handleSubmit}>
          <div style={formGroupStyle}>
            <label style={labelStyle}>
              Enter Puzzle below or load an example
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
                style={getSampleButtonStyle(loading)}
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
                style={getSampleButtonStyle(loading)}
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
                style={getSampleButtonStyle(loading)}
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
                style={getSampleButtonStyle(loading)}
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
              Solve Mode
            </label>
            <div style={radioGroupStyle}>
              <label style={getRadioLabelStyle(loading)}>
                <input
                  type="radio"
                  name="solveMode"
                  value="full"
                  checked={solveMode === 'full'}
                  onChange={() => setSolveMode('full')}
                  disabled={loading}
                  style={getRadioInputStyle(loading)}
                />
                <span>Full Solve</span>
              </label>
              <label style={getRadioLabelStyle(loading)}>
                <input
                  type="radio"
                  name="solveMode"
                  value="step"
                  checked={solveMode === 'step'}
                  onChange={() => setSolveMode('step')}
                  disabled={loading}
                  style={getRadioInputStyle(loading)}
                />
                <span>Step Solve</span>
              </label>
            </div>
          </div>

          <button
            type="submit"
            style={getButtonStyle(loading)}
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

      {/* RESULT MODE: Show result panel based on solve mode */}
      {mode === 'result' && solveMode === 'full' && (
        <>
          <ResultPanel 
            result={result} 
            validationError={validationError}
            networkError={networkError}
            originalGrid={originalGrid}
            showOriginal={showOriginal}
            onToggleShowOriginal={() => setShowOriginal(!showOriginal)}
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

      {mode === 'result' && solveMode === 'step' && (
        <>
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <label style={labelStyle}>
                {showOriginal ? 'Original Puzzle' : 'Solving Puzzle (Step Solve Mode)'}
              </label>
              <button
                type="button"
                onClick={() => setShowOriginal(!showOriginal)}
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
            </div>
            {(() => {
              const displayGrid =
                showOriginal && originalGrid ? originalGrid : grid;
              const isValidGrid = displayGrid && displayGrid.length === 9;

              if (!isValidGrid) {
                return <div style={{ color: '#b00020' }}>Error: Invalid grid state</div>;
              }

              if (showOriginal) {
                return (
                  <EditableGrid
                    value={displayGrid}
                    onChange={() => {}}
                    disabled={true}
                  />
                );
              }

              return (
                <SolutionGrid
                  grid={displayGrid}
                  showCandidates={true}
                  candidates={stepCandidates ?? null}
                />
              );
            })()}
          </div>

          <div className="message-box" aria-label="Step status" style={{ marginBottom: '16px' }}>
            <div className="message-content">
              {(() => {
                const statusMessage = formatStepStatusMessage(stepState, stepChangeRecord, stepInfo !== null);
                const messageLines = statusMessage.split('\n');
                return (
                  <>
                    <strong>{messageLines[0]}</strong>
                    {messageLines.slice(1).map((line, idx) => (
                      <div key={idx}>{line}</div>
                    ))}
                    {networkError && (
                      <div style={{ color: '#b00020', marginTop: '8px' }}>
                        {networkError}
                      </div>
                    )}
                    {validationError && (
                      <div style={{ color: '#b00020', marginTop: '8px' }}>
                        {validationError}
                      </div>
                    )}
                  </>
                );
              })()}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
            {stepState !== 'stuck' && stepState !== 'solved' && (
              <button
                type="button"
                style={{ ...getButtonStyle(loading), width: '50%' }}
                disabled={loading || !sessionId || stepDone}
                onClick={handleNextStep}
                onMouseOver={(e) => {
                  if (!loading && !stepDone) {
                    e.currentTarget.style.backgroundColor = '#0056b3';
                  }
                }}
                onMouseOut={(e) => {
                  if (!loading && !stepDone) {
                    e.currentTarget.style.backgroundColor = '#007bff';
                  }
                }}
              >
                {loading ? 'Stepping...' : 'Next Step'}
              </button>
            )}

            <button
              type="button"
              style={{ ...newPuzzleButtonStyle, width: stepState === 'stuck' || stepState === 'solved' ? '100%' : '50%' }}
              onClick={handleEndSession}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#218838';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#28a745';
              }}
            >
              End Session / New Puzzle
            </button>
          </div>
        </>
      )}
    </div>
  );
}

