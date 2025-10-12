# SudokuSolver

A comprehensive Python Sudoku solver with advanced solving techniques and OCR capabilities for extracting and solving Sudoku puzzles from images.

## Features

### Core Solving Engine
- **Naked Singles**: Fill cells with only one candidate
- **Hidden Singles**: Fill cells where a value can only go in one position in a constraint group
- **Intersection Removal**: Advanced constraint propagation techniques
- **Naked Groups**: Handle pairs, triples, and quads of candidates
- **Hidden Groups**: Advanced group-based solving techniques

### Web Application (Beta)
- **React + TypeScript Frontend**: Modern single-page application with responsive design
- **FastAPI Backend**: RESTful API with automatic validation and documentation
- **Real-time Solving**: Submit puzzles and receive solutions via API
- **Docker Deployment**: Containerized architecture with Nginx reverse proxy
- **Result Display**: Shows success/fail status, solution, and detailed messages
- **Note**: Frontend UI currently echoes puzzle input; integration with core SudokuSolver logic is in progress

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
│   ├── IMPROVEMENTS.md      # Detailed improvement documentation
│   └── application_flow.md  # Web app architecture documentation
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

# Create solver for step-by-step solving
solver = SudokuSolver(puzzle, debug_level=2)

# Solve step by step
while solver.count_empty_cells() > 0:
    step_solved = solver.step_solve()
    print(f"Step completed. Solved: {step_solved}")
    
    if step_solved:
        print("Puzzle solved!")
        break
    elif solver.metrics.solve_loops > 50:  # Prevent infinite loops
        print("Too many steps, stopping")
        break

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

- `solve() -> bool`: Solve the puzzle and return success status
- `step_solve() -> bool`: Perform one solving step and return success status
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

**Solve Puzzle:**
- `POST /api/solve` - Accepts `{"puzzle": "string"}`, returns `{"solution": "string", "success": boolean, "message": "string"}`
- **Note**: Currently echoes input; integration with core SudokuSolver logic in progress

### Features

- ✅ **Modern UI**: React + TypeScript single-page application
- ✅ **Type-Safe API**: FastAPI with Pydantic validation
- ✅ **Result Display**: Shows success/fail status, solution, and detailed messages with all three backend response fields
- ✅ **Error Handling**: Network errors and validation errors properly displayed
- ✅ **Accessibility**: ARIA labels and live regions for screen readers
- ✅ **Containerized**: Docker-based deployment with Nginx reverse proxy
- 🚧 **In Progress**: Integration with core SudokuSolver backend logic

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

### Recent Improvements (Latest)
- **Project Organization**: Reorganized test and example data files into dedicated subdirectories
  - Tests now use `tests/test_data/` for all test data files (images, JSON, expected outputs)
  - Examples now use `examples/examples_data/` for all data files (images, JSON puzzles)
  - Improved project structure with clear separation of code and data files
- **Enhanced Debug System**: Added 4-level debug system (silent, informational, basic, detailed)
- **Step-by-Step Solving**: New `step_solve()` method for interactive puzzle solving
- **Flexible Print Functions**: `print_grid()` and `print_candidates()` with `force_print` parameter
- **Silent Mode**: Complete output suppression for batch processing
- **Improved API**: Better control over solver output and behavior

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