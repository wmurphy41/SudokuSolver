"""
Step-wise Sudoku solver using the real SudokuSolver engine.

This module provides step-wise solving by integrating with the SudokuSolver class.
Each step runs one pass of all solving techniques using step_solve().
"""

import io
from contextlib import redirect_stdout
from typing import List, Tuple, Optional, Dict, Any
import sys

# Import SudokuSolver - use the same import path as app.py
try:
    from src.sudoku_solver import SudokuSolver
except ImportError:
    # Try alternative import for Docker container
    try:
        sys.path.insert(0, '/app')
        from src.sudoku_solver import SudokuSolver
    except ImportError:
        # Fallback for development
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        from src.sudoku_solver import SudokuSolver

Grid = List[List[int]]


def apply_one_step(grid: Grid, debug_level: int = 0, solver_state: Optional[Dict[str, Any]] = None) -> Tuple[Grid, bool, str, Dict[str, Any]]:
    """
    Apply a single logical solving step using SudokuSolver.
    
    Logic:
    - If solver_state is provided, restore solver from that state.
    - Otherwise, create a SudokuSolver from the grid using the given debug level.
    - Redirect stdout to a buffer while running step_solve().
    - If the buffer contains any text, use that as the message.
    - Otherwise, if step_solve returned True, message = "Solved".
      If it returned False, message = "In Progress".
    
    Args:
        grid: 9x9 grid of integers (used only if solver_state is None)
        debug_level: Debug output level (used only if solver_state is None)
        solver_state: Optional serialized solver state to restore from
    
    Returns:
        new_grid: updated 9x9 grid of integers
        success: flag returned from step_solve() (True if puzzle solved)
        message: log or status message
        solver_state: updated serialized solver state
    """
    buf = io.StringIO()
    success = False

    with redirect_stdout(buf):
        # Restore from state if provided, otherwise create new solver
        if solver_state is not None:
            solver = SudokuSolver.from_dict(solver_state)
        else:
            solver = SudokuSolver(grid, debug_level=debug_level)
        
        success = solver.step_solve()

    # Capture logs from stdout
    logs = buf.getvalue()
    logs_stripped = logs.strip()

    if logs_stripped:
        message = logs
    else:
        message = "Solved" if success else "In Progress"

    # Extract updated grid from solver
    new_grid: Grid = []
    for row in solver.grid:
        int_row: List[int] = []
        for cell in row:
            value = getattr(cell, "value", 0)
            int_row.append(int(value) if isinstance(value, int) else 0)
        new_grid.append(int_row)

    # Extract full solver state for persistence
    updated_solver_state = solver.to_dict()

    return new_grid, success, message, updated_solver_state

