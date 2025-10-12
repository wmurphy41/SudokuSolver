/**
 * API Types for SudokuSolver Backend
 * 
 * These types define the shape of requests and responses for the FastAPI backend.
 * 
 * Future Evolution:
 * - Session endpoints for saving/loading puzzles may be added
 * - User authentication and puzzle history tracking
 * - OCR result types for image-based puzzle input
 */

/**
 * 9x9 Sudoku grid
 * Each cell contains 0 (empty) or 1-9 (filled digit)
 */
export type Grid = number[][];

/**
 * Request payload for solving a sudoku puzzle
 * 
 * @property grid - 9x9 grid of integers (0 = empty, 1-9 = filled)
 * @property debug_level - Optional debug level for solver (default: 0)
 */
export interface SolveRequest {
  grid: Grid;
  debug_level?: number;
}

/**
 * Response from the solve endpoint
 * 
 * @property solution - Solved puzzle as 9x9 grid, or null if unsolved
 * @property success - Whether the puzzle was solved successfully
 * @property message - Human-readable status or error message
 */
export interface SolveResponse {
  solution: Grid | null;
  success: boolean;
  message: string;
}

/**
 * Health check response
 * 
 * @property status - Always 'ok' when service is healthy
 */
export interface Healthz {
  status: 'ok';
}

