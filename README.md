# SudokuSolver

A comprehensive Python Sudoku solver implementing multiple advanced solving techniques. This project has been significantly improved from its original version with modern Python practices, better performance, and enhanced functionality.

## Features

### Solving Techniques
- **Naked Singles**: Fill cells with only one candidate
- **Hidden Singles**: Fill cells where a value can only go in one position in a constraint group
- **Intersection Removal**: Advanced constraint propagation techniques
- **Naked Groups**: Handle pairs, triples, and quads of candidates
- **Hidden Groups**: Advanced group-based solving techniques

### Key Improvements
- ✅ **Type Safety**: Comprehensive type hints throughout
- ✅ **Error Handling**: Custom exceptions with descriptive messages
- ✅ **Performance**: Optimized algorithms and data structures
- ✅ **Documentation**: Google-style docstrings and clear API
- ✅ **Testing**: Comprehensive test suite with edge cases
- ✅ **Modern Python**: Dataclasses, enums, and best practices

## Project Structure

```
SudokuSolver/
├── src/
│   └── sudoku.py          # Main solver implementation
├── tests/
│   └── test_sudoku.py     # Comprehensive test suite
├── examples/
│   ├── demo.py            # Usage demonstrations
│   └── sample_puzzles.py  # Collection of test puzzles
├── docs/
│   └── IMPROVEMENTS.md    # Detailed improvement documentation
└── README.md              # This file
```

## Installation

No external dependencies required - uses only Python standard library.

```bash
git clone https://github.com/wmurphy41/SudokuSolver.git
cd SudokuSolver
```

## Quick Start

### Basic Usage

```python
from src.sudoku import solve_sudoku

# Define a puzzle (0 = empty cell, 1-9 = filled cells)
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

# Solve the puzzle
solved = solve_sudoku(puzzle)
print(f"Puzzle solved: {solved}")
```

### Advanced Usage

```python
from src.sudoku import SudokuSolver

# Create solver with debug output
solver = SudokuSolver(puzzle, debug_level=1)
solved = solver.solve()

if solved:
    print(f"Solved in {solver.metrics.solve_loops} iterations!")
    print(f"Techniques used:")
    print(f"  Naked singles: {solver.metrics.fill_only_candidate}")
    print(f"  Hidden singles: {solver.metrics.fill_only_option}")
    print(f"  Intersection removal: {solver.metrics.prune_gotta_be_here}")
    print(f"  Naked groups: {solver.metrics.prune_magic_pairs}")
    
    # Display the solved puzzle
    solver.print_grid()
```

## API Reference

### SudokuSolver Class

The main solver class implementing comprehensive Sudoku solving techniques.

#### Constructor
```python
SudokuSolver(puzzle: List[List[int]], debug_level: int = 0)
```

**Parameters:**
- `puzzle`: 9x9 grid of integers (0 for empty cells, 1-9 for filled)
- `debug_level`: Debug output level (0=none, 1=basic, 2=detailed)

**Raises:**
- `SudokuError`: If puzzle format is invalid

#### Methods

- `solve() -> bool`: Solve the puzzle and return success status
- `print_grid()`: Display the current state of the grid
- `print_candidates()`: Show candidates for all cells (debugging aid)
- `count_empty_cells() -> int`: Count remaining empty cells

#### Properties

- `metrics`: `SolvingMetrics` object tracking solving performance
- `debug_level`: Current debug output level

### SudokuCell Class

Represents a single cell in the Sudoku grid.

#### Constructor
```python
SudokuCell(value: int, row: int, col: int)
```

#### Methods

- `set_value(value: int)`: Set cell value and clear candidates
- `is_empty() -> bool`: Check if cell is empty
- `remove_candidate(candidate: int) -> bool`: Remove a candidate

### Convenience Functions

- `solve_sudoku(puzzle: List[List[int]], debug_level: int = 0) -> bool`: Simple solving function

## Running Examples

### Demo Script
```bash
python examples/demo.py
```

### Test Suite
```bash
python tests/test_sudoku.py
```

### Sample Puzzles
```python
from examples.sample_puzzles import matrix_easy_1, matrix_hard_1
from src.sudoku import solve_sudoku

# Try different difficulty levels
print("Easy puzzle:", solve_sudoku(matrix_easy_1))
print("Hard puzzle:", solve_sudoku(matrix_hard_1))
```

## Algorithm Details

The solver uses a multi-pass approach with increasingly sophisticated techniques:

1. **Initialization**: Load puzzle and initialize candidates for empty cells
2. **Constraint Propagation**: Remove impossible candidates based on existing values
3. **Iterative Solving**: Apply techniques in order of complexity:
   - Naked singles (cells with one candidate)
   - Hidden singles (values that can only go in one position)
   - Intersection removal (advanced constraint propagation)
   - Naked groups (pairs, triples, quads)
   - Hidden groups (advanced group techniques)

4. **Termination**: Stop when puzzle is solved or no progress can be made

## Error Handling

The solver includes comprehensive error handling:

```python
from src.sudoku import SudokuError

try:
    solver = SudokuSolver(invalid_puzzle)
except SudokuError as e:
    print(f"Invalid puzzle: {e}")
```

Common error conditions:
- Invalid puzzle dimensions (not 9x9)
- Invalid cell values (not 0-9)
- Malformed input data

## Performance

The improved solver offers significant performance enhancements:

- **Memory**: Reduced object creation and efficient data structures
- **Speed**: Optimized algorithms with better complexity
- **Maintainability**: Clean code structure with comprehensive documentation

## Testing

The project includes a comprehensive test suite covering:

- ✅ Cell creation and validation
- ✅ Puzzle solving with various difficulties
- ✅ Error handling and edge cases
- ✅ Performance validation
- ✅ Original puzzle compatibility

Run tests:
```bash
python tests/test_sudoku.py
```

## Contributing

This project follows modern Python best practices:

- Type hints for all functions and methods
- Comprehensive docstrings
- Error handling with custom exceptions
- Clean separation of concerns
- Extensive testing

## License

Copyright © 2022 [William A. Murphy](https://github.com/wmurphy41).

This project is [MIT](https://spdx.org/licenses/MIT.html) licensed.

## Changelog

### Recent Improvements
- Complete rewrite with modern Python practices
- Added comprehensive type hints and documentation
- Implemented advanced solving techniques
- Enhanced error handling and validation
- Created extensive test suite
- Optimized performance and memory usage

See [docs/IMPROVEMENTS.md](docs/IMPROVEMENTS.md) for detailed improvement documentation.