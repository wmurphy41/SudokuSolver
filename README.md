# SudokuSolver
 Python program that solves sudoku puzzles.   I developed the program as a way to teach myself python.

## Code
 Project comprises two files:
 - sudoku.py - All functional code.
 - test_sudoku.py - Contains test matrices that I took from the NY Times puzzles section.

### Class: Sudoku
 This is the main class, including the internal representation of the matrix and all the methods used to solve it.  The matrix is a 9x9 matrix of S_Cells.

#### Public Methods

 - `__init__`(self, matrix)  Takes as input a 9x9 matrix of digits representing the puzzle.  Blanks are represented as zeros.  See the test_sudoku files for examples
 - printPuzzle(self)  Prints a formatted version of the puzzle.
 - printCandidates(self) Prints a formatted grid of all the candidate values for each empty cell.  Since candidates are represented as sets, filled cells show the empty set in the candidate list.
 - solvePuzzle(self)  This method attempts to solve the puzzle and prints the results.

 ### Class: S_Cell
  This is the class that makes up each item in the puzzle matrix.  Each cell holds the cell value (zero for blank), the cell's row num, block num, and cell num, and the list of potential candidates that could be values for the cell.

 #### Public Methods

  - `__init__`(self, value, row_num, block_num)  Constructor
  - setVal(value) Sets the value of the cell and clears the constructor list.  Not that it does not make any changes to the matrix that owns the cell, like clearing the new cell value from other cells in its block.
  - setCandidates(candidates)  Sets the candidate list to the provided set.


#### Public Attributes
 - debug_level  At default of zero, solver displays only summary information after completing.  Setting debug_level to 1 and the sovler will print information about each cell filled and each candidate pruned so that you could use the output to manually solve a puzzle.  Set to 2 for some additional detail for the candidate pruning functions.

## How to use
- Import both source files into your python environment
- Load one of the matrices from the test file and use the solvePuzzle method.

```
>>> from sudoku import *
>>> from test_sudoku import *
>>> puzzle = Sudoku(matrix_hard_1)
>>> puzzle.solvePuzzle()
Starting puzzle:

0 0 0  0 0 0  7 0 5
0 0 0  9 3 0  0 0 0
0 1 4  0 0 5  2 0 0

0 0 0  0 0 1  3 0 0
1 0 0  0 0 7  0 0 0
6 0 8  0 4 0  0 9 0

0 0 0  2 0 0  0 6 0
8 0 0  0 0 0  0 5 4
0 0 3  0 0 0  0 0 0

Successfully solved puzzle
Completed 8 solve loops
Metrics:
 fillOnlyCandidate             :  23
 fillOnlyOption                :  36
 pruneGottaBeHereCantBeThere   :  14
 pruneMagicPairs               :  0
 pruneMagicTriplets            :  8
Final state of puzzle:

9 8 6  1 2 4  7 3 5
2 5 7  9 3 8  4 1 6
3 1 4  6 7 5  2 8 9

4 2 9  5 6 1  3 7 8
1 3 5  8 9 7  6 4 2
6 7 8  3 4 2  5 9 1

7 4 1  2 5 9  8 6 3
8 6 2  7 1 3  9 5 4
5 9 3  4 8 6  1 2 7

```

## License

Copyright © 2022 [William A. Murphy](https://github.com/wmurphy41).

This project is [MIT](https://spdx.org/licenses/MIT.html) licensed.
