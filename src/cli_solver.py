#!/usr/bin/env python3
"""
Command-line interface for solving Sudoku puzzles.

This script provides a simple CLI for using SudokuSolver to solve puzzles
from JSON files or inline puzzle definitions.

Usage:
    # From JSON file
    python -m sudoku_solver.cli --file examples/examples_data/NYT-EASY-2025-09-27_puzzle.json
    
    # From inline puzzle (example grid)
    python -m sudoku_solver.cli --puzzle "[[0,2,0,0,8,0,3,0,0],[4,5,9,0,0,7,0,8,6],...]"
    
    # With debug output
    python -m sudoku_solver.cli --file puzzle.json --debug 2
"""

import argparse
import sys
from pathlib import Path
import json
from typing import List

from sudoku_models import SudokuPuzzle, SudokuError
from sudoku_solver import SudokuSolver


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Solve Sudoku puzzles from JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Solve from JSON file
  python -m sudoku_solver.cli --file examples/examples_data/NYT-EASY-2025-09-27_puzzle.json
  
  # Solve with detailed debug output
  python -m sudoku_solver.cli --file puzzle.json --debug 2
  
  # Solve with minimal output
  python -m sudoku_solver.cli --file puzzle.json --debug 0
  
  # Save solution to JSON
  python -m sudoku_solver.cli --file puzzle.json --output solution.json
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--file", "-f",
        help="Path to JSON file containing the puzzle (9x9 array)"
    )
    input_group.add_argument(
        "--puzzle", "-p",
        help="Inline puzzle definition as JSON string"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        help="Path to save the solution JSON (optional)"
    )
    
    parser.add_argument(
        "--debug", "-d",
        type=int,
        default=1,
        help="Debug level (0=silent, 1=info, 2=detailed, 3=verbose) (default: 1)"
    )
    
    parser.add_argument(
        "--step",
        action="store_true",
        help="Solve one step at a time (for debugging)"
    )
    
    args = parser.parse_args()
    
    try:
        # Load puzzle
        if args.file:
            puzzle_path = Path(args.file)
            if not puzzle_path.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(1)
            
            puzzle = SudokuPuzzle(str(puzzle_path))
            grid = puzzle.puzzle
            
        else:  # --puzzle
            try:
                grid = json.loads(args.puzzle)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in puzzle argument: {e}", file=sys.stderr)
                sys.exit(1)
        
        # Validate grid
        if not isinstance(grid, list) or len(grid) != 9:
            print("Error: Puzzle must be a 9x9 grid", file=sys.stderr)
            sys.exit(1)
        
        for i, row in enumerate(grid):
            if not isinstance(row, list) or len(row) != 9:
                print(f"Error: Row {i} must have 9 elements", file=sys.stderr)
                sys.exit(1)
        
        # Create solver
        solver = SudokuSolver(grid, debug_level=args.debug)
        
        # Solve puzzle
        print(f"Initial puzzle ({puzzle.get_empty_cells_count() if args.file else len([c for row in grid for c in row if c == 0])} empty cells):")
        solver.print_grid(False)
        
        if args.step:
            # Solve step by step
            step_count = 0
            while solver.count_empty_cells() > 0:
                step_count += 1
                input(f"\nPress Enter for step {step_count}...")
                solved = solver.step_solve()
                if solved:
                    print("\nPuzzle solved!")
                    break
                elif solver.count_empty_cells() == len([c for row in grid for c in row if c == 0]):
                    print("\nNo progress - puzzle may be unsolvable with current techniques")
                    break
        else:
            # Solve completely
            solved = solver.solve()
        
        if not solved:
            print(f"\nWarning: Puzzle not fully solved. {solver.count_empty_cells()} cells remain.")
            sys.exit(2)
        
        # Output solution
        solution = [[cell.value for cell in row] for row in solver.grid]
        
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(solution, f, indent=2)
            print(f"\nSolution saved to: {output_path}")
        
        # Exit successfully
        sys.exit(0)
        
    except SudokuError as e:
        print(f"Sudoku Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
