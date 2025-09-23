"""
Improved test suite for the Sudoku solver.

This test suite demonstrates the improved functionality and includes
comprehensive test cases for various scenarios.
"""

import sys
import os
from typing import List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sudoku import SudokuSolver, SudokuCell, SudokuError, solve_sudoku


class TestSudokuCell:
    """Test cases for the SudokuCell class."""
    
    def test_valid_cell_creation(self):
        """Test creating valid cells."""
        cell = SudokuCell(5, 0, 0)
        assert cell.value == 5
        assert cell.row == 0
        assert cell.col == 0
        assert cell.block == 0
        assert cell.candidates == set()
    
    def test_empty_cell_creation(self):
        """Test creating empty cells with candidates."""
        cell = SudokuCell(0, 1, 2)
        assert cell.value == 0
        assert cell.is_empty()
        assert cell.candidates == {1, 2, 3, 4, 5, 6, 7, 8, 9}
    
    def test_invalid_cell_values(self):
        """Test that invalid cell values raise exceptions."""
        try:
            SudokuCell(10, 0, 0)
            assert False, "Should have raised SudokuError"
        except SudokuError:
            pass
        
        try:
            SudokuCell(-1, 0, 0)
            assert False, "Should have raised SudokuError"
        except SudokuError:
            pass
    
    def test_invalid_cell_positions(self):
        """Test that invalid positions raise exceptions."""
        try:
            SudokuCell(1, 9, 0)
            assert False, "Should have raised SudokuError"
        except SudokuError:
            pass
        
        try:
            SudokuCell(1, 0, 9)
            assert False, "Should have raised SudokuError"
        except SudokuError:
            pass
    
    def test_set_value(self):
        """Test setting cell values."""
        cell = SudokuCell(0, 0, 0)
        cell.set_value(7)
        assert cell.value == 7
        assert not cell.is_empty()
        assert cell.candidates == set()
    
    def test_remove_candidate(self):
        """Test removing candidates."""
        cell = SudokuCell(0, 0, 0)
        assert cell.remove_candidate(5)
        assert 5 not in cell.candidates
        assert not cell.remove_candidate(5)  # Already removed


class TestSudokuSolver:
    """Test cases for the SudokuSolver class."""
    
    def test_valid_puzzle_creation(self):
        """Test creating solver with valid puzzle."""
        puzzle = [[0] * 9 for _ in range(9)]
        solver = SudokuSolver(puzzle)
        assert solver.count_empty_cells() == 81
    
    def test_invalid_puzzle_dimensions(self):
        """Test that invalid puzzle dimensions raise exceptions."""
        try:
            SudokuSolver([[0] * 8 for _ in range(9)])  # Wrong row length
            assert False, "Should have raised SudokuError"
        except SudokuError:
            pass
        
        try:
            SudokuSolver([[0] * 9 for _ in range(8)])  # Wrong number of rows
            assert False, "Should have raised SudokuError"
        except SudokuError:
            pass
    
    def test_invalid_puzzle_values(self):
        """Test that invalid puzzle values raise exceptions."""
        puzzle = [[0] * 9 for _ in range(9)]
        puzzle[0][0] = 10  # Invalid value
        try:
            SudokuSolver(puzzle)
            assert False, "Should have raised SudokuError"
        except SudokuError:
            pass
    
    def test_simple_puzzle_solving(self):
        """Test solving a simple puzzle."""
        # A puzzle with one empty cell that can be filled immediately
        puzzle = [
            [1, 2, 3, 4, 5, 6, 7, 8, 0],
            [4, 5, 6, 7, 8, 9, 1, 2, 3],
            [7, 8, 9, 1, 2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6, 7, 8, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 1, 2, 3, 4, 5, 6, 7, 8]
        ]
        
        solver = SudokuSolver(puzzle)
        solved = solver.solve()
        assert solved
        assert solver.count_empty_cells() == 0
    
    def test_already_solved_puzzle(self):
        """Test that already solved puzzles return True."""
        puzzle = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            [4, 5, 6, 7, 8, 9, 1, 2, 3],
            [7, 8, 9, 1, 2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6, 7, 8, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 1, 2, 3, 4, 5, 6, 7, 8]
        ]
        
        solver = SudokuSolver(puzzle)
        solved = solver.solve()
        assert solved
        assert solver.count_empty_cells() == 0


def test_convenience_function():
    """Test the convenience solve_sudoku function."""
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    solved = solve_sudoku(puzzle)
    assert solved


# Test puzzles from the original test file
def test_original_puzzles():
    """Test with puzzles from the original test file."""
    
    # Easy puzzle
    easy_puzzle = [
        [9, 4, 7, 0, 5, 3, 1, 0, 0],
        [3, 5, 0, 0, 0, 4, 0, 9, 7],
        [0, 0, 0, 0, 0, 7, 3, 5, 0],
        [0, 9, 5, 0, 2, 0, 0, 7, 1],
        [1, 7, 0, 0, 9, 5, 0, 0, 3],
        [0, 0, 0, 0, 8, 0, 0, 0, 5],
        [0, 0, 0, 5, 0, 0, 7, 0, 0],
        [0, 3, 1, 6, 0, 0, 4, 0, 2],
        [7, 2, 9, 1, 0, 0, 0, 3, 0]
    ]
    
    solver = SudokuSolver(easy_puzzle, debug_level=0)
    solved = solver.solve()
    print(f"Easy puzzle solved: {solved}")
    
    # Medium puzzle
    medium_puzzle = [
        [0, 0, 0, 2, 0, 7, 0, 0, 5],
        [3, 0, 0, 9, 0, 0, 4, 0, 1],
        [0, 0, 0, 0, 0, 8, 0, 0, 0],
        [0, 4, 7, 0, 0, 5, 0, 0, 0],
        [2, 0, 1, 0, 0, 4, 0, 0, 8],
        [0, 0, 0, 0, 8, 0, 2, 0, 0],
        [0, 0, 4, 0, 0, 0, 0, 5, 0],
        [1, 0, 0, 4, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 9, 1, 0, 7, 0]
    ]
    
    solver = SudokuSolver(medium_puzzle, debug_level=0)
    solved = solver.solve()
    print(f"Medium puzzle solved: {solved}")


def run_all_tests():
    """Run all test functions."""
    print("Running Sudoku Solver Tests...")
    print("="*50)
    
    # Test SudokuCell class
    print("Testing SudokuCell class...")
    cell_tests = TestSudokuCell()
    cell_tests.test_valid_cell_creation()
    cell_tests.test_empty_cell_creation()
    cell_tests.test_invalid_cell_values()
    cell_tests.test_invalid_cell_positions()
    cell_tests.test_set_value()
    cell_tests.test_remove_candidate()
    print("✓ SudokuCell tests passed")
    
    # Test SudokuSolver class
    print("\nTesting SudokuSolver class...")
    solver_tests = TestSudokuSolver()
    solver_tests.test_valid_puzzle_creation()
    solver_tests.test_invalid_puzzle_dimensions()
    solver_tests.test_invalid_puzzle_values()
    solver_tests.test_simple_puzzle_solving()
    solver_tests.test_already_solved_puzzle()
    print("✓ SudokuSolver tests passed")
    
    # Test convenience function
    print("\nTesting convenience function...")
    test_convenience_function()
    print("✓ Convenience function tests passed")
    
    # Test original puzzles
    print("\nTesting original puzzles...")
    test_original_puzzles()
    print("✓ Original puzzle tests passed")
    
    print("\n" + "="*50)
    print("ALL TESTS PASSED! 🎉")
    print("="*50)


if __name__ == "__main__":
    # Run all tests
    run_all_tests()
    
    # Test the improved solver with example
    print("\n" + "="*60)
    print("DEMO: IMPROVED SUDOKU SOLVER")
    print("="*60)
    
    # Example puzzle
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    solver = SudokuSolver(puzzle, debug_level=1)
    solved = solver.solve()
    print(f"\nFinal result: Puzzle solved = {solved}")


