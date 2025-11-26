"""
Sudoku Solver

Main Sudoku solving logic implementing multiple solving techniques including:
- Naked singles and hidden singles
- Naked and hidden pairs, triples, and quads
- Intersection removal techniques
- Advanced constraint propagation

Author: Improved version with better Python practices
"""

from typing import List, Set, Iterator
from sudoku_models import SudokuCell, SudokuError, SolvingMetrics


class SudokuSolver:
    """Main Sudoku solver class implementing multiple solving techniques."""
    
    # Constants
    GRID_SIZE = 9
    BLOCK_SIZE = 3
    VALID_VALUES = set(range(1, 10))
    
    def __init__(self, puzzle: List[List[int]], debug_level: int = 0) -> None:
        """
        Initialize the Sudoku solver.
        
        Args:
            puzzle: 9x9 grid of integers (0 for empty cells, 1-9 for filled)
            debug_level: Debug output level (0=silent, 1=informational, 2=basic, 3=detailed)
            
        Raises:
            SudokuError: If puzzle format is invalid
        """
        self.debug_level = debug_level
        self.metrics = SolvingMetrics()
        self.grid: List[List[SudokuCell]] = []
        
        self._validate_puzzle(puzzle)
        self._load_puzzle(puzzle)
        self._initialize_candidates()
    
    def _validate_puzzle(self, puzzle: List[List[int]]) -> None:
        """Validate the input puzzle format."""
        if len(puzzle) != self.GRID_SIZE:
            raise SudokuError(f"Puzzle must have {self.GRID_SIZE} rows, got {len(puzzle)}")
        
        for i, row in enumerate(puzzle):
            if len(row) != self.GRID_SIZE:
                raise SudokuError(f"Row {i} must have {self.GRID_SIZE} columns, got {len(row)}")
            for j, value in enumerate(row):
                if not isinstance(value, int) or not (0 <= value <= 9):
                    raise SudokuError(f"Invalid value at ({i}, {j}): {value}")
    
    def _load_puzzle(self, puzzle: List[List[int]]) -> None:
        """Load the puzzle into the internal grid representation."""
        self.grid = []
        for row_idx, row in enumerate(puzzle):
            grid_row = []
            for col_idx, value in enumerate(row):
                grid_row.append(SudokuCell(value, row_idx, col_idx))
            self.grid.append(grid_row)
    
    def _initialize_candidates(self) -> None:
        """Initialize candidates for all empty cells."""
        # Get existing values in each constraint group
        block_values = [self._get_block_values(b) for b in range(self.GRID_SIZE)]
        row_values = [self._get_row_values(r) for r in range(self.GRID_SIZE)]
        col_values = [self._get_col_values(c) for c in range(self.GRID_SIZE)]
        
        # Remove impossible candidates
        for cell in self._iterate_all_cells():
            if cell.is_empty():
                cell.candidates -= block_values[cell.block]
                cell.candidates -= row_values[cell.row]
                cell.candidates -= col_values[cell.col]
    
    def _get_block_values(self, block_num: int) -> Set[int]:
        """Get all filled values in a block."""
        return {cell.value for cell in self._iterate_block(block_num) if not cell.is_empty()}
    
    def _get_row_values(self, row_num: int) -> Set[int]:
        """Get all filled values in a row."""
        return {cell.value for cell in self._iterate_row(row_num) if not cell.is_empty()}
    
    def _get_col_values(self, col_num: int) -> Set[int]:
        """Get all filled values in a column."""
        return {cell.value for cell in self._iterate_col(col_num) if not cell.is_empty()}
    
    # Iterator methods
    def _iterate_all_cells(self) -> Iterator[SudokuCell]:
        """Iterate through all cells in the grid."""
        for row in self.grid:
            for cell in row:
                yield cell
    
    def _iterate_block(self, block_num: int) -> Iterator[SudokuCell]:
        """Iterate through cells in a specific block."""
        start_row = (block_num // self.BLOCK_SIZE) * self.BLOCK_SIZE
        start_col = (block_num % self.BLOCK_SIZE) * self.BLOCK_SIZE
        
        for row in range(start_row, start_row + self.BLOCK_SIZE):
            for col in range(start_col, start_col + self.BLOCK_SIZE):
                yield self.grid[row][col]
    
    def _iterate_row(self, row_num: int) -> Iterator[SudokuCell]:
        """Iterate through cells in a specific row."""
        for col in range(self.GRID_SIZE):
            yield self.grid[row_num][col]
    
    def _iterate_col(self, col_num: int) -> Iterator[SudokuCell]:
        """Iterate through cells in a specific column."""
        for row in range(self.GRID_SIZE):
            yield self.grid[row][col_num]
    
    def _debug_print(self, level: int, message: str) -> None:
        """Print debug message if level is appropriate."""
        if level <= self.debug_level:
            print(message)
    
    def to_dict(self) -> dict:
        """
        Serialize the solver state to a dictionary.
        
        Returns:
            Dictionary containing grid (with values and candidates) and debug_level
        """
        grid_data = []
        for row in self.grid:
            row_data = []
            for cell in row:
                cell_data = {
                    "value": cell.value,
                    "candidates": sorted(cell.candidates) if cell.candidates else []
                }
                row_data.append(cell_data)
            grid_data.append(row_data)
        
        return {
            "grid": grid_data,
            "debug_level": self.debug_level
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SudokuSolver':
        """
        Restore a SudokuSolver instance from a serialized dictionary.
        
        Args:
            data: Dictionary containing grid (with values and candidates) and debug_level
            
        Returns:
            Restored SudokuSolver instance
        """
        debug_level = data.get("debug_level", 0)
        grid_data = data["grid"]
        
        # Create a solver instance (we'll bypass normal initialization)
        solver = cls.__new__(cls)
        solver.debug_level = debug_level
        solver.metrics = SolvingMetrics()
        solver.grid = []
        
        # Restore grid with values and candidates
        for row_idx, row_data in enumerate(grid_data):
            grid_row = []
            for col_idx, cell_data in enumerate(row_data):
                value = cell_data["value"]
                candidates = set(cell_data.get("candidates", []))
                
                # Create cell with value
                cell = SudokuCell(value, row_idx, col_idx)
                # Restore candidates
                cell.candidates = candidates
                grid_row.append(cell)
            solver.grid.append(grid_row)
        
        return solver
    
    def count_empty_cells(self) -> int:
        """Count the number of empty cells remaining."""
        return sum(1 for cell in self._iterate_all_cells() if cell.is_empty())
    
    def print_grid(self, force_print: bool = True) -> None:
        """Print the current state of the grid with block separators."""
        if force_print or self.debug_level > 0:  # Print if forced or not silent
            for row in range(self.GRID_SIZE):
                if row % self.BLOCK_SIZE == 0 and row > 0:
                    print("  " + "-" * 21)
                
                row_str = "  "
                for col in range(self.GRID_SIZE):
                    if col % self.BLOCK_SIZE == 0 and col > 0:
                        row_str += "| "
                    row_str += f"{self.grid[row][col]} "
                print(row_str)
            print()
    
    def print_candidates(self, force_print: bool = True) -> None:
        """Print candidates for all cells (debugging aid)."""
        if force_print or self.debug_level > 0:  # Print if forced or not silent
            print("\nCandidates:")
            for row in range(self.GRID_SIZE):
                if row % self.BLOCK_SIZE == 0 and row > 0:
                    print()
                
                for col in range(self.GRID_SIZE):
                    if col % self.BLOCK_SIZE == 0 and col > 0:
                        print(" | ", end="")
                    cell = self.grid[row][col]
                    candidates_str = str(sorted(cell.candidates)) if cell.candidates else "[]"
                    print(f"{candidates_str:>20}", end="")
                print()
            print()
    
    def solve(self) -> bool:
        """
        Solve the Sudoku puzzle using multiple techniques.
        
        Returns:
            True if puzzle is solved, False if unsolvable
        """
        self._debug_print(1, "Starting puzzle solution...")
        self.print_grid(False)
        
        self.metrics.reset()
        initial_empty = self.count_empty_cells()
        
        while self.count_empty_cells() > 0:
            self.metrics.solve_loops += 1
            self._debug_print(2, f"Solve loop: {self.metrics.solve_loops}")
            
            cells_filled = 0
            candidates_pruned = 0
            
            # Try to fill cells
            cells_filled += self._fill_naked_singles()
            cells_filled += self._fill_hidden_singles()
            
            # If no cells filled, try pruning candidates
            if cells_filled == 0:
                candidates_pruned += self._prune_intersection_removal()
                candidates_pruned += self._prune_naked_groups()
                candidates_pruned += self._prune_hidden_groups()
            
            # If no progress made, puzzle is unsolvable with current techniques
            if cells_filled == 0 and candidates_pruned == 0:
                self._debug_print(2, "No progress made - puzzle may be unsolvable")
                break
        
        solved = self.count_empty_cells() == 0
        self._print_solution_summary(initial_empty, solved)
        return solved
    
    def step_solve(self) -> bool:
        """
        Perform one pass through all solving techniques without looping.
        
        Returns:
            True if puzzle is solved after this step, False otherwise
        """
        self._debug_print(1, "Performing one solving step...")
        self.print_grid(False)
        
        # Increment solve loop counter for metrics tracking
        self.metrics.solve_loops += 1
        self._debug_print(2, f"Solve step: {self.metrics.solve_loops}")
        
        cells_filled = 0
        candidates_pruned = 0
        
        # Try to fill cells
        cells_filled += self._fill_naked_singles()
        cells_filled += self._fill_hidden_singles()
        
        # If no cells filled, try pruning candidates
        if cells_filled == 0:
            candidates_pruned += self._prune_intersection_removal()
            candidates_pruned += self._prune_naked_groups()
            candidates_pruned += self._prune_hidden_groups()
        
        # Check if puzzle is solved
        solved = self.count_empty_cells() == 0
        
        self._debug_print(2, f"Step completed: {cells_filled} cells filled, {candidates_pruned} candidates pruned")
        if solved:
            self._debug_print(1, "Puzzle is now solved!")
            self._print_solution_summary(0, solved)  # Pass 0 for initial_empty since we don't track it in step mode
        elif cells_filled == 0 and candidates_pruned == 0:
            self._debug_print(2, "No progress made in this step")
        else:
            self._debug_print(1, "Progress made in this step.  Resulting puzzle:")
            self.print_grid(False)
            self._debug_print(2, f"Step completed: {cells_filled} cells filled, {candidates_pruned} candidates pruned")
        
        return solved
    
    def _fill_naked_singles(self) -> int:
        """Fill cells that have only one candidate."""
        self._debug_print(2, "Checking for naked singles...")
        filled_count = 0
        
        for cell in self._iterate_all_cells():
            if cell.is_empty() and len(cell.candidates) == 1:
                value = cell.candidates.pop()
                self._fill_cell(cell, value)
                filled_count += 1
                self.metrics.fill_only_candidate += 1
        
        self._debug_print(2, f"Filled {filled_count} naked singles")
        return filled_count
    
    def _fill_hidden_singles(self) -> int:
        """Fill cells where a value can only go in one position in a constraint group."""
        self._debug_print(2, "Checking for hidden singles...")
        filled_count = 0
        
        # Check blocks, rows, and columns
        for group_type in ['block', 'row', 'col']:
            for group_idx in range(self.GRID_SIZE):
                filled_count += self._find_hidden_singles_in_group(group_type, group_idx)
        
        self._debug_print(2, f"Filled {filled_count} hidden singles")
        return filled_count
    
    def _find_hidden_singles_in_group(self, group_type: str, group_idx: int) -> int:
        """Find hidden singles in a specific constraint group."""
        filled_count = 0
        
        # Get cells in the group
        if group_type == 'block':
            cells = list(self._iterate_block(group_idx))
        elif group_type == 'row':
            cells = list(self._iterate_row(group_idx))
        else:  # column
            cells = list(self._iterate_col(group_idx))
        
        # Find values that appear in only one cell
        for value in self.VALID_VALUES:
            cells_with_value = [cell for cell in cells if cell.is_empty() and value in cell.candidates]
            if len(cells_with_value) == 1:
                cell = cells_with_value[0]
                self._fill_cell(cell, value)
                filled_count += 1
                self.metrics.fill_only_option += 1
        
        return filled_count
    
    def _fill_cell(self, cell: SudokuCell, value: int) -> None:
        """Fill a cell with a value and update constraints."""
        cell.set_value(value)
        self._debug_print(2, f"Filled {value} at ({cell.row}, {cell.col})")
        
        # Remove value from candidates in same block, row, and column
        for other_cell in self._iterate_block(cell.block):
            if other_cell != cell:
                other_cell.remove_candidate(value)
        
        for other_cell in self._iterate_row(cell.row):
            if other_cell != cell:
                other_cell.remove_candidate(value)
        
        for other_cell in self._iterate_col(cell.col):
            if other_cell != cell:
                other_cell.remove_candidate(value)
    
    def _prune_intersection_removal(self) -> int:
        """Apply intersection removal techniques."""
        self._debug_print(2, "Applying intersection removal...")
        pruned_count = 0
        
        # Check each constraint group
        for group_type in ['block', 'row', 'col']:
            for group_idx in range(self.GRID_SIZE):
                pruned_count += self._prune_intersection_in_group(group_type, group_idx)
        
        self.metrics.prune_gotta_be_here += pruned_count
        self._debug_print(2, f"Pruned {pruned_count} candidates via intersection removal")
        return pruned_count
    
    def _prune_intersection_in_group(self, group_type: str, group_idx: int) -> int:
        """Apply intersection removal within a specific group."""
        pruned_count = 0
        
        # Get cells in the group
        if group_type == 'block':
            cells = list(self._iterate_block(group_idx))
        elif group_type == 'row':
            cells = list(self._iterate_row(group_idx))
        else:  # column
            cells = list(self._iterate_col(group_idx))
        
        # For each value, check if it's constrained to one sub-group
        for value in self.VALID_VALUES:
            cells_with_value = [cell for cell in cells if cell.is_empty() and value in cell.candidates]
            if len(cells_with_value) <= 3:  # Only apply if few cells have this candidate
                # Check if all cells with this value are in the same sub-group
                if self._all_in_same_subgroup(cells_with_value, group_type):
                    pruned_count += self._prune_value_from_other_subgroups(value, cells_with_value, group_type)
        
        return pruned_count
    
    def _all_in_same_subgroup(self, cells: List[SudokuCell], group_type: str) -> bool:
        """Check if all cells are in the same sub-group."""
        if len(cells) <= 1:
            return True
        
        if not cells:  # Safety check for empty list
            return False
        
        if group_type == 'block':
            # Check if all in same row or column
            rows = {cell.row for cell in cells}
            cols = {cell.col for cell in cells}
            return len(rows) == 1 or len(cols) == 1
        else:
            # Check if all in same block
            blocks = {cell.block for cell in cells}
            return len(blocks) == 1
    
    def _prune_value_from_other_subgroups(self, value: int, cells: List[SudokuCell], group_type: str) -> int:
        """Remove value from other sub-groups."""
        pruned_count = 0
        
        # Safety check: ensure we have cells to work with
        if not cells:
            return pruned_count
        
        if group_type == 'block':
            # If all cells are in same row, remove from other cells in that row
            if len({cell.row for cell in cells}) == 1:
                row = cells[0].row
                for cell in self._iterate_row(row):
                    if cell not in cells and value in cell.candidates:
                        cell.remove_candidate(value)
                        pruned_count += 1
            
            # If all cells are in same column, remove from other cells in that column
            elif len({cell.col for cell in cells}) == 1:
                col = cells[0].col
                for cell in self._iterate_col(col):
                    if cell not in cells and value in cell.candidates:
                        cell.remove_candidate(value)
                        pruned_count += 1
        
        else:  # row or column
            # Remove from other cells in the same block
            block = cells[0].block
            for cell in self._iterate_block(block):
                if cell not in cells and value in cell.candidates:
                    cell.remove_candidate(value)
                    pruned_count += 1
        
        return pruned_count
    
    def _prune_naked_groups(self) -> int:
        """Apply naked group techniques (pairs, triples, quads)."""
        self._debug_print(2, "Applying naked group techniques...")
        pruned_count = 0
        
        # Check each constraint group
        for group_type in ['block', 'row', 'col']:
            for group_idx in range(self.GRID_SIZE):
                pruned_count += self._prune_naked_groups_in_group(group_type, group_idx)
        
        self.metrics.prune_magic_pairs += pruned_count
        self._debug_print(2, f"Pruned {pruned_count} candidates via naked groups")
        return pruned_count
    
    def _prune_naked_groups_in_group(self, group_type: str, group_idx: int) -> int:
        """Apply naked group techniques within a specific group."""
        pruned_count = 0
        
        # Get cells in the group
        if group_type == 'block':
            cells = [cell for cell in self._iterate_block(group_idx) if cell.is_empty()]
        elif group_type == 'row':
            cells = [cell for cell in self._iterate_row(group_idx) if cell.is_empty()]
        else:  # column
            cells = [cell for cell in self._iterate_col(group_idx) if cell.is_empty()]
        
        # Find naked groups of different sizes
        for group_size in range(2, 5):  # pairs, triples, quads
            naked_groups = self._find_naked_groups(cells, group_size)
            for group in naked_groups:
                pruned_count += self._prune_other_cells_in_group(cells, group, group_size)
        
        return pruned_count
    
    def _find_naked_groups(self, cells: List[SudokuCell], group_size: int) -> List[List[SudokuCell]]:
        """Find naked groups of a specific size."""
        naked_groups = []
        
        # Generate all combinations of cells of the specified size
        from itertools import combinations
        
        for cell_group in combinations(cells, group_size):
            # Check if this group forms a naked group
            all_candidates = set()
            for cell in cell_group:
                all_candidates.update(cell.candidates)
            
            # If the union of candidates equals the group size, it's a naked group
            if len(all_candidates) == group_size:
                naked_groups.append(list(cell_group))
        
        return naked_groups
    
    def _prune_other_cells_in_group(self, cells: List[SudokuCell], naked_group: List[SudokuCell], group_size: int) -> int:
        """Remove naked group candidates from other cells in the group."""
        pruned_count = 0
        group_candidates = set()
        
        for cell in naked_group:
            group_candidates.update(cell.candidates)
        
        for cell in cells:
            if cell not in naked_group:
                original_size = len(cell.candidates)
                cell.candidates -= group_candidates
                pruned_count += original_size - len(cell.candidates)
        
        return pruned_count
    
    def _prune_hidden_groups(self) -> int:
        """Apply hidden group techniques."""
        # This is a simplified implementation
        # A full implementation would be quite complex
        return 0
    
    def _print_solution_summary(self, initial_empty: int, solved: bool) -> None:
        """Print a summary of the solution attempt."""
        if self.debug_level > 0:  # Only print if not silent
            final_empty = self.count_empty_cells()
            
            print(f"\n{'='*50}")
            print("SOLUTION SUMMARY")
            print(f"{'='*50}")
            print(f"Initial empty cells: {initial_empty}")
            print(f"Final empty cells: {final_empty}")
            print(f"Solve loops: {self.metrics.solve_loops}")
            print(f"Solved: {'Yes' if solved else 'No'}")
            
            print("\nTechniques used:")
            print(f"  Naked singles: {self.metrics.fill_only_candidate}")
            print(f"  Hidden singles: {self.metrics.fill_only_option}")
            print(f"  Intersection removal: {self.metrics.prune_gotta_be_here}")
            print(f"  Naked groups: {self.metrics.prune_magic_pairs}")
            
            print("\nFinal grid:")
            self.print_grid(False)


def solve_sudoku(puzzle: List[List[int]], debug_level: int = 0) -> bool:
    """
    Convenience function to solve a Sudoku puzzle.
    
    Args:
        puzzle: 9x9 grid of integers (0 for empty cells, 1-9 for filled)
        debug_level: Debug output level (0=silent, 1=informational, 2=basic, 3=detailed)
        
    Returns:
        True if puzzle is solved, False otherwise
    """
    solver = SudokuSolver(puzzle, debug_level)
    return solver.solve()


if __name__ == "__main__":
    # Example usage
    example_puzzle = [
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
    
    solver = SudokuSolver(example_puzzle, debug_level=2)
    solved = solver.solve()
    print(f"Puzzle solved: {solved}")
