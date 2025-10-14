import { useRef, KeyboardEvent, ClipboardEvent } from 'react';
import type { Grid } from '../types/api';

/**
 * EditableGrid Component
 * 
 * An editable 9×9 Sudoku grid with keyboard navigation and paste support.
 * Each cell is a single-digit input (0-9, where 0 = empty).
 */

interface EditableGridProps {
  value: Grid;                     // current 9x9 numbers (0 = empty)
  onChange: (next: Grid) => void;  // called on any edit
  disabled?: boolean;              // disable editing while solving
  className?: string;              // optional style hook
}

export default function EditableGrid({ value, onChange, disabled = false, className = 'editable-grid' }: EditableGridProps) {
  const inputRefs = useRef<(HTMLInputElement | null)[][]>(
    Array.from({ length: 9 }, () => Array(9).fill(null))
  );

  /**
   * Update a single cell value
   */
  const updateCell = (row: number, col: number, val: string) => {
    // Only accept digits 0-9 or empty
    if (val !== '' && !/^[0-9]$/.test(val)) {
      return;
    }

    const newGrid: Grid = value.map(r => [...r]);
    newGrid[row][col] = val === '' ? 0 : parseInt(val);
    onChange(newGrid);
  };

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>, row: number, col: number) => {
    let newRow = row;
    let newCol = col;

    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault();
        newRow = row > 0 ? row - 1 : row;
        break;
      case 'ArrowDown':
        e.preventDefault();
        newRow = row < 8 ? row + 1 : row;
        break;
      case 'ArrowLeft':
        e.preventDefault();
        newCol = col > 0 ? col - 1 : col;
        break;
      case 'ArrowRight':
        e.preventDefault();
        newCol = col < 8 ? col + 1 : col;
        break;
      case 'Backspace':
      case 'Delete':
        e.preventDefault();
        updateCell(row, col, '');
        return;
      case 'Tab':
        // Allow default tab behavior
        return;
      default:
        // If it's a digit, handle it and move right
        if (/^[0-9]$/.test(e.key)) {
          updateCell(row, col, e.key);
          e.preventDefault();
          // Advance to next cell
          if (col < 8) {
            newCol = col + 1;
          } else if (row < 8) {
            newRow = row + 1;
            newCol = 0;
          }
        }
        return;
    }

    // Focus the new cell
    inputRefs.current[newRow]?.[newCol]?.focus();
  };

  /**
   * Handle paste events - supports 81 digits or JSON array
   */
  const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedText = e.clipboardData.getData('text');

    // Try parsing as JSON first
    try {
      const parsed = JSON.parse(pastedText);
      if (Array.isArray(parsed) && parsed.length === 9 &&
          parsed.every(row => Array.isArray(row) && row.length === 9)) {
        onChange(parsed as Grid);
        return;
      }
    } catch {
      // Not JSON, try digit parsing
    }

    // Try parsing as 81 digits
    const digitsOnly = pastedText.replace(/[^0-9]/g, '');
    if (digitsOnly.length === 81) {
      const newGrid: Grid = [];
      for (let i = 0; i < 9; i++) {
        const row: number[] = [];
        for (let j = 0; j < 9; j++) {
          row.push(parseInt(digitsOnly[i * 9 + j]));
        }
        newGrid.push(row);
      }
      onChange(newGrid);
    }
  };

  /**
   * Prevent wheel/scroll from changing values
   */
  const handleWheel = (e: React.WheelEvent<HTMLInputElement>) => {
    e.currentTarget.blur();
  };

  return (
    <div className="grid-card">
      <table className={`sudoku-grid ${className}`}>
        <tbody>
          {value.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, colIndex) => (
                <td key={colIndex}>
                  <input
                    ref={el => {
                      if (!inputRefs.current[rowIndex]) {
                        inputRefs.current[rowIndex] = [];
                      }
                      inputRefs.current[rowIndex][colIndex] = el;
                    }}
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={1}
                    value={cell === 0 ? '' : cell}
                    onChange={(e) => updateCell(rowIndex, colIndex, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, rowIndex, colIndex)}
                    onPaste={handlePaste}
                    onWheel={handleWheel}
                    disabled={disabled}
                    className="cell-input"
                    aria-label={`r${rowIndex + 1} c${colIndex + 1} entry`}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

