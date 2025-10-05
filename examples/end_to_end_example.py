#!/usr/bin/env python3
"""
End-to-End Example: Image → OCR → JSON → SudokuPuzzle → SudokuSolver

This example script demonstrates the complete SudokuSolver pipeline:
1. Load a Sudoku image from the examples directory
2. Process it through OCR to extract grid
3. Save grid as JSON file
4. Create SudokuPuzzle from JSON
5. Solve using SudokuSolver
6. Display results and verify solution

Usage: python end_to_end_example.py

This script should be run from the examples directory and will process
the NYT puzzle images in the same directory.
"""

import sys
import json
import cv2
from pathlib import Path

# Add src to path for imports (since we're in examples directory now)
sys.path.append('../src')

from sudoku_models import SudokuPuzzle
from sudoku_solver import SudokuSolver, solve_sudoku
from sudoku_ocr import find_and_warp, split_into_cells, ocr_cells, to_grid


def run_end_to_end_test(image_path: str, output_dir: str = "e2e_output"):
    """
    Run complete end-to-end test pipeline.
    
    Args:
        image_path: Path to input Sudoku image
        output_dir: Directory for intermediate outputs
    """
    print("End-to-End Sudoku Pipeline Test")
    print("=" * 50)
    
    # Step 1: Check image exists
    image_file = Path(image_path)
    if not image_file.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    print(f"Step 1: Loading image: {image_file.name}")
    
    # Step 2: Load and process image through OCR pipeline
    print("Step 2: Processing image through OCR pipeline...")
    
    # Load the image
    img_bgr = cv2.imread(str(image_file))
    if img_bgr is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    print(f"   Image loaded: {img_bgr.shape}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    try:
        # Process through OCR pipeline
        result = find_and_warp(img_bgr)
        warped_img = result['warped']
        print(f"   Success: Grid detection successful: {warped_img.shape}")
        
        cells = split_into_cells(warped_img, pad=6)
        print(f"   Success: Cell extraction successful: {len(cells)} cells")
        
        # Perform OCR on cells
        digit_strings = ocr_cells(cells)
        print(f"   Success: OCR completed: {len(digit_strings)} cells processed")
        
        # Convert to grid
        grid = to_grid(digit_strings)
        print(f"   Success: Grid conversion successful")
        
    except Exception as e:
        print(f"   Error: OCR processing failed: {e}")
        return False
    
    # Step 3: Save grid as JSON file
    print("Step 3: Saving grid as JSON...")
    
    json_file = output_path / f"{image_file.stem}.json"
    with open(json_file, 'w') as f:
        json.dump(grid, f, indent=2)
    
    print(f"   Success: JSON saved: {json_file}")
    
    # Step 4: Create SudokuPuzzle from JSON
    print("Step 4: Creating SudokuPuzzle from JSON...")
    
    try:
        puzzle = SudokuPuzzle(str(json_file))
        print(f"   Success: SudokuPuzzle created successfully")
        print(f"   Empty cells: {puzzle.get_empty_cells_count()}")
        print(f"   Grid preview:")
        
        # Display grid preview
        grid_lines = repr(puzzle).split('\n')
        for i, line in enumerate(grid_lines[:3]):  # Show first 3 rows
            print(f"      {line}")
        print("      ...")
        
        for i, line in enumerate(grid_lines[-3:]):  # Show last 3 rows
            print(f"      {line}")
            
    except Exception as e:
        print(f"   Error: SudokuPuzzle creation failed: {e}")
        return False
    
    # Step 5: Create SudokuSolver and solve
    print("Step 5: Solving puzzle with SudokuSolver...")
    
    try:
        solver = SudokuSolver(puzzle.puzzle, debug_level=0)  # Reduced debug output
        print("   Success: SudokuSolver created successfully")
        
        print("   Solving puzzle...")
        solved = solver.solve()
        
        if solved:
            print(f"   Success: Puzzle solved successfully!")
            print(f"   Solve loops: {solver.metrics.solve_loops}")
            print(f"   Techniques used:")
            print(f"     - Naked singles: {solver.metrics.fill_only_candidate}")
            print(f"     - Hidden singles: {solver.metrics.fill_only_option}")
            print(f"     - Intersection removal: {solver.metrics.prune_gotta_be_here}")
            print(f"     - Naked groups: {solver.metrics.prune_magic_pairs}")
        else:
            print(f"   Warning: Puzzle could not be solved with current techniques")
            
    except Exception as e:
        print(f"   Error: Solving failed: {e}")
        return False
    
    # Step 6: Save solution
    print("Step 6: Saving solution...")
    
    solution_file = output_path / f"{image_file.stem}_solution.json"
    with open(solution_file, 'w') as f:
        # Convert SudokuCell objects back to simple grid
        solution_grid = [[cell.value for cell in row] for row in solver.grid]
        json.dump(solution_grid, f, indent=2)
    
    print(f"   Success: Solution saved: {solution_file}")
    
    # Step 7: Verify against expected solution (if available)
    print("Step 7: Verification...")
    
    expected_file = Path(f"examples_data/{image_file.stem}_puzzle.json")
    if expected_file.exists():
        try:
            with open(expected_file, 'r') as f:
                expected = json.load(f)
            
            # Compare grid structures
            if len(expected) == len(solution_grid) and all(len(row) == 9 for row in expected):
                print("   Success: Grid structure matches expected format")
                
                # Count differences
                differences = 0
                for i in range(9):
                    for j in range(9):
                        if expected[i][j] != 0 and solution_grid[i][j] != expected[i][j]:
                            differences += 1
                
                if differences == 0:
                    print("   Success: Solution exactly matches expected!")
                    
                else:
                    print(f"   Warning: Solution has {differences} differences from expected")
                    
                    # Show some differences
                    print("   Sample differences:")
                    diff_count = 0
                    for i in range(9):
                        for j in range(9):
                            if expected[i][j] != solution_grid[i][j] and diff_count < 5:
                                print(f"     Row {i}, Col {j}: Expected {expected[i][j]}, Got {solution_grid[i][j]}")
                                diff_count += 1
                    
            else:
                print("   Warning: Grid structure doesn't match expected format")
                
        except Exception as e:
            print(f"   Warning: Could not verify against expected: {e}")
    else:
        print(f"   Info: No expected solution file found: {expected_file}")
    
    print("\n" + "=" * 50)
    print("End-to-End Test Completed!")
    print(f"All outputs saved to: {output_path}")
    print("=" * 50)
    
    return True


def main():
    """Main function to run the end-to-end test."""
    
    # Test with one of the example images (now in examples_data directory)
    test_images = [
        "examples_data/NYT-EASY-2025-09-27.png",
        "examples_data/NYT-MED-2025-09-27.png", 
        "examples_data/NYT-HARD-2025-09-27.png"
    ]
    
    # Try each image until one works
    for image_path in test_images:
        print(f"\nTesting with image: {image_path}")
        
        try:
            success = run_end_to_end_test(image_path)
            if success:
                print(f"\nSuccessfully completed end-to-end test with {image_path}")
                break
            else:
                print(f"\nEnd-to-end test failed for {image_path}")
                
        except Exception as e:
            print(f"\nEnd-to-end test failed for {image_path}: {e}")
    
    else:
        print("\nAll images failed the end-to-end test")


if __name__ == "__main__":
    main()
