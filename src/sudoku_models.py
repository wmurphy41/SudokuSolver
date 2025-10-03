"""
Sudoku Models

Data models, enums, and exceptions for the Sudoku solver.

This module contains:
- Difficulty enumeration
- SolvingMetrics dataclass
- SudokuError exception
- SudokuCell class
- SudokuPuzzle class

Author: Improved version with better Python practices
"""

from typing import Set, List
from dataclasses import dataclass
from enum import Enum
import json
import os


class Difficulty(Enum):
    """Enumeration for puzzle difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


@dataclass
class SolvingMetrics:
    """Metrics tracking for solving performance."""
    fill_only_candidate: int = 0
    fill_only_option: int = 0
    prune_gotta_be_here: int = 0
    prune_magic_pairs: int = 0
    prune_magic_triplets: int = 0
    prune_magic_quads: int = 0
    solve_loops: int = 0

    def reset(self) -> None:
        """Reset all metrics to zero."""
        for field in self.__dataclass_fields__:
            setattr(self, field, 0)


class SudokuError(Exception):
    """Custom exception for Sudoku-related errors."""
    pass


class SudokuCell:
    """Represents a single cell in the Sudoku grid."""
    
    # Constants
    GRID_SIZE = 9
    BLOCK_SIZE = 3
    VALID_VALUES = set(range(1, 10))
    
    def __init__(self, value: int, row: int, col: int) -> None:
        """
        Initialize a Sudoku cell.
        
        Args:
            value: The cell value (0 for empty, 1-9 for filled)
            row: Row index (0-8)
            col: Column index (0-8)
            
        Raises:
            SudokuError: If value or position is invalid
        """
        if not (0 <= value <= 9):
            raise SudokuError(f"Invalid cell value: {value}. Must be 0-9.")
        if not (0 <= row < self.GRID_SIZE):
            raise SudokuError(f"Invalid row: {row}. Must be 0-8.")
        if not (0 <= col < self.GRID_SIZE):
            raise SudokuError(f"Invalid column: {col}. Must be 0-8.")
            
        self.value = value
        self.row = row
        self.col = col
        self.block = (row // self.BLOCK_SIZE) * self.BLOCK_SIZE + (col // self.BLOCK_SIZE)
        self.candidates: Set[int] = set()
        
        # Initialize candidates for empty cells
        if self.value == 0:
            self.candidates = self.VALID_VALUES.copy()
    
    def set_value(self, value: int) -> None:
        """Set the cell value and clear candidates."""
        if value not in self.VALID_VALUES:
            raise SudokuError(f"Invalid value: {value}. Must be 1-9.")
        self.value = value
        self.candidates.clear()
    
    def is_empty(self) -> bool:
        """Check if the cell is empty."""
        return self.value == 0
    
    def remove_candidate(self, candidate: int) -> bool:
        """
        Remove a candidate from the cell.
        
        Returns:
            True if candidate was removed, False if it wasn't present
        """
        if candidate in self.candidates:
            self.candidates.discard(candidate)
            return True
        return False
    
    def __str__(self) -> str:
        """String representation of the cell."""
        return str(self.value) if self.value != 0 else "."
    
    def __repr__(self) -> str:
        """Detailed representation of the cell."""
        return f"SudokuCell(value={self.value}, row={self.row}, col={self.col}, candidates={self.candidates})"


class SudokuPuzzle:
    """
    A class to load and validate Sudoku puzzles from JSON files.
    
    This class handles loading Sudoku puzzles from JSON files, validating
    their structure and content, and providing access to the puzzle data.
    """
    
    def __init__(self, filename: str) -> None:
        """
        Initialize a SudokuPuzzle by loading from a JSON file.
        
        Args:
            filename: Path to the JSON file containing the Sudoku puzzle
            
        Raises:
            ValueError: If the file doesn't exist, is malformed, or contains invalid data
            FileNotFoundError: If the file path doesn't exist
        """
        self.filename = filename
        self.puzzle: List[List[int]] = []
        
        # Load and validate the puzzle
        self._load_puzzle()
        self._validate_puzzle()
    
    def _load_puzzle(self) -> None:
        """
        Load the puzzle from the JSON file.
        
        Raises:
            ValueError: If the file is malformed JSON or doesn't contain a list
            FileNotFoundError: If the file doesn't exist
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Sudoku puzzle file not found: {self.filename}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.filename}: {e}")
        
        # Check if the loaded data is a list
        if not isinstance(data, list):
            raise ValueError(f"JSON file {self.filename} must contain a list, got {type(data).__name__}")
        
        self.puzzle = data
    
    def _validate_puzzle(self) -> None:
        """
        Validate the structure and content of the loaded puzzle.
        
        Raises:
            ValueError: If the puzzle structure or content is invalid
        """
        # Check if we have exactly 9 rows
        if len(self.puzzle) != 9:
            raise ValueError(f"Puzzle must have exactly 9 rows, got {len(self.puzzle)}")
        
        # Check each row
        for row_idx, row in enumerate(self.puzzle):
            # Check if each row is a list
            if not isinstance(row, list):
                raise ValueError(f"Row {row_idx} must be a list, got {type(row).__name__}")
            
            # Check if each row has exactly 9 elements
            if len(row) != 9:
                raise ValueError(f"Row {row_idx} must have exactly 9 elements, got {len(row)}")
            
            # Check each cell value
            for col_idx, value in enumerate(row):
                if not isinstance(value, int):
                    raise ValueError(f"Cell at ({row_idx}, {col_idx}) must be an integer, got {type(value).__name__}")
                
                if not (0 <= value <= 9):
                    raise ValueError(f"Cell at ({row_idx}, {col_idx}) must be 0-9, got {value}")
    
    def __repr__(self) -> str:
        """
        Return a compact string representation of the puzzle.
        
        Returns:
            A string with 9 lines of digits, spaces for zeros
        """
        lines = []
        for row in self.puzzle:
            # Convert each row to a string, replacing 0 with space
            row_str = ''.join(str(cell) if cell != 0 else ' ' for cell in row)
            lines.append(row_str)
        return '\n'.join(lines)
    
    def __str__(self) -> str:
        """Return the same representation as __repr__."""
        return self.__repr__()
    
    def get_empty_cells_count(self) -> int:
        """
        Count the number of empty cells (zeros) in the puzzle.
        
        Returns:
            Number of empty cells
        """
        return sum(1 for row in self.puzzle for cell in row if cell == 0)
    
    def is_solved(self) -> bool:
        """
        Check if the puzzle is completely filled (no zeros).
        
        Returns:
            True if puzzle has no empty cells, False otherwise
        """
        return self.get_empty_cells_count() == 0
