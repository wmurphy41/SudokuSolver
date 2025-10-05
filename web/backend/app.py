"""
FastAPI backend application for SudokuSolver web interface.

This module provides REST API endpoints for the SudokuSolver web application.
It includes health check and placeholder solve endpoints.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

# Initialize FastAPI application
app = FastAPI(
    title="SudokuSolver API",
    description="Backend API for SudokuSolver web application",
    version="1.0.0"
)

# Pydantic model for solve request payload
class SolveRequest(BaseModel):
    """Model for sudoku solve requests."""
    puzzle: str  # Will contain the sudoku puzzle data
    difficulty: str = "easy"  # Optional difficulty level

class SolveResponse(BaseModel):
    """Model for sudoku solve responses."""
    solution: str
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
    
    Currently echoes the payload for testing purposes.
    Will be integrated with the actual SudokuSolver logic later.
    
    Args:
        request: SolveRequest containing puzzle data
        
    Returns:
        SolveResponse with solution data
    """
    # TODO: Integrate with actual SudokuSolver backend
    return SolveResponse(
        solution=request.puzzle,  # Echo the puzzle for now
        success=True,
        message=f"Echoed puzzle with difficulty: {request.difficulty}"
    )

if __name__ == "__main__":
    import uvicorn
    # Run the application on port 8000 for Docker container
    uvicorn.run(app, host="0.0.0.0", port=8000)
