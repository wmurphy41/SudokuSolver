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
from typing import Dict, List, Optional, Any
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
CandidateGrid = List[List[List[int]]]

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
    candidates: Optional[CandidateGrid] = None
    changes: Optional[List[Dict[str, Any]]] = None  # List of all change records

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
    """Model for step-wise solve responses (same shape as SolveResponse)."""
    solution: Optional[Grid]
    success: bool
    message: str
    state: str  # "solving", "solved", or "stuck"
    candidates: Optional[CandidateGrid] = None  # Candidate lists for each cell
    changes: Optional[List[Dict[str, Any]]] = None  # List with single change record for this step


def _format_changes(changes: List[Dict[str, Any]]) -> str:
    """
    Format a list of change records into a human-readable message.
    
    Args:
        changes: List of change records, each with technique, cells_filled, candidates_pruned
    
    Returns:
        Formatted string describing the changes
    """
    if not changes:
        return "No changes made."
    
    parts = []
    for change in changes:
        technique = change.get("technique", "Unknown technique")
        cells_filled = change.get("cells_filled", [])
        candidates_pruned = change.get("candidates_pruned", [])
        
        change_desc = f"{technique}: "
        if cells_filled:
            filled_list = [f"{cf['value']} at ({cf['row']},{cf['col']})" for cf in cells_filled]
            filled_str = ", ".join(filled_list)
            change_desc += f"Filled {len(cells_filled)} cell(s) ({filled_str}). "
        if candidates_pruned:
            pruned_list = [f"{cp['value']} from ({cp['row']},{cp['col']})" for cp in candidates_pruned[:10]]
            pruned_str = ", ".join(pruned_list)
            if len(candidates_pruned) > 10:
                pruned_str += f" and {len(candidates_pruned) - 10} more"
            change_desc += f"Pruned {len(candidates_pruned)} candidate(s) ({pruned_str})."
        if not cells_filled and not candidates_pruned:
            change_desc += "No changes."
        
        parts.append(change_desc)
    
    return "\n".join(parts)

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
    
    candidate_grid: Optional[CandidateGrid] = None

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
        
        # Serialize candidate lists
        try:
            candidate_grid = solver.get_candidate_grid()
        except Exception:
            candidate_grid = None
        
        # Get captured output
        message = log_buf.getvalue() or ""
        
        # Get change history from solver
        change_history = []
        try:
            change_history = solver.get_change_history()
        except Exception:
            change_history = []
        
        # Append formatted changes to message if available
        if change_history:
            formatted_changes = _format_changes(change_history)
            if message:
                message = message + "\n\n" + formatted_changes
            else:
                message = formatted_changes
        
        return SolveResponse(
            solution=solution_grid,  # Return grid even on failure to show progress
            success=bool(ok),
            message=message if message else ("Solved" if ok else "Unsolved or invalid"),
            candidates=candidate_grid,
            changes=change_history if change_history else None,
        )
        
    except Exception as e:
        # Include any partial logs plus the error
        message = (log_buf.getvalue() or "") + f"\nERROR: {e}"
        return SolveResponse(
            solution=None, 
            success=False, 
            message=message.strip(),
            candidates=None,
        )

# Session endpoints for step-wise solving
@app.post("/api/sessions")
async def create_session(payload: StepSessionCreate) -> Dict[str, Any]:
    """
    Create a new step-wise solving session.
    
    Args:
        payload: StepSessionCreate containing 9x9 grid and debug level
        
    Returns:
        Dict containing session_id and initial candidates
    """
    try:
        r = get_redis()
        # Test connection before proceeding
        r.ping()
    except redis.ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Redis connection failed: {str(e)}. Please ensure Redis is running."
        )
    except redis.TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail=f"Redis connection timeout: {str(e)}. Redis may be slow or unreachable."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Redis: {type(e).__name__}: {str(e)}"
        )
    
    try:
        session_id = uuid.uuid4().hex
        
        # Create initial solver to get state with candidates initialized
        solver = SudokuSolver(payload.grid, debug_level=payload.debug_level)
        solver_state = solver.to_dict()
        initial_candidates = solver.get_candidate_grid()
        
        data = {
            "grid": payload.grid,
            "debug_level": payload.debug_level,
            "solver_state": solver_state,
            "state": "solving",  # Initial state is "solving"
        }
        r.set(f"sudoku:session:{session_id}", json.dumps(data))
        return {
            "session_id": session_id,
            "candidates": initial_candidates
        }
    except redis.RedisError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Redis operation failed: {str(e)}"
        )
    except json.JSONEncodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to serialize session data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {type(e).__name__}: {str(e)}"
        )

@app.post("/api/sessions/{session_id}/step", response_model=StepResponse)
async def step_session(session_id: str) -> StepResponse:
    """
    Apply a single solving step to a session's grid.
    
    Args:
        session_id: Session identifier
        
    Returns:
        StepResponse with updated grid, success flag, and message
    """
    r = get_redis()
    raw = r.get(f"sudoku:session:{session_id}")
    if raw is None:
        raise HTTPException(status_code=404, detail="Session not found")

    data = json.loads(raw)
    grid: Grid = data["grid"]
    debug_level: int = int(data.get("debug_level", 0))
    solver_state = data.get("solver_state")  # May be None for old sessions

    # apply_one_step signature: (grid, state, message, solver_state, candidates, change_record)
    # Pass solver_state if available, otherwise use grid (backward compatible)
    new_grid, state, message, updated_solver_state, candidate_grid, change_record = apply_one_step(
        grid, debug_level, solver_state
    )

    # Persist updated grid, state, and solver state back into the session
    data["grid"] = new_grid
    data["state"] = state
    data["solver_state"] = updated_solver_state
    r.set(f"sudoku:session:{session_id}", json.dumps(data))

    # Determine success flag from state
    success = state == "solved"
    
    # Format change record into message if available
    if change_record and (change_record.get("cells_filled") or change_record.get("candidates_pruned")):
        formatted_change = _format_changes([change_record])
        if message:
            message = message + "\n\n" + formatted_change
        else:
            message = formatted_change

    # For step mode, always return the updated grid as the "solution"
    # Include change record as a list with single item
    changes_list = [change_record] if change_record and (change_record.get("cells_filled") or change_record.get("candidates_pruned")) else None
    
    return StepResponse(
        solution=new_grid,
        success=success,
        message=message,
        state=state,
        candidates=candidate_grid,
        changes=changes_list,
    )

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, bool]:
    """
    Delete a step-wise solving session.
    
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
