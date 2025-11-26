"""
Step-wise Sudoku solver (stub implementation).

This module provides a minimal stub for step-wise solving.
The stub fills the first empty cell with 1 and marks done when no zeros remain.
"""

from typing import List, Tuple, Dict, Any

Grid = List[List[int]]


def apply_one_step(grid: Grid) -> Tuple[Grid, Dict[str, Any], bool]:
    """
    TEMPORARY stub for step-wise solving.
    - Finds the first cell with 0 and sets it to 1.
    - If no zeros remain, marks done = True.
    
    Returns:
        new_grid: updated grid after the step
        step_info: dict with keys rule, row, col, value
        done: True if there are no more zeros in the grid
    """
    new_grid = [row[:] for row in grid]
    step_info: Dict[str, Any] = {"rule": None, "row": None, "col": None, "value": None}

    for r in range(9):
        for c in range(9):
            if new_grid[r][c] == 0:
                new_grid[r][c] = 1
                step_info = {"rule": "stub-fill-1", "row": r, "col": c, "value": 1}
                return new_grid, step_info, False

    # No zeros: we're done
    return new_grid, step_info, True

