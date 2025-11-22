"""
FastAPI backend application for SudokuSolver web interface.

This module provides REST API endpoints for the SudokuSolver web application.
It includes health check and solve endpoints integrated with the SudokuSolver engine.
"""

import io
import json
import os
import sys
import uuid
from contextlib import redirect_stdout
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional
import redis

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

# Import step solver (stub for now)
from step_solver import apply_one_step

# Initialize FastAPI application
app = FastAPI(
    title="SudokuSolver API",
    description="Backend API for SudokuSolver web application",
    version="1.0.0"
)

# Type aliases for 9x9 Sudoku grid
Row = List[int]
Grid = List[Row]

# Redis client configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def get_redis() -> redis.Redis:
    """Get a Redis client instance."""
    return redis.from_url(REDIS_URL, decode_responses=True)

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

# Session models for step-wise solving
class StepSessionCreate(BaseModel):
    """Model for creating a step-wise solving session."""
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

class StepInfo(BaseModel):
    """Model for step information."""
    rule: Optional[str] = None
    row: Optional[int] = None
    col: Optional[int] = None
    value: Optional[int] = None

class StepResponse(BaseModel):
    """Model for step response."""
    grid: Grid
    step: StepInfo
    done: bool


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

# Session endpoints for step-wise solving
@app.post("/api/sessions")
async def create_session(payload: StepSessionCreate) -> Dict[str, str]:
    """
    Create a new step-wise solving session.
    
    Args:
        payload: StepSessionCreate containing 9x9 grid and debug level
        
    Returns:
        Dict containing session_id
    """
    r = get_redis()
    session_id = uuid.uuid4().hex
    data = {
        "grid": payload.grid,
        "debug_level": payload.debug_level,
    }
    r.set(f"sudoku:session:{session_id}", json.dumps(data))
    return {"session_id": session_id}

@app.post("/api/sessions/{session_id}/step", response_model=StepResponse)
async def step_session(session_id: str) -> StepResponse:
    """
    Apply one step to a solving session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        StepResponse with updated grid, step info, and done status
    """
    r = get_redis()
    raw = r.get(f"sudoku:session:{session_id}")
    if raw is None:
        raise HTTPException(status_code=404, detail="Session not found")

    data = json.loads(raw)
    grid: Grid = data["grid"]

    # Apply a single step (stubbed for now)
    new_grid, step_info_dict, done = apply_one_step(grid)

    # Persist updated grid if not done
    data["grid"] = new_grid
    r.set(f"sudoku:session:{session_id}", json.dumps(data))

    step_info = StepInfo(**step_info_dict)
    return StepResponse(grid=new_grid, step=step_info, done=done)

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, bool]:
    """
    Delete a solving session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dict indicating whether the session was deleted
    """
    r = get_redis()
    key = f"sudoku:session:{session_id}"
    exists = r.delete(key)
    return {"deleted": bool(exists)}

if __name__ == "__main__":
    import uvicorn
    # Run the application on port 8000 for Docker container
    uvicorn.run(app, host="0.0.0.0", port=8000)
