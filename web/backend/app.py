"""
FastAPI backend application for SudokuSolver web interface.

This module provides REST API endpoints for the SudokuSolver web application.
It includes health check and solve endpoints integrated with the SudokuSolver engine.
"""

import io
import sys
from contextlib import redirect_stdout
from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional

# Import the SudokuSolver engine
# NOTE: If running in Docker, PYTHONPATH may need to be set to /app
# or the solver code needs to be copied into the container
try:
    from src.sudoku_solver import SudokuSolver
except ImportError:
    # Try alternative import for Docker container
    try:
        import sys
        sys.path.insert(0, '/app')
        from src.sudoku_solver import SudokuSolver
    except ImportError:
        # Fallback for development
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        from src.sudoku_solver import SudokuSolver

# Initialize FastAPI application
app = FastAPI(
    title="SudokuSolver API",
    description="Backend API for SudokuSolver web application",
    version="1.0.0"
)

# Type aliases for 9x9 Sudoku grid
Row = List[int]
Grid = List[Row]

class SolveRequest(BaseModel):
    """Model for sudoku solve requests with structured 9x9 grid."""
    grid: Grid
    debug_level: int = 0

    @field_validator('grid')
    @classmethod
    def validate_grid_size(cls, grid: Grid) -> Grid:
        """Validate grid is exactly 9x9."""
        if len(grid) != 9:
            raise ValueError("grid must have exactly 9 rows")
        for i, row in enumerate(grid):
            if len(row) != 9:
                raise ValueError(f"row {i} must have exactly 9 columns")
        return grid

    @field_validator('grid')
    @classmethod
    def validate_digits(cls, grid: Grid) -> Grid:
        """Validate all grid values are integers 0-9."""
        for i, row in enumerate(grid):
            for j, val in enumerate(row):
                if not isinstance(val, int) or not (0 <= val <= 9):
                    raise ValueError(f"grid[{i}][{j}] must be an integer 0..9, got {val}")
        return grid

class SolveResponse(BaseModel):
    """Model for sudoku solve responses with structured 9x9 grid."""
    solution: Optional[Grid]  # None if invalid/unsolved
    success: bool
    message: str


def _to_int_grid(solver: SudokuSolver) -> Grid:
    """
    Extract the current grid from SudokuSolver as a 9x9 integer grid.
    
    Args:
        solver: SudokuSolver instance
        
    Returns:
        9x9 grid of integers
    """
    grid: Grid = []
    for row in solver.grid:
        int_row: List[int] = []
        for cell in row:
            # Extract the value from the cell (assuming cell has a value attribute)
            int_row.append(int(cell.value) if hasattr(cell, 'value') else 0)
        grid.append(int_row)
    return grid


@app.get("/api/healthz")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and load balancer health checks.
    
    Returns:
        Dict containing status information
    """
    return {"status": "ok"}

@app.post("/api/solve", response_model=SolveResponse)
async def solve_sudoku(request: SolveRequest) -> SolveResponse:
    """
    Solve a sudoku puzzle using the SudokuSolver engine.
    
    Captures all solver output (prints) and returns the solution grid,
    success status, and aggregated log messages.
    
    Args:
        request: SolveRequest containing 9x9 grid and debug level
        
    Returns:
        SolveResponse with solution grid, success status, and captured logs
    """
    log_buf = io.StringIO()
    
    try:
        # Capture all stdout from solver initialization and solving
        with redirect_stdout(log_buf):
            solver = SudokuSolver(request.grid, debug_level=request.debug_level)
            ok = solver.solve()
        
        # Attempt to extract final grid whether ok or not
        # On failure, this shows the partial progress made by the solver
        solution_grid = None
        try:
            solution_grid = _to_int_grid(solver)
        except Exception:
            solution_grid = None
        
        # Get captured output
        message = log_buf.getvalue() or ""
        
        return SolveResponse(
            solution=solution_grid,  # Return grid even on failure to show progress
            success=bool(ok),
            message=message if message else ("Solved" if ok else "Unsolved or invalid")
        )
        
    except Exception as e:
        # Include any partial logs plus the error
        message = (log_buf.getvalue() or "") + f"\nERROR: {e}"
        return SolveResponse(
            solution=None, 
            success=False, 
            message=message.strip()
        )

if __name__ == "__main__":
    import uvicorn
    # Run the application on port 8000 for Docker container
    uvicorn.run(app, host="0.0.0.0", port=8000)
