# Command Line Usage Guide

This guide explains how to use the Sudoku solver classes (`sudoku_models.py` and `sudoku_solver.py`) from the command line.

## Table of Contents
- [Quick Start](#quick-start)
- [Method 1: Using Python's Interactive Mode](#method-1-using-pythons-interactive-mode)
- [Method 2: Using the CLI Script](#method-2-using-the-cli-script)
- [Method 3: Creating Your Own Script](#method-3-creating-your-own-script)
- [Method 4: Running Built-in Examples](#method-4-running-built-in-examples)
- [Classes Overview](#classes-overview)
- [Examples](#examples)

## Quick Start

The easiest way to use the Sudoku solver from the command line:

```bash
# From the project root directory
python -m src.sudoku_solver.cli --file examples/examples_data/NYT-EASY-2025-09-27_puzzle.json
```

## Method 1: Using Python's Interactive Mode

Open Python in interactive mode and import the classes:

```bash
# Navigate to the project root
cd /path/to/SudokuSolver

# Start Python (ensure src is in the path)
python
```

Then in the Python shell:

```python
# Import the classes
from src.sudoku_models import SudokuPuzzle
from src.sudoku_solver import SudokuSolver, solve_sudoku

# Load a puzzle from a JSON file
puzzle = SudokuPuzzle('examples/examples_data/NYT-EASY-2025-09-27_puzzle.json')

# Create a solver with the puzzle
solver = SudokuSolver(puzzle.puzzle, debug_level=1)

# Solve the puzzle
solved = solver.solve()

# Print the solution
solver.print_grid()
```

## Method 2: Using the CLI Script

A command-line interface script is available. Navigate to the project root and run:

```bash
# Basic usage - solve from JSON file
python -m src.sudoku_solver.cli --file examples/examples_data/NYT-EASY-2025-09-27_puzzle.json

# With detailed debug output
python -m src.sudoku_solver.cli --file puzzle.json --debug 2

# Silent mode (minimal output)
python -m src.sudoku_solver.cli --file puzzle.json --debug 0

# Save solution to a file
python -m src.sudoku_solver.cli --file puzzle.json --output solution.json

# Step-by-step solving (interactive)
python -m src.sudoku_solver.cli --file puzzle.json --step

# Inline puzzle (not from file)
python -m src.sudoku_solver.cli --puzzle "[[0,2,0,0,8,0,3,0,0],[4,5,9,0,0,7,0,8,6],[0,0,7,1,6,0,5,4,0],[0,0,2,6,9,0,8,0,0],[0,6,5,3,4,0,0,0,7],[1,0,0,7,0,0,0,9,3],[0,0,0,0,0,6,9,3,5],[0,7,6,9,0,3,0,0,0],[8,0,0,0,0,4,0,0,1]]"
```

### CLI Options

- `--file` or `-f`: Path to JSON file containing the puzzle
- `--puzzle` or `-p`: Inline puzzle as JSON string
- `--output` or `-o`: Path to save the solution JSON
- `--debug` or `-d`: Debug level (0-3, default: 1)
  - 0 = Silent (no output)
  - 1 = Informational (shows progress)
  - 2 = Detailed (shows solving techniques)
  - 3 = Verbose (maximum detail)
- `--step`: Solve one step at a time (press Enter to continue)

## Method 3: Creating Your Own Script

Create a Python script to use the classes programmatically:

```python
#!/usr/bin/env python3
"""My Sudoku Solver Script"""

import sys
sys.path.insert(0, 'src')  # Add src to path

from sudoku_models import SudokuPuzzle
from sudoku_solver import SudokuSolver

# Load a puzzle
puzzle = SudokuPuzzle('examples/examples_data/NYT-EASY-2025-09-27_puzzle.json')

# Create solver
solver = SudokuSolver(puzzle.puzzle, debug_level=1)

# Solve
solved = solver.solve()

if solved:
    print("Puzzle solved!")
    solver.print_grid()
else:
    print(f"Could not solve completely. {solver.count_empty_cells()} cells remain.")
```

Save this as `my_solver.py` and run:
```bash
python my_solver.py
```

## Method 4: Running Built-in Examples

The project includes example scripts:

```bash
# Run the demo
python examples/demo.py

# Run the end-to-end example
python examples/end_to_end_example.py
```

## Classes Overview

### SudokuPuzzle (from `sudoku_models.py`)

Loads and validates Sudoku puzzles from JSON files.

**Key Methods:**
- `__init__(filename)`: Load puzzle from JSON file
- `get_empty_cells_count()`: Return number of empty cells
- `is_solved()`: Check if puzzle is fully filled
- `__str__()` / `__repr__()`: Print puzzle grid

**Example:**
```python
from sudoku_models import SudokuPuzzle

puzzle = SudokuPuzzle('puzzle.json')
print(f"Empty cells: {puzzle.get_empty_cells_count()}")
print(puzzle)  # Prints the puzzle grid
```

### SudokuSolver (from `sudoku_solver.py`)

Solves Sudoku puzzles using multiple techniques.

**Key Methods:**
- `__init__(puzzle, debug_level=0)`: Initialize solver
- `solve()`: Solve the puzzle completely
- `step_solve()`: Perform one solving step
- `print_grid(force_print=True)`: Print current grid state
- `count_empty_cells()`: Return number of empty cells

**Properties:**
- `metrics`: `SolvingMetrics` object tracking solving techniques used

**Example:**
```python
from sudoku_solver import SudokuSolver

puzzle = [[0,2,0,...], [4,5,9,...], ...]  # 9x9 grid
solver = SudokuSolver(puzzle, debug_level=1)
solved = solver.solve()

# Access metrics
print(f"Solve loops: {solver.metrics.solve_loops}")
print(f"Naked singles: {solver.metrics.fill_only_candidate}")
```

### solve_sudoku (convenience function)

A simple function that solves a puzzle in one call:

```python
from sudoku_solver import solve_sudoku

puzzle = [[0,2,0,...], [4,5,9,...], ...]
solved = solve_sudoku(puzzle, debug_level=1)
print(f"Solved: {solved}")
```

## Examples

### Example 1: Basic Solving

```python
from sudoku_solver import solve_sudoku

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
print(f"Solved: {solved}")
```

### Example 2: Advanced Usage with Metrics

```python
from sudoku_models import SudokuPuzzle
from sudoku_solver import SudokuSolver

# Load puzzle
puzzle = SudokuPuzzle('examples/examples_data/NYT-EASY-2025-09-27_puzzle.json')

# Create solver with detailed output
solver = SudokuSolver(puzzle.puzzle, debug_level=2)

# Solve
solved = solver.solve()

# Display metrics
if solved:
    print(f"\nSolved in {solver.metrics.solve_loops} iterations!")
    print(f"Techniques used:")
    print(f"  Naked singles: {solver.metrics.fill_only_candidate}")
    print(f"  Hidden singles: {solver.metrics.fill_only_option}")
    print(f"  Intersection removal: {solver.metrics.prune_gotta_be_here}")
    print(f"  Naked groups: {solver.metrics.prune_magic_pairs}")
```

### Example 3: Step-by-Step Solving

```python
from sudoku_solver import SudokuSolver

puzzle = [[0,2,0,...], [4,5,9,...], ...]
solver = SudokuSolver(puzzle, debug_level=2)

# Solve step by step
step = 1
while solver.count_empty_cells() > 0:
    print(f"\n=== Step {step} ===")
    solved = solver.step_solve()
    
    if solved:
        print("Puzzle solved!")
        break
    elif solver.count_empty_cells() > 0:
        input("Press Enter to continue...")
        step += 1
    else:
        print("No more progress possible")
        break
```

### Example 4: Save Solution to File

```python
import json
from sudoku_models import SudokuPuzzle
from sudoku_solver import SudokuSolver

# Load and solve
puzzle = SudokuPuzzle('puzzle.json')
solver = SudokuSolver(puzzle.puzzle)
solved = solver.solve()

if solved:
    # Extract solution
    solution = [[cell.value for cell in row] for row in solver.grid]
    
    # Save to file
    with open('solution.json', 'w') as f:
        json.dump(solution, f, indent=2)
    
    print("Solution saved to solution.json")
```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the project root and that the `src` directory is in your Python path:

```bash
# From project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python your_script.py
```

Or add to your script:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
```

### JSON File Format

The JSON file must contain a 9x9 array of integers (0-9):
```json
[
  [0, 2, 0, 0, 8, 0, 3, 0, 0],
  [4, 5, 9, 0, 0, 7, 0, 8, 6],
  ...
]
```

### Puzzle Cannot Be Solved

If the solver reports the puzzle cannot be solved, it may require advanced techniques not yet implemented, or it may be an invalid puzzle. Check with `--step` mode to see where solving stops.

## Additional Resources

- See `examples/demo.py` for more examples
- See `tests/` directory for unit test examples
- See `docs/application_flow.md` for detailed algorithm explanation
