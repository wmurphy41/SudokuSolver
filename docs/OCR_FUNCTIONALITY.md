# Sudoku OCR Functionality Documentation

This document describes the OCR (Optical Character Recognition) pipeline for extracting Sudoku puzzles from images, covering all modules in the `src/sudoku_ocr/` directory.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Pipeline Stages](#pipeline-stages)
3. [Module Details](#module-details)
4. [Complete Pipeline](#complete-pipeline)
5. [Usage Examples](#usage-examples)
6. [Performance and Limitations](#performance-and-limitations)

---

## Architecture Overview

The OCR system processes Sudoku puzzle images through a multi-stage pipeline:

```
Input Image (BGR)
    ↓
[1] Preprocessing (preprocess.py)
    ├─ Convert to grayscale
    ├─ Apply CLAHE (optional)
    ├─ Gaussian blur
    ├─ Adaptive thresholding
    └─ Morphological operations
    ↓
Binary Image
    ↓
[2] Grid Detection (grid.py)
    ├─ Find largest contour
    ├─ Approximate to quadrilateral
    ├─ Validate quadrilateral
    └─ Order corners
    ↓
4 Corner Points
    ↓
[3] Perspective Correction (grid.py)
    ├─ Calculate transformation matrix
    └─ Warp to square
    ↓
Warped Square Grid (450×450)
    ↓
[4] Cell Extraction (cells.py)
    ├─ Split into 9×9 cells
    ├─ Apply inner padding
    └─ Ensure minimum cell size
    ↓
81 Cell Images
    ↓
[5] Digit Recognition (ocr.py)
    ├─ Preprocess each cell
    ├─ Run Tesseract OCR
    ├─ Multiple fallback methods
    └─ Confidence thresholding
    ↓
9×9 Grid of Digits (0-9)
```

---

## Pipeline Stages

### Stage 1: Image Preprocessing

**Module:** `preprocess.py`

Converts input BGR image to binary format optimized for grid detection.

#### `to_binary(img_bgr, apply_clahe=False) -> np.ndarray`

**Process:**
1. **Grayscale Conversion**: `cv2.cvtColor(BGR2GRAY)`
2. **Optional CLAHE**: Contrast Limited Adaptive Histogram Equalization
   - Improves contrast in poorly lit images
   - `clipLimit=2.0`, `tileGridSize=(8,8)`
3. **Gaussian Blur**: `(3,3)` kernel to reduce noise
4. **Adaptive Thresholding**: `ADAPTIVE_THRESH_GAUSSIAN_C`
   - Block size: 11
   - C constant: 2
   - Converts to binary (0/255)
5. **Inversion**: Digits/grid become white on black background
6. **Morphological Operations**:
   - Opening: Removes small noise (2×2 kernel)
   - Closing: Fills small gaps (2×2 kernel)

**Output:** Binary image (uint8, 0/255) with white grid/digits on black background

#### `largest_contour(binary) -> np.ndarray | None`

Finds the largest external contour in the binary image.

**Algorithm:**
1. Use `cv2.findContours()` with `RETR_EXTERNAL` mode
2. Select contour with maximum area
3. Return None if no contours found

**Use Case:** Typically finds the outer Sudoku grid boundary

---

### Stage 2: Grid Detection

**Module:** `grid.py`

Detects and validates the Sudoku grid quadrilateral.

#### `approx_to_quad(cnt) -> np.ndarray | None`

Approximates a contour to a quadrilateral using Douglas-Peucker algorithm.

**Algorithm:**
1. Calculate epsilon: `0.02 * perimeter`
2. Apply `cv2.approxPolyDP()` to simplify contour
3. Check if result has exactly 4 points
4. Validate quadrilateral shape

**Validation (`_is_valid_quad`):**
- Must be convex (convex hull has 4 points)
- Aspect ratio: 0.8 to 1.2 (roughly square)
- Minimum area: 1000 pixels
- Width and height must be positive

**Returns:** 4 corner points as (4, 2) array, or None if invalid

#### `order_corners(pts4) -> np.ndarray`

Orders 4 corner points in standard order: top-left, top-right, bottom-right, bottom-left.

**Algorithm:**
1. Calculate sum and difference of coordinates for each point
2. **Top-left**: Smallest sum (closest to origin)
3. **Bottom-right**: Largest sum (farthest from origin)
4. **Top-right**: Smallest difference (x ≈ y, both large)
5. **Bottom-left**: Largest difference (one large, one small)

**Returns:** Ordered array (4, 2) in TL, TR, BR, BL order

#### `find_and_warp(img_bgr, size=450, apply_clahe=False) -> dict`

Complete pipeline from input image to warped grid.

**Process:**
1. Convert to binary using `to_binary()`
2. Find largest contour using `largest_contour()`
3. Approximate to quadrilateral using `approx_to_quad()`
4. Order corners using `order_corners()`
5. Warp to square using `warp_to_square()`

**Returns:** Dictionary with:
- `binary`: Binary image
- `contour_mask`: Filled contour mask
- `quad`: Detected quadrilateral
- `warped`: Warped square grid (BGR)

**Raises:** `GridNotFoundError` if any step fails

#### `warp_to_square(img_bgr, pts4, size=450) -> np.ndarray`

Applies perspective transformation to create a perfect square view.

**Algorithm:**
1. Define target square: `[(0,0), (size,0), (size,size), (0,size)]`
2. Calculate transformation matrix: `cv2.getPerspectiveTransform()`
3. Apply transformation: `cv2.warpPerspective()`

**Output:** Square BGR image (size×size pixels)

---

### Stage 3: Cell Extraction

**Module:** `cells.py`

Splits the warped grid into 81 individual cells.

#### `split_into_cells(warped_bgr, pad=4) -> list[np.ndarray]`

Splits 450×450 square into 9×9 grid of cells.

**Process:**
1. **Calculate cell size**: `450 // 9 = 50 pixels per cell`
2. **For each cell (row 0-8, col 0-8):**
   - Calculate boundaries: `y1, y2, x1, x2`
   - Extract cell region from warped image
   - **Apply inner padding**: Remove `pad` pixels from each edge
     - Avoids grid lines in cell images
     - Ensures padding doesn't exceed cell size
   - **Ensure minimum size**: Resize if cell < 32×32
     - Uses `cv2.INTER_CUBIC` for upscaling
     - Only resizes if cell has content (variance > 10)
     - Creates white cell if completely empty

**Returns:** List of 81 BGR cell images in row-major order

**Row-Major Order:**
```
Cell 0:  row 0, col 0
Cell 1:  row 0, col 1
...
Cell 8:  row 0, col 8
Cell 9:  row 1, col 0
...
Cell 80: row 8, col 8
```

**Edge Cases Handled:**
- Empty cells → White 32×32 image
- Very small cells → Upscaled to minimum 32×32
- Padding exceeds cell size → Adjusted automatically

---

### Stage 4: Digit Recognition

**Module:** `ocr.py`

Recognizes digits in individual cell images using Tesseract OCR.

#### `preprocess_cell(cell_bgr) -> np.ndarray`

Preprocesses a single cell for optimal OCR recognition.

**Process:**
1. **Convert to grayscale** (if BGR)
2. **Resize if needed**: Ensure minimum 80×80 pixels
   - Tesseract works better with larger text
   - Uses `cv2.INTER_CUBIC` for upscaling
3. **Gaussian blur**: `(3,3)` kernel to smooth
4. **Adaptive thresholding**: `ADAPTIVE_THRESH_GAUSSIAN_C`
   - Block size: 15
   - C constant: 2
   - Inverted: Digits are white on black
5. **Morphological operations**:
   - Opening: Remove noise (2×2 kernel)
   - Closing: Fill gaps (3×3 kernel)
6. **Final size check**: Ensure minimum 64×64

**Output:** Binary image optimized for Tesseract

#### `ocr_cell(cell_bgr, conf_thresh=0.45) -> int`

Recognizes a single digit using multiple fallback methods.

**Multi-Method Approach:**

**Method 1: Enhanced Preprocessing**
- Uses `preprocess_cell()` with standard parameters
- Confidence threshold: `conf_thresh` (default 0.45)

**Method 2: Alternative Preprocessing**
- Larger size (120×120)
- Otsu thresholding instead of adaptive
- Lower confidence threshold: `conf_thresh * 0.8`

**Method 3: Simple Preprocessing**
- Standard size (80×80)
- Simple threshold (127)
- Even lower confidence: `conf_thresh * 0.7`

**Tesseract Configuration:**

Uses multiple PSM (Page Segmentation Mode) configurations:
- `--psm 10`: Single character (best for isolated digits)
- `--psm 8`: Single word
- `--psm 7`: Single text line
- `--psm 6`: Single uniform block

**Algorithm:**
1. Try Method 1 with all PSM modes
2. If no result, try Method 2 with all PSM modes
3. If still no result, try Method 3 with all PSM modes
4. Select best result based on confidence score
5. Return digit (1-9) if confidence ≥ threshold, else 0

**Returns:** Digit (1-9) or 0 if not recognized

#### `ocr_cells(cells_bgr, conf_thresh=0.45) -> List[int]`

Processes all 81 cells and returns recognized digits.

**Process:**
1. Iterate through all 81 cells
2. Call `ocr_cell()` for each cell
3. Print progress indicator (row-by-row)
4. Return flat list of 81 digits (0-9)

**Returns:** List of 81 integers in row-major order

#### `to_grid(flat) -> List[List[int]]`

Converts flat list of 81 digits to 9×9 grid.

**Algorithm:**
```python
for i in range(9):
    row = flat[i * 9 : (i + 1) * 9]
    grid.append(row)
```

**Returns:** 9×9 grid as list of lists

---

## Complete Pipeline

### End-to-End Function

```python
from sudoku_ocr import find_and_warp, split_into_cells, ocr_cells, to_grid
import cv2

# Load image
img_bgr = cv2.imread("sudoku_puzzle.png")

# Stage 1-3: Preprocess, detect, and warp
result = find_and_warp(img_bgr, size=450, apply_clahe=False)
warped = result['warped']

# Stage 4: Extract cells
cells = split_into_cells(warped, pad=4)

# Stage 5: Recognize digits
digits = ocr_cells(cells, conf_thresh=0.45)

# Convert to grid
grid = to_grid(digits)
```

### Error Handling

The pipeline raises `GridNotFoundError` if:
- Input image is empty or invalid
- No contours found in binary image
- Contour cannot be approximated to valid quadrilateral
- Perspective transformation fails

Individual cell OCR failures return 0 (empty cell) without raising exceptions.

---

## Module Details

### preprocess.py

**Functions:**
- `to_binary()`: Main preprocessing function
- `largest_contour()`: Find largest external contour
- `preprocess_image()`: Legacy compatibility function
- `enhance_contrast()`: CLAHE application
- `remove_noise()`: Connected component filtering

### grid.py

**Functions:**
- `approx_to_quad()`: Contour to quadrilateral approximation
- `order_corners()`: Corner point ordering
- `warp_to_square()`: Perspective transformation
- `find_and_warp()`: Complete detection and warping pipeline
- `create_quad_overlay()`: Visualization helper
- `find_grid()`, `warp_perspective()`: Legacy compatibility

**Exceptions:**
- `GridNotFoundError`: Raised when grid detection fails

### cells.py

**Functions:**
- `split_into_cells()`: Main cell extraction function
- `extract_cells()`: Legacy compatibility
- `add_margin()`: Add padding around cells
- `preprocess_cell()`: Cell preprocessing (legacy)
- `is_empty_cell()`: Empty cell detection
- `center_digit()`: Digit centering (not currently used)

### ocr.py

**Functions:**
- `preprocess_cell()`: Cell preprocessing for OCR
- `ocr_cell()`: Single cell digit recognition
- `ocr_cells()`: Batch processing of all cells
- `to_grid()`: Convert flat list to 9×9 grid
- `print_grid()`: Pretty-print grid
- `validate_grid()`: Grid structure validation
- `get_tesseract_version()`: Version information
- `test_tesseract_installation()`: Installation test

**Internal Functions:**
- `_tesseract_ocr()`: Core Tesseract wrapper
- `_alternative_preprocessing()`: Fallback method 2
- `_simple_preprocessing()`: Fallback method 3

---

## Usage Examples

### Basic OCR Pipeline

```python
import cv2
from sudoku_ocr import find_and_warp, split_into_cells, ocr_cells, to_grid

# Load image
img = cv2.imread("puzzle.png")

# Detect and warp grid
result = find_and_warp(img, size=450)
warped = result['warped']

# Extract cells
cells = split_into_cells(warped, pad=4)

# Recognize digits
digits = ocr_cells(cells)

# Convert to grid
grid = to_grid(digits)
```

### With CLAHE Enhancement

```python
# For poorly lit or low-contrast images
result = find_and_warp(img, size=450, apply_clahe=True)
```

### Custom Confidence Threshold

```python
# More strict recognition (fewer false positives, more empty cells)
digits = ocr_cells(cells, conf_thresh=0.60)

# More lenient recognition (more digits recognized, possible errors)
digits = ocr_cells(cells, conf_thresh=0.30)
```

### Using CLI Module

```python
from sudoku_ocr.cli import main
import sys

# Run CLI with arguments
sys.argv = ['ocr_cli', '--image', 'puzzle.png', '--out', 'output']
main()
```

---

## Performance and Limitations

### Performance Characteristics

**Typical Processing Times** (on modern hardware):
- Preprocessing: < 100ms
- Grid detection: < 50ms
- Perspective warping: < 50ms
- Cell extraction: < 20ms
- OCR (81 cells): 2-5 seconds (Tesseract is the bottleneck)

**Accuracy** (from test results):
- Easy puzzles: ~100% accuracy
- Medium puzzles: ~80-100% accuracy
- Hard puzzles: ~80-100% accuracy
- Overall: 83.4% accuracy, 91.2% precision

### Limitations

1. **Image Quality Requirements:**
   - Grid must be clearly visible
   - Minimal perspective distortion
   - Good lighting and contrast
   - No overlapping objects

2. **Grid Detection:**
   - Requires clear grid boundaries
   - May fail with heavily distorted images
   - Needs minimum resolution (~300×300 pixels)

3. **OCR Accuracy:**
   - Depends on font style and clarity
   - May confuse similar digits (6/8, 1/7)
   - Handwritten digits not supported
   - Requires Tesseract installation

4. **Cell Extraction:**
   - Assumes perfect 9×9 grid structure
   - May fail with irregular grids
   - Padding may cut off digits if too large

### Error Handling

- **GridNotFoundError**: Raised when grid cannot be detected
- **ValueError**: Raised for invalid input parameters
- **OCR Errors**: Return 0 (empty cell) instead of raising exceptions
- **Tesseract Errors**: Caught and handled gracefully

### Best Practices

1. **Image Preprocessing:**
   - Use high-resolution images (≥ 600×600)
   - Ensure good lighting and contrast
   - Use `apply_clahe=True` for low-contrast images

2. **Grid Detection:**
   - Ensure grid is largest object in image
   - Remove background clutter if possible
   - Use images with clear grid boundaries

3. **OCR Tuning:**
   - Adjust `conf_thresh` based on image quality
   - Higher threshold (0.6) for clean images
   - Lower threshold (0.3) for noisy images
   - Test with sample images to find optimal value

4. **Validation:**
   - Always validate extracted grid structure
   - Check for reasonable number of filled cells (17-30 typical)
   - Verify grid can be solved by solver

---

## Tesseract Configuration

### Installation

**Windows:**
```bash
choco install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Path Configuration

The module hardcodes Tesseract path for Windows Chocolatey installation:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

For other installations, modify this path or set environment variable.

### Testing Installation

```python
from sudoku_ocr import test_tesseract_installation

if test_tesseract_installation():
    print("Tesseract is working correctly")
else:
    print("Tesseract installation issue")
```

---

## Future Enhancements

Potential improvements:
1. **Machine Learning**: Train custom digit recognition model
2. **Better Preprocessing**: Advanced image enhancement techniques
3. **Grid Line Detection**: More robust grid detection using line detection
4. **Multi-Scale Processing**: Process at multiple resolutions
5. **Confidence Aggregation**: Combine results from multiple methods

