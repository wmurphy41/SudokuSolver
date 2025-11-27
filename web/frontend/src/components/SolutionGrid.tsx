import type { Grid, CandidateGrid } from '../types/api';

interface SolutionGridProps {
  grid: Grid;
  showCandidates?: boolean;
  candidates?: CandidateGrid | null;
}

function renderCandidateDigits(digits: number[]) {
  const padded = Array.from({ length: 9 }, (_, idx) => {
    const value = idx + 1;
    return digits.includes(value) ? value : '';
  });

  return (
    <div className="candidate-grid" aria-label="Cell candidates">
      {[0, 3, 6].map((start) => (
        <div className="candidate-row" key={start}>
          {padded.slice(start, start + 3).map((val, idx) => (
            <span className="candidate-cell" key={idx}>
              {val}
            </span>
          ))}
        </div>
      ))}
    </div>
  );
}

/**
 * Shared read-only grid used in result panels and step mode display.
 * Phase 1: empty cells render placeholder digits 1-9.
 * Phase 2: candidates prop will feed actual SudokuSolver candidate lists.
 */
export default function SolutionGrid({ grid, showCandidates = false, candidates }: SolutionGridProps) {
  return (
    <div className="grid-card">
      <table className="sudoku-grid solution-grid">
        <tbody>
          {grid.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, colIndex) => {
                const isEmpty = cell === 0;
                const candidateList =
                  candidates &&
                  candidates[rowIndex] &&
                  candidates[rowIndex][colIndex]
                    ? candidates[rowIndex][colIndex]
                    : [1, 2, 3, 4, 5, 6, 7, 8, 9];

                return (
                  <td
                    key={colIndex}
                    className={isEmpty ? 'empty-cell candidate-cell-wrapper' : 'filled-cell'}
                  >
                    {isEmpty
                      ? showCandidates
                        ? renderCandidateDigits(candidateList)
                        : ''
                      : cell}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

