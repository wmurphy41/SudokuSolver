"""
FastAPI backend application for SudokuSolver web interface.

This module provides REST API endpoints for the SudokuSolver web application.
It includes health check and placeholder solve endpoints.
"""

from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional

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
    Placeholder endpoint for solving sudoku puzzles.
    
    Currently echoes the grid for testing purposes.
    Will be integrated with the actual SudokuSolver logic later.
    
    Args:
        request: SolveRequest containing 9x9 grid and debug level
        
    Returns:
        SolveResponse with solution grid
    """
    # TODO: Integrate with actual SudokuSolver backend
    # For now, echo the grid back to verify end-to-end types
    return SolveResponse(
        solution=request.grid,  # Echo the grid for now
        success=True,
        message=f"OK (echo for grid wire-up, debug_level={request.debug_level})"
    )

if __name__ == "__main__":
    import uvicorn
    # Run the application on port 8000 for Docker container
    uvicorn.run(app, host="0.0.0.0", port=8000)
