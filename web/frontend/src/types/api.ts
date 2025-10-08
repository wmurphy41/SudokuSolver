/**
 * API Types for SudokuSolver Backend
 * 
 * These types define the shape of requests and responses for the FastAPI backend.
 * 
 * Future Evolution:
 * - Puzzle format may evolve from string to number[][] (9x9 grid)
 * - Session endpoints for saving/loading puzzles may be added
 * - User authentication and puzzle history tracking
 * - OCR result types for image-based puzzle input
 */

/**
 * Request payload for solving a sudoku puzzle
 * 
 * @property puzzle - Currently an 81-character string or JSON-ish string
 *                    May evolve to number[][] (9x9 grid) in the future
 */
export interface SolveRequest {
  puzzle: string;  // 81-char string or JSON-ish string for now
}

/**
 * Response from the solve endpoint
 * 
 * @property solution - Solved puzzle in same format as input
 * @property success - Whether the puzzle was solved successfully
 * @property message - Human-readable status or error message
 */
export interface SolveResponse {
  solution: string;
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

