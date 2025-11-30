# SudokuSolver

A comprehensive Python Sudoku solver with advanced solving techniques and OCR capabilities for extracting and solving Sudoku puzzles from images.

## Features

### Core Solving Engine
- **Naked Singles**: Fill cells with only one candidate
- **Hidden Singles**: Fill cells where a value can only go in one position in a constraint group
- **Intersection Removal**: Advanced constraint propagation techniques
- **Naked Groups**: Handle pairs, triples, and quads of candidates
- **Hidden Groups**: Advanced group-based solving techniques

### Command-Line Interface
- **CLI Solver**: New command-line interface for solving puzzles from JSON files
- **Interactive Mode**: Python shell integration for programmatic puzzle solving
- **Batch Processing**: Silent mode for solving multiple puzzles efficiently
- **Documentation**: Comprehensive command-line usage guide

### Web Application (Beta)
- **React + TypeScript Frontend**: Modern single-page application with responsive design
- **FastAPI Backend**: RESTful API with automatic validation and documentation
- **Integrated Solving**: Fully integrated with core SudokuSolver engine
- **Mode-Based UI**: Edit and Result modes with seamless state management
- **Grid-Based API**: Structured 9×9 grid input/output with type validation
- **Visual Grid Display**: Shows original puzzle and solution as interactive tables with 3×3 box boundaries
- **Debug Levels**: Four debug levels (Silent, Informational, Basic, Detailed) with captured solver logs
- **Sample Puzzles**: Quick-load buttons for Empty, Easy, Medium, and Hard example puzzles
- **Smart Error Handling**: Distinguishes between invalid input, network errors, and solver failures
- **Stepwise Solving**: Redis-backed session-based step-by-step solving with single-technique execution, change tracking, and candidate display
- **Docker Deployment**: Containerized architecture with Nginx reverse proxy and Redis support

### OCR Capabilities (Optional)
- **Image Preprocessing**: Converts images to binary format with adaptive thresholding and morphological operations
- **Grid Detection**: Automatically detects Sudoku grid boundaries and applies perspective correction
- **Cell Extraction**: Splits the corrected grid into 81 individual cells
- **Multi-Method OCR**: Uses Tesseract OCR with multiple fallback preprocessing methods for robust digit recognition
- **End-to-End Pipeline**: Complete workflow from image to solved puzzle

### Key Improvements
- ✅ **Type Safety**: Comprehensive type hints throughout
- ✅ **Error Handling**: Custom exceptions with descriptive messages
- ✅ **Performance**: Optimized algorithms and data structures
- ✅ **Documentation**: Google-style docstrings and clear API
- ✅ **Testing**: Comprehensive test suite with edge cases
- ✅ **Modern Python**: Dataclasses, enums, and best practices
- ✅ **Modular Design**: Separated solving engine and OCR components

## Project Structure

```
SudokuSolver/
├── src/
│   ├── sudoku_models.py       # Data models, enums, exceptions
│   ├── sudoku_solver.py       # Core solving engine
│   ├── cli_solver.py          # CLI for solving puzzles from JSON
│   └── sudoku_ocr/            # OCR processing modules
│       ├── __init__.py        # Package initialization
│       ├── cli.py            # Command-line interface
│       ├── preprocess.py     # Image preprocessing functions
│       ├── grid.py           # Grid detection and warping
 │       ├── cells.py          # Cell extraction
│       └── ocr.py            # Multi-method OCR with Tesseract
├── web/                       # Web application (React + FastAPI)
│   ├── backend/              # FastAPI backend
│   │   ├── app.py           # REST API endpoints
│   │   ├── requirements.txt # Python dependencies
│   │   └── Dockerfile       # Backend container
│   ├── frontend/            # React + TypeScript frontend
│   │   ├── src/             # Source code
│   │   │   ├── components/  # React components
│   │   │   ├── services/    # API service layer
│   │   │   └── types/       # TypeScript types
│   │   ├── package.json     # Node dependencies
│   │   └── Dockerfile.prod  # Production frontend container
│   ├── nginx/               # Nginx reverse proxy config
│   ├── docker-compose.yml   # Container orchestration
│   └── README*.md           # Web app documentation
├── scripts/                  # Build and deployment scripts
│   ├── build-push.sh        # Linux/Mac image builder
│   └── build-push.ps1       # Windows image builder
├── tests/
│   ├── test_data/            # Test data files (images, JSON, expected outputs)
│   │   ├── TestData.txt      # Test cases with expected outputs
│   │   ├── *.png             # Test images
│   │   └── *.json            # Test puzzle files
│   ├── test_sudoku.py        # Core solver tests
│   ├── test_grid_stub.py    # Grid detection tests
│   ├── test_all_images.py   # OCR comprehensive tests
│   └── test_sudoku_json.py  # JSON validation tests
├── examples/
│   ├── examples_data/        # Example data files (images, JSON puzzles)
│   │   ├── *.png             # Example Sudoku images
│   │   └── *.json            # Example puzzle files
│   ├── demo.py               # Basic solver demo
│   ├── end_to_end_example.py # Complete pipeline demo
│   └── sample_puzzles.py     # Test puzzles
├── docs/
│   ├── IMPROVEMENTS.md       # Detailed improvement documentation
│   ├── application_flow.md   # Web app architecture documentation
│   └── COMMAND_LINE_USAGE.md # Command-line usage guide
├── pyproject.toml            # Unified project configuration
└── README.md                 # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- For OCR features: Tesseract OCR engine

### Setup

1. Clone the repository:
```bash
git clone https://github.com/wmurphy41/SudokuSolver.git
cd SudokuSolver
```

2. Install dependencies:

**Core solver only (recommended for most users):**
```bash
pip install sudoku-solver
```

**With OCR capabilities:**
```bash
pip install sudoku-solver[ocr]
```

**Development setup:**
```bash
pip install sudoku-solver[dev]
```

**Everything:**
```bash
pip install sudoku-solver[all]
```

3. For OCR features, install Tesseract OCR:
   - **Windows**: `choco install tesseract`
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

## Quick Start

### Command-Line Solving

**Solve from JSON file:**
```bash
# Navigate to project root
cd SudokuSolver

# Solve a puzzle from JSON file
python src/cli_solver.py --file examples/examples_data/NYT-EASY-2025-09-27_puzzle.json

# With detailed debug output
python src/cli_solver.py --file puzzle.json --debug 2

# Save solution to file
python src/cli_solver.py --file puzzle.json --output solution.json
```

**For more CLI usage examples, see [docs/COMMAND_LINE_USAGE.md](docs/COMMAND_LINE_USAGE.md)**

### Basic Sudoku Solving

```python
from src.sudoku_solver import solve_sudoku

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

### Advanced Solving with Metrics

```python
from src.sudoku_solver import SudokuSolver

# Create solver with debug output
solver = SudokuSolver(puzzle, debug_level=2)
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

### Step-by-Step Solving

```python
from src.sudoku_solver import SudokuSolver
from typing import Literal

# Create solver for step-by-step solving
solver = SudokuSolver(puzzle, debug_level=2)

# Solve step by step - one technique per call
state: Literal["solving", "solved", "stuck"]
change_record: dict

while True:
    state, change_record = solver.step_solve()
    
    technique = change_record.get("technique", "unknown")
    cells_filled = len(change_record.get("cells_filled", []))
    candidates_pruned = len(change_record.get("candidates_pruned", []))
    
    print(f"Applied {technique}: {cells_filled} cells filled, {candidates_pruned} candidates pruned")
    
    if state == "solved":
        print("Puzzle solved!")
        break
    elif state == "stuck":
        print("Stuck - no progress made in full pass")
        break
    # Continue if state == "solving"

# Or force display even in silent mode
solver.print_grid()  # Always shows grid
solver.print_candidates()  # Always shows candidates
```

### Silent Mode for Batch Processing

```python
from src.sudoku_solver import solve_sudoku

# Silent mode - no output, perfect for batch processing
solved = solve_sudoku(puzzle, debug_level=0)
print(f"Puzzle solved: {solved}")  # Only this output will be shown
```

### Loading Puzzles from JSON

```python
from src.sudoku_models import SudokuPuzzle

# Load puzzle from JSON file
puzzle_obj = SudokuPuzzle("examples/examples_data/NYT-EASY-2025-09-27_puzzle.json")
print(f"Loaded puzzle with {puzzle_obj.get_empty_cells_count()} empty cells")
print(f"Grid preview:\n{puzzle_obj}")

# Solve the loaded puzzle
solver = SudokuSolver(puzzle_obj.puzzle)
solved = solver.solve()
```

### Complete End-to-End Pipeline (OCR + Solving)

```python
# Run the complete pipeline example
python examples/end_to_end_example.py
```

This will process a Sudoku image and perform the complete workflow:
1. Load Sudoku image
2. Extract grid using OCR
3. Save grid as JSON
4. Create SudokuPuzzle from JSON
5. Solve using SudokuSolver
6. Display results and verify solution

### OCR Processing Only

```bash
# Process a Sudoku image with OCR
python -m src.sudoku_ocr.cli --image examples/examples_data/NYT-EASY-2025-09-27.png --out output
```

### OCR Advanced Options

```bash
python -m src.sudoku_ocr.cli --image examples/examples_data/NYT-EASY-2025-09-27.png --out output \
    --size 450 \
    --pad 4 \
    --apply-clahe \
    --saving-cells \
    --debug
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
- `debug_level`: Debug output level (0=silent, 1=informational, 2=basic, 3=detailed)

**Raises:**
- `SudokuError`: If puzzle format is invalid

#### Methods

- `solve() -> bool`: Solve the puzzle completely and return success status
- `step_solve() -> Tuple[Literal["solving", "solved", "stuck"], Dict[str, Any]]`: Perform one solving technique and return state and change record
  - Returns: Tuple of (state, change_record) where:
    - `state` is "solved" if puzzle is solved, "stuck" if no progress in full pass, or "solving" otherwise
    - `change_record` contains technique name, cells_filled list, and candidates_pruned list
- `get_candidate_grid() -> List[List[List[int]]]`: Return 9×9 grid of candidate lists for each cell
- `get_change_history() -> List[Dict[str, Any]]`: Get complete list of all change records made during solving
- `get_last_change() -> Optional[Dict[str, Any]]`: Get the most recent change record
- `print_grid(force_print: bool = True)`: Display the current state of the grid
- `print_candidates(force_print: bool = True)`: Show candidates for all cells (debugging aid)
- `count_empty_cells() -> int`: Count remaining empty cells

#### Properties

- `metrics`: `SolvingMetrics` object tracking solving performance
- `debug_level`: Current debug output level

### SudokuPuzzle Class

Represents a Sudoku puzzle loaded from a JSON file with validation.

#### Constructor
```python
SudokuPuzzle(filename: str)
```

**Parameters:**
- `filename`: Path to JSON file containing the Sudoku puzzle

**Raises:**
- `ValueError`: If file doesn't exist, is malformed, or contains invalid data
- `FileNotFoundError`: If the file path doesn't exist

#### Methods

- `get_empty_cells_count() -> int`: Count the number of empty cells (zeros)
- `is_solved() -> bool`: Check if the puzzle is completely filled

#### Properties

- `puzzle`: `List[List[int]]` containing the loaded grid
- `filename`: Original filename

### Convenience Functions

- `solve_sudoku(puzzle: List[List[int]], debug_level: int = 0) -> bool`: Simple solving function

### Debug Levels

The solver supports four debug levels for different output scenarios:

| Level | Name | Behavior |
|-------|------|----------|
| **0** | **Silent** | No output at all - perfect for batch processing |
| **1** | **Informational** | Shows grids and summaries only |
| **2** | **Basic** | Shows informational output plus solving technique details |
| **3** | **Detailed** | Shows all output including detailed debugging information |

### Print Function Options

Both `print_grid()` and `print_candidates()` support a `force_print` parameter:

- `force_print=True` (default): Always displays output regardless of debug level
- `force_print=False`: Respects debug level settings (silent when debug_level=0)

## Web Application

The SudokuSolver includes a modern web interface for solving puzzles through a browser.

### Quick Start (Local Development)

**Start Backend:**
```bash
cd web/backend
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

**Start Frontend (separate terminal):**
```bash
cd web/frontend
npm install
npm run dev
```

Access at: `http://localhost:5173`

### Docker Deployment

**Local Testing:**
```bash
cd web
docker compose up --build
```

Access at: `http://localhost`

**Production Deployment:**
See [web/README-deploy-images.md](web/README-deploy-images.md) for complete deployment instructions using pre-built Docker images.

### API Endpoints

**Health Check:**
- `GET /api/healthz` - Returns `{"status": "ok"}`

**Solve Puzzle (Full Solve):**
- `POST /api/solve` - Accepts `{"grid": number[][], "debug_level": number}`, returns `{"solution": number[][] | null, "success": boolean, "message": "string"}`
- **Fully integrated** with core SudokuSolver engine
- Captures solver output based on debug level
- Returns partial progress even on failure

**Session-Based Stepwise Solving:**
- `POST /api/sessions` - Creates a new solving session, accepts `{"grid": number[][], "debug_level": number}`, returns `{"session_id": "string", "candidates": CandidateGrid | null}`
- `POST /api/sessions/{session_id}/step` - Applies one solving technique, returns:
  - `solution: Grid | null` - Updated grid state
  - `success: boolean` - True if puzzle is solved
  - `message: string` - Status message
  - `state: "solving" | "solved" | "stuck"` - Current solving state
  - `candidates: CandidateGrid | null` - 9×9 grid of candidate lists for each cell
  - `changes: ChangeRecord[] | null` - List of change records (technique, cells_filled, candidates_pruned)
- `DELETE /api/sessions/{session_id}` - Deletes a solving session, returns `{"deleted": boolean}`
- **Fully integrated** with SudokuSolver engine using single-technique-per-step execution
- **Redis-backed** session storage for persistent solver state between steps
- **Change tracking** records all modifications made by each solving technique

### Features

- ✅ **Modern UI**: React + TypeScript single-page application with grid visualization
- ✅ **Type-Safe API**: FastAPI with Pydantic validation for 9×9 grids
- ✅ **Grid Display**: Visual 9×9 tables with 3×3 box boundaries for original and solution
- ✅ **Sample Puzzles**: One-click loading of Empty, Easy, Medium, and Hard example puzzles
- ✅ **Debug Levels**: Four levels (0-3) to control solver output verbosity
- ✅ **Smart Error Handling**: Distinguishes invalid input, network errors, and solver failures
- ✅ **Result Display**: Shows original puzzle, solution grid, and captured solver logs
- ✅ **Accessibility**: ARIA labels and live regions for screen readers
- ✅ **Containerized**: Docker-based deployment with Nginx reverse proxy
- ✅ **Fully Integrated**: Backend now uses actual SudokuSolver engine with log capture
- ✅ **Stepwise Solving**: Fully integrated step-by-step solving with one technique per step
- ✅ **Candidate Display**: Visual 3×3 mini-grid showing candidate lists in empty cells
- ✅ **Show Original Toggle**: Toggle between original puzzle and current solved state
- ✅ **Change Tracking**: Detailed records of cells filled and candidates pruned per technique
- ✅ **Three-State Solving**: Clear solving states (solving/solved/stuck) with pass progress tracking
- ✅ **Session Management**: Create, step through, and delete solving sessions via REST API
- ✅ **Mobile Responsive**: Optimized UI for iPhone SE and mobile devices

### Documentation

- [Web Application Overview](web/README.md)
- [Application Flow](docs/application_flow.md)
- [Deployment Guide](web/README-deploy-images.md)
- [Frontend README](web/frontend/README.md)

## Running Examples

### Demo Script
```bash
python examples/demo.py
```

### End-to-End Example
```bash
python examples/end_to_end_example.py
```

### Test Suite
```bash
python tests/test_sudoku.py
```

### OCR Tests
```bash
python tests/test_all_images.py
```

### Sample Puzzles
```python
from examples.sample_puzzles import matrix_easy_1, matrix_hard_1
from src.sudoku_solver import solve_sudoku

# Try different difficulty levels
print("Easy puzzle:", solve_sudoku(matrix_easy_1))
print("Hard puzzle:", solve_sudoku(matrix_hard_1))
```

## Algorithm Details

### Solving Engine

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

### OCR Pipeline

1. **Preprocessing**: 
   - Convert BGR to grayscale
   - Apply Gaussian blur
   - Adaptive thresholding
   - Morphological operations

2. **Grid Detection**:
   - Find largest contour
   - Approximate to quadrilateral
   - Apply perspective transformation
   - Warp to square grid

3. **Cell Extraction**:
   - Split warped grid into 9×9 cells
   - Apply padding and resizing
   - Ensure minimum cell size (32×32)

4. **Digit Recognition**:
   - Multi-method Tesseract OCR approach
   - Enhanced preprocessing with larger image sizes
   - Alternative preprocessing methods (Otsu thresholding, simple thresholding)
   - Multiple PSM modes for robust recognition
   - Progressive confidence thresholds for fallback methods

## OCR Performance

Current performance on test dataset:

| Image | Accuracy | Precision | Recall | F1-Score | Status |
|-------|----------|-----------|--------|----------|--------|
| NYT-EASY-2025-09-27 | 100% | 100% | 100% | 100% | ✅ Perfect |
| NYT-MED-2025-09-27 | 0% | 0% | 0% | 0% | ⚠️ Challenging |
| NYT-HARD-2025-09-27 | 100% | 100% | 100% | 100% | ✅ Perfect |
| NYT-EASY-2025-09-28 | 100% | 100% | 100% | 100% | ✅ Perfect |
| NYT-MED-2025-09-28 | 100% | 100% | 100% | 100% | ✅ Perfect |
| NYT-HARD-2025-09-28 | 100% | 100% | 100% | 100% | ✅ Perfect |

**Overall Performance:**
- **Overall Accuracy**: 83.4%
- **Overall Precision**: 91.2%
- **Overall Recall**: 83.4%
- **Overall F1-Score**: 87.2%
- **Success Rate**: 5 out of 6 images achieve perfect 100% accuracy

## Error Handling

The solver includes comprehensive error handling:

```python
from src.sudoku_models import SudokuError

try:
    solver = SudokuSolver(invalid_puzzle)
except SudokuError as e:
    print(f"Invalid puzzle: {e}")
```

Common error conditions:
- Invalid puzzle dimensions (not 9x9)
- Invalid cell values (not 0-9)
- Malformed input data
- JSON parsing errors
- File not found errors

## Testing

The project includes comprehensive test suites:

```bash
# Core solver tests
python tests/test_sudoku.py

# OCR functionality tests
python tests/test_all_images.py

# Grid detection tests
python tests/test_grid_stub.py

# JSON validation tests
python tests/test_sudoku_json.py
```

## Contributing

This project follows modern Python best practices:

- Type hints for all functions and methods
- Comprehensive docstrings
- Error handling with custom exceptions
- Clean separation of concerns
- Extensive testing
- Modular architecture

## License

Copyright © 2022 [William A. Murphy](https://github.com/wmurphy41).

This project is [MIT](https://spdx.org/licenses/MIT.html) licensed.

## Changelog

For detailed version history and release notes, see [CHANGELOG.md](CHANGELOG.md).

### Latest Release (v2025.11.28)

**Major Features:**
- **Enhanced Step Solve Mode**: Single-technique-per-step execution with three-state system (solving/solved/stuck)
- **Change Tracking**: Comprehensive records of all modifications (cells filled, candidates pruned) per technique
- **Candidate Display**: Visual 3×3 mini-grid showing candidate lists in empty cells for enhanced solving visibility
- **Show Original Toggle**: Toggle between original puzzle and current solved state in both Full and Step modes
- **Mobile Responsive**: Optimized UI scaling for iPhone SE and mobile devices

**Improvements:**
- Improved message formatting with status-first structure
- Consistent message box styling across both solve modes
- Removed debug mode selection UI (still supported via API)
- Enhanced stuck state detection through pass progress tracking

See [CHANGELOG.md](CHANGELOG.md) for complete change history.

### Previous Improvements
- Complete rewrite with modern Python practices
- Added comprehensive type hints and documentation
- Implemented advanced solving techniques
- Enhanced error handling and validation
- Created extensive test suite
- Optimized performance and memory usage
- Integrated OCR capabilities for end-to-end pipeline
- Modular architecture with separated concerns
- Unified configuration and packaging

See [docs/IMPROVEMENTS.md](docs/IMPROVEMENTS.md) for detailed improvement documentation.