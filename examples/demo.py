"""
Demo script showing how to use the Sudoku Solver
"""

import sys
import os

# Add the src directory to the path so we can import the solver
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sudoku_solver import solve_sudoku, SudokuSolver


def main():
    """Demonstrate the Sudoku solver with different examples."""
    
    print("=" * 60)
    print("SUDOKU SOLVER DEMO")
    print("=" * 60)
    
    # Example 1: Simple puzzle
    print("\n1. Simple Puzzle Example:")
    print("-" * 30)
    
    simple_puzzle = [
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
    
    # Use the simple API
    solved = solve_sudoku(simple_puzzle)
    print(f"Puzzle solved: {solved}")
    
    # Example 2: Advanced usage with debug output
    print("\n2. Advanced Usage with Debug Output:")
    print("-" * 40)
    
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
    
    # Use the advanced API with debug output
    solver = SudokuSolver(medium_puzzle, debug_level=1)
    solved = solver.solve()
    
    if solved:
        print(f"\nSolved in {solver.metrics.solve_loops} iterations!")
        print(f"Techniques used:")
        print(f"  Naked singles: {solver.metrics.fill_only_candidate}")
        print(f"  Hidden singles: {solver.metrics.fill_only_option}")
        print(f"  Intersection removal: {solver.metrics.prune_gotta_be_here}")
        print(f"  Naked groups: {solver.metrics.prune_magic_pairs}")
    else:
        print("Puzzle could not be solved with current techniques")
    
    # Example 3: Error handling
    print("\n3. Error Handling Example:")
    print("-" * 30)
    
    try:
        invalid_puzzle = [[1, 2, 3]] * 9  # Wrong dimensions
        solve_sudoku(invalid_puzzle)
    except Exception as e:
        print(f"Caught expected error: {e}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
