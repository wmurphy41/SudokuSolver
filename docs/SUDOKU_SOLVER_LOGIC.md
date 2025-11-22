# Sudoku Solver Logic Documentation

This document describes the core logic and architecture of the SudokuSolver engine, covering the data models (`sudoku_models.py`) and solving algorithms (`sudoku_solver.py`).

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Models](#data-models)
3. [Solving Engine](#solving-engine)
4. [Solving Techniques](#solving-techniques)
5. [Algorithm Flow](#algorithm-flow)
6. [Usage Examples](#usage-examples)

---

## Architecture Overview

The Sudoku solver is built on a constraint-based solving approach using candidate elimination. The system consists of:

- **Data Models**: Core data structures representing cells, puzzles, and metrics
- **Solver Engine**: Main solving logic implementing multiple techniques
- **Constraint Propagation**: Automatic removal of impossible candidates
- **Iterative Refinement**: Multiple passes through solving techniques

### Key Design Principles

1. **Candidate-Based**: Each empty cell maintains a set of possible values (candidates)
2. **Constraint Propagation**: Filling a cell automatically removes candidates from related cells
3. **Progressive Techniques**: Starts with simple techniques, progresses to advanced methods
4. **Metrics Tracking**: Records which techniques were used and how often

---

## Data Models

### SudokuCell Class

Represents a single cell in the 9×9 Sudoku grid.

#### Properties

- `value` (int): Cell value (0 = empty, 1-9 = filled)
- `row` (int): Row index (0-8)
- `col` (int): Column index (0-8)
- `block` (int): 3×3 block index (0-8), calculated automatically
- `candidates` (Set[int]): Set of possible values for empty cells

#### Key Methods

- `set_value(value)`: Sets cell value and clears candidates
- `is_empty()`: Returns True if cell is empty (value == 0)
- `remove_candidate(candidate)`: Removes a candidate value, returns True if removed

#### Block Calculation

The block index is calculated as:
```python
block = (row // 3) * 3 + (col // 3)
```

This creates 9 blocks numbered 0-8:
- Block 0: rows 0-2, cols 0-2
- Block 1: rows 0-2, cols 3-5
- Block 2: rows 0-2, cols 6-8
- Block 3: rows 3-5, cols 0-2
- ... and so on

### SudokuPuzzle Class

Handles loading and validating Sudoku puzzles from JSON files.

#### Initialization

```python
puzzle = SudokuPuzzle("path/to/puzzle.json")
```

The constructor:
1. Loads JSON file and validates format
2. Validates grid structure (9×9)
3. Validates cell values (0-9)

#### Validation Rules

- Must have exactly 9 rows
- Each row must have exactly 9 elements
- All values must be integers in range 0-9
- Raises `ValueError` or `FileNotFoundError` on validation failure

#### Key Methods

- `get_empty_cells_count()`: Returns number of empty cells (zeros)
- `is_solved()`: Returns True if no empty cells remain
- `__repr__()`: Returns formatted string representation

### SolvingMetrics Dataclass

Tracks solving performance and technique usage.

#### Metrics Tracked

- `fill_only_candidate`: Count of naked singles filled
- `fill_only_option`: Count of hidden singles filled
- `prune_gotta_be_here`: Count of intersection removal operations
- `prune_magic_pairs`: Count of naked group operations (pairs, triples, quads)
- `prune_magic_triplets`: Reserved for future use
- `prune_magic_quads`: Reserved for future use
- `solve_loops`: Number of solving iterations performed

#### Methods

- `reset()`: Resets all metrics to zero

### Difficulty Enum

Enumeration for puzzle difficulty levels (currently not actively used in solving logic):
- `EASY`
- `MEDIUM`
- `HARD`
- `EXPERT`

### SudokuError Exception

Custom exception raised for Sudoku-related errors (invalid values, dimensions, etc.).

---

## Solving Engine

### SudokuSolver Class

Main solver class implementing comprehensive solving techniques.

#### Initialization

```python
solver = SudokuSolver(puzzle, debug_level=0)
```

**Parameters:**
- `puzzle`: 9×9 grid of integers (0 for empty, 1-9 for filled)
- `debug_level`: Output verbosity (0=silent, 1=info, 2=basic, 3=detailed)

**Process:**
1. Validates puzzle format
2. Creates `SudokuCell` objects for each cell
3. Initializes candidates for empty cells
4. Performs initial constraint propagation

#### Core Methods

##### `solve() -> bool`

Solves the puzzle completely using iterative refinement.

**Algorithm:**
1. Reset metrics
2. While empty cells remain:
   - Try filling cells (naked singles, hidden singles)
   - If no cells filled, try pruning candidates (intersection removal, naked groups, hidden groups)
   - If no progress made, break (puzzle may be unsolvable)
3. Return True if solved, False otherwise

**Returns:** `True` if puzzle is completely solved, `False` otherwise

##### `step_solve() -> bool`

Performs one solving pass without looping.

**Algorithm:**
1. Increment solve loop counter
2. Try filling cells (naked singles, hidden singles)
3. If no cells filled, try pruning candidates
4. Return True if puzzle is now solved

**Use Case:** Useful for step-by-step solving or debugging

##### `count_empty_cells() -> int`

Returns the number of empty cells remaining.

##### `print_grid(force_print=True)`

Displays the current grid state with 3×3 block separators.

##### `print_candidates(force_print=True)`

Displays candidates for all cells (debugging aid).

#### Iterator Methods

The solver provides efficient iterators for constraint groups:

- `_iterate_all_cells()`: Iterates through all 81 cells
- `_iterate_block(block_num)`: Iterates through cells in a 3×3 block
- `_iterate_row(row_num)`: Iterates through cells in a row
- `_iterate_col(col_num)`: Iterates through cells in a column

---

## Solving Techniques

### 1. Naked Singles (`_fill_naked_singles`)

**Principle:** If a cell has only one candidate, that value must be correct.

**Algorithm:**
1. Iterate through all empty cells
2. If a cell has exactly one candidate:
   - Set cell value to that candidate
   - Remove candidate from related cells (same block, row, column)
   - Increment metrics

**Complexity:** O(81) per pass

### 2. Hidden Singles (`_fill_hidden_singles`)

**Principle:** If a value can only appear in one cell within a constraint group (block/row/column), that cell must contain that value.

**Algorithm:**
1. For each constraint group (block, row, column):
   - For each value 1-9:
     - Find all empty cells in the group that have this value as a candidate
     - If exactly one cell has this candidate:
       - Set that cell's value
       - Remove candidate from related cells
       - Increment metrics

**Complexity:** O(9 × 9 × 3) = O(243) per pass

### 3. Intersection Removal (`_prune_intersection_removal`)

**Principle:** If all cells containing a candidate value in a block are in the same row (or column), that value can be removed from other cells in that row (or column) outside the block.

**Algorithm:**
1. For each constraint group (block, row, column):
   - For each value 1-9:
     - Find all empty cells in the group with this candidate
     - If all cells are in the same sub-group:
       - Remove candidate from other cells in that sub-group
       - Increment metrics

**Example:**
```
In Block 0 (top-left), value 5 can only appear in row 0.
Therefore, 5 can be removed from row 0 cells in blocks 1 and 2.
```

**Complexity:** O(9 × 9 × 3) = O(243) per pass

### 4. Naked Groups (`_prune_naked_groups`)

**Principle:** If N cells in a constraint group contain exactly N candidates (and no others), those candidates can be removed from other cells in the group.

**Types:**
- **Naked Pairs**: 2 cells with exactly 2 candidates total
- **Naked Triples**: 3 cells with exactly 3 candidates total
- **Naked Quads**: 4 cells with exactly 4 candidates total

**Algorithm:**
1. For each constraint group (block, row, column):
   - Find all combinations of 2, 3, or 4 empty cells
   - If the union of candidates equals the group size:
     - Remove those candidates from other cells in the group
     - Increment metrics

**Example:**
```
Two cells in a row have candidates {3, 7} and {3, 7}.
These cells must contain 3 and 7.
Therefore, 3 and 7 can be removed from all other cells in that row.
```

**Complexity:** O(9 × C(n,2) + C(n,3) + C(n,4)) where n is number of empty cells per group

### 5. Hidden Groups (`_prune_hidden_groups`)

**Status:** Currently stubbed (returns 0). Future implementation would find groups where N values can only appear in N cells.

---

## Algorithm Flow

### Complete Solve Flow

```
1. Initialize
   ├─ Validate puzzle format
   ├─ Create SudokuCell objects
   └─ Initialize candidates (remove impossible values)

2. Main Solving Loop
   ├─ Increment solve_loops counter
   ├─ Try Filling Cells
   │  ├─ Fill naked singles
   │  └─ Fill hidden singles
   │
   ├─ If no cells filled, try Pruning Candidates
   │  ├─ Apply intersection removal
   │  ├─ Apply naked groups (pairs, triples, quads)
   │  └─ Apply hidden groups (stubbed)
   │
   └─ Check Termination
      ├─ If puzzle solved → return True
      ├─ If no progress → break, return False
      └─ Otherwise → continue loop

3. Print Summary
   └─ Display metrics and final state
```

### Step Solve Flow

```
1. Increment solve_loops counter
2. Try Filling Cells
   ├─ Fill naked singles
   └─ Fill hidden singles
3. If no cells filled, try Pruning Candidates
   ├─ Apply intersection removal
   ├─ Apply naked groups
   └─ Apply hidden groups
4. Return solved status
```

### Constraint Propagation

When a cell is filled via `_fill_cell()`:

```
1. Set cell value
2. Clear cell's candidates
3. For each related cell (same block, row, column):
   └─ Remove filled value from that cell's candidates
```

This automatic propagation ensures consistency without explicit checks.

---

## Usage Examples

### Basic Solving

```python
from src.sudoku_solver import SudokuSolver

puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    # ... rest of puzzle
]

solver = SudokuSolver(puzzle, debug_level=1)
solved = solver.solve()

if solved:
    print("Puzzle solved!")
    solver.print_grid()
else:
    print(f"Puzzle not fully solved. {solver.count_empty_cells()} cells remain.")
```

### Step-by-Step Solving

```python
solver = SudokuSolver(puzzle, debug_level=2)

while solver.count_empty_cells() > 0:
    solved = solver.step_solve()
    if solved:
        print("Puzzle solved!")
        break
    elif solver.metrics.solve_loops > 50:
        print("Too many steps, stopping")
        break
```

### Loading from JSON

```python
from src.sudoku_models import SudokuPuzzle
from src.sudoku_solver import SudokuSolver

puzzle_obj = SudokuPuzzle("puzzle.json")
solver = SudokuSolver(puzzle_obj.puzzle, debug_level=2)
solved = solver.solve()
```

### Accessing Metrics

```python
solver = SudokuSolver(puzzle)
solver.solve()

print(f"Solve loops: {solver.metrics.solve_loops}")
print(f"Naked singles: {solver.metrics.fill_only_candidate}")
print(f"Hidden singles: {solver.metrics.fill_only_option}")
print(f"Intersection removal: {solver.metrics.prune_gotta_be_here}")
print(f"Naked groups: {solver.metrics.prune_magic_pairs}")
```

### Debug Levels

- **Level 0 (Silent)**: No output except forced prints
- **Level 1 (Informational)**: Shows grids and summaries
- **Level 2 (Basic)**: Shows technique details and progress
- **Level 3 (Detailed)**: Shows all debugging information

---

## Performance Characteristics

### Time Complexity

- **Per iteration**: O(81) for naked singles, O(243) for hidden singles and intersection removal
- **Naked groups**: O(n²) to O(n⁴) depending on number of empty cells per group
- **Overall**: Typically solves easy puzzles in 1-5 iterations, medium in 5-15, hard may require 20+

### Space Complexity

- **Grid storage**: O(81) cells
- **Candidates**: O(81 × 9) = O(729) in worst case (all cells empty with all candidates)
- **Overall**: O(1) - constant space regardless of puzzle difficulty

### Limitations

1. **No Backtracking**: Cannot solve puzzles requiring guessing
2. **No Hidden Groups**: Advanced technique not yet implemented
3. **No X-Wing/Y-Wing**: Advanced techniques not implemented
4. **May Fail**: Some hard puzzles may not be solvable with current techniques

---

## Error Handling

The solver raises `SudokuError` for:
- Invalid puzzle dimensions (not 9×9)
- Invalid cell values (not 0-9)
- Invalid cell positions

The `SudokuPuzzle` class raises:
- `FileNotFoundError`: If JSON file doesn't exist
- `ValueError`: If JSON is malformed or puzzle structure is invalid

---

## Future Enhancements

Potential improvements:
1. Implement hidden groups technique
2. Add X-Wing and Y-Wing techniques
3. Add backtracking for puzzles requiring guessing
4. Add puzzle validation (check for multiple solutions)
5. Add puzzle generation capabilities

