# Sudoku solver


# ----------------------------------------------------- #
class Sudoku:
# Main Sudoku solver class
# - Holds matrix of Sudoku cell, with values and candidates
# - Has methods for solving the puzzle.

    # ------ public methods -------------------------------------
    def __init__(self, matrix):
        self.loadMatrix(matrix)
        self.initCandidates()
        self.metrics = {                        \
            'fillOnlyCandidate':0,              \
            'fillOnlyOption':0,                 \
            'pruneGottaBeHereCantBeThere':0,    \
            'pruneMagicPairs':0,                \
            'pruneMagicTriplets':0,             \
            'pruneMagicQuads':0 }
        self.solve_loops = 0
        self.debug_level = 0

    def printPuzzle(self):
    #Prints the formated grid with spaces between blocks
        for row in range(9):
            if row%3==0: print()
            for col in range(9):
                if col%3==0: print(" ", end="")
                print(self.grid[row][col].val, end=" ")
            print()
        print()

    def printCandidates(self):
        # Prints matrix of all the candidates for each cell
        for r in range(9):
            if r % 3 == 0: print()
            row = [cell.candidates for cell in self.S_Row(r)]
            for cell in self.S_Row(r):
                print(str(cell.candidates).ljust(22), end="")
                if cell.col_num % 3 == 2: print(" | ",end="")
            print()

    def solvePuzzle(self):
        # Logic for solving puzzle:
        # - Loop until through the heuristics until no progress:
        #     - Fill cells where there is only one candidate for a cell
        #     - Fill cells where a row/block/col is missing a number
        #       and that number is a candidate in only one cell
        #
        #     - If you didn't fill any cells on this loop then
        #       use heuristics to prune some candidates:
        #       - If a number for a row/block/cell is only in
        #         one row/block/cell, then prune it from the others
        #       - If there is a magic pair, then prune other candidates
        #       - If there is a magic triplet, then prune other candidates
        #       - If there is a magic quad, then prune other candidates
        #
        print("Starting puzzle:")
        self.printPuzzle()

        # solve Loop
        count0 = self.countZeros()
        self.solve_loops = 0
        error_message = ""
        fail = False

        while count0 != 0:
            self.solve_loops += 1
            cells_filled_this_loop = 0
            self.debugPrint(1, 'Solve loop: ' + str(self.solve_loops))

            #try:
            # Fill as many cells as you can
            cells_filled_this_loop += self.fillOnlyCandidate()
            cells_filled_this_loop += self.fillOnlyOption()

            # if unable to fill any cells, try purging candidates
            if cells_filled_this_loop == 0:
                prune_count = self.pruneGottaBeHereCantBeThere()
                prune_count += self.pruneMagicPairs()
                prune_count += self.pruneMagicTriplets()
                prune_count += self.pruneMagicQuads()

            # if no candidates pruned, then break out of the solve loops
            # and give up
            if cells_filled_this_loop == 0 and prune_count == 0:
                fail = True

            #except Exception as error:
                #error_message = str(error.args)

            if fail or len(error_message) != 0:
                break

            count0 = self.countZeros()

        if error_message != "":
            print("Error encountered while solving: " + error_message)
        elif count0 == 0:
            print("Successfully solved puzzle")
        else:
            print("Unable to solve puzzle. " + str(count0) + " blanks remain.")
        print('Completed ' + str(self.solve_loops) + ' solve loops')
        print("Metrics:")
        for k in self.metrics:
            print("  " + k.ljust(30) + ":  " + str(self.metrics[k]))
        print("Final state of puzzle:")
        self.printPuzzle()
        return

    # ------ private methods -------------------------------------
    # ------ initialization methods -------------------------------------
    def loadMatrix(self, matrix):
        # Initializes Sudoku internal representation of the puzzle
        # Validates dimensions and values of the inputs
        # Creates matrix of S_Cells
        if len(matrix) != 9:
            raise Exception("Matrix dimensions are bad")
        grid = []
        for r in range(9):
            grid_row = []
            for c in range(9):
                grid_row += [S_Cell(matrix[r][c], r, c)]
            grid += [grid_row]
        self.grid = grid

    def initCandidates(self):
        # For all blank cells in the matrix, fills in the possible values
        # that could go there
        block_vals = [{cell.val for cell in self.S_Block(b)} for b in range(9)]
        row_vals = [{cell.val for cell in self.S_Row(r)} for r in range(9)]
        col_vals = [{cell.val for cell in self.S_Col(c)} for c in range(9)]

        for cell in self.S_Matrix():
            cell.candidates.difference_update(block_vals[cell.block_num])
            cell.candidates.difference_update(row_vals[cell.row_num])
            cell.candidates.difference_update(col_vals[cell.col_num])

    def debugPrint(self, d, str):
        # Prints only if we are in debug mode
        if d <= self.debug_level:
            print(str)

    # ------ UTILITY methods -------------------------------------
    def countZeros(self):
        # Counts the zeros left in the puzzle
        count0 = 0
        for r in range(9):
            for cell in self.S_Row(r):
                if cell.val == 0: count0 += 1
        return count0


    # ------ Generator methods:
    def S_Matrix(self):
    # Generator function for iterating through the cells in the Matrix
        for r in range(9):
            for c in range(9):
                yield self.grid[r][c]

    def S_Block(self, block_num):
    # Generator function for iterating through the cells in a block
        block_r = block_num // 3 * 3
        block_c = block_num % 3 * 3
        for r in range(block_r, block_r + 3):
            for c in range(block_c, block_c + 3):
                yield self.grid[r][c]

    def S_Row(self, row_num):
    # Generator function for iterating through the cells in a row
        for c in range(9):
            yield self.grid[row_num][c]

    def S_Col(self, col_num):
    # Generator function for iterating through the cells in a row
        for r in range(9):
            yield self.grid[r][col_num]


    # ------ SOLVE methods -------------------------------------
    def fillOnlyCandidate(self):
        # If a cell only has one candidate, fill it in and prune
        # the candidate lists for all other cells in the same block, row, col
        self.debugPrint(1, "Start fillOneCandidate...")
        values_filled = 0
        for cell in self.S_Matrix():
            if cell.val != 0: continue
            if len(cell.candidates) == 0:
                raise Exception("No candidates at "+ str(cell.val) + "| "+ str(cell.row_num) + ", " + str(cell.col_num))
            if len(cell.candidates) == 1:
                values_filled += 1
                self.fillValue(cell, cell.candidates.pop())
        self.metrics['fillOnlyCandidate'] += values_filled
        self.debugPrint(1, 'Total filled: ' + str(values_filled))
        return values_filled



    def fillOnlyOption(self):
        # logic
        # for each row/blocks
        #   make a list that's the concatenation of all the candidates
        #   Put each one that occurs only once into a set
        #   For each cell in the row
        #       If one of the singletons is in the candidates
        #       clear the other candidates
        #
        self.debugPrint(1, "Start fillOnlyOption...")
        values_filled = 0

        # Check blocks
        for i in range(9):
            for s in self.findSingleCandidates([cell for cell in self.S_Block(i)]):
                for cell in self.S_Block(i):
                    if s in cell.candidates:
                        values_filled += 1
                        self.fillValue(cell, s)
                        break
        # Check rows
        for i in range(9):
            for s in self.findSingleCandidates([cell for cell in self.S_Row(i)]):
                for cell in self.S_Row(i):
                    if s in cell.candidates:
                        values_filled += 1
                        self.fillValue(cell, s)
                        break

        # Check cols
        for i in range(9):
            for s in self.findSingleCandidates([cell for cell in self.S_Col(i)]):
                for cell in self.S_Col(i):
                    if s in cell.candidates:
                        values_filled += 1
                        self.fillValue(cell, s)
                        break

        self.metrics['fillOnlyOption'] += values_filled
        self.debugPrint(1, 'Total filled: ' + str(values_filled))
        return values_filled

    def fillValue(self, cell, val):
        # Set cell value to v and prune the canidates in all the cell's
        # block, row, and column
        cell.setVal(val)
        self.debugPrint(1, "- filled " + str(val) + " into " + str(cell.row_num) + ", " + str(cell.col_num))
        for b_cell in self.S_Block(cell.block_num):
            b_cell.candidates.discard(val)
        for r_cell in self.S_Row(cell.row_num):
            r_cell.candidates.discard(val)
        for c_cell in self.S_Col(cell.col_num):
            c_cell.candidates.discard(val)

    def findSingleCandidates(self, cell_array):
        full_c_list = []
        for c in [list(cell.candidates) for cell in cell_array]:
            full_c_list.extend(c)
        single_candidates = set()
        for n in range(9):
            if full_c_list.count(n) == 1:
                single_candidates.add(n)
        return(single_candidates)


    def pruneGottaBeHereCantBeThere(self):
        # if a candidate in a row/col occurs only in one block
        #     then remove that candidate from all cells in the block outside
        #     that row/col
        # If a candidate in a block occurs only in one row/col
        #     then remove that candidate from all cells in the row/col
        #     outside that block
        self.debugPrint(1, "Start pruneGottaBeHereCantBeThere...")
        prune_count = self.pruneGbhcbtBlock()
        prune_count += self.pruneGbhcbtRow()
        prune_count += self.pruneGbhcbtCol()

        self.metrics['pruneGottaBeHereCantBeThere'] += prune_count
        self.debugPrint(1, 'Total pruned: ' + str(prune_count) + " xxx " + str(self.metrics['pruneGottaBeHereCantBeThere']))
        return prune_count

    def pruneGbhcbtBlock(self):
        # If a candidate in a block occurs only in one row/col
        #     then remove that candidate from all cells in the row/col
        #     outside that block
        prune_count = 0
        for block in range(9):
            # Create dict of candidates that occur only in one row/col
            prune_dict_col = dict()
            prune_dict_row = dict()
            for cell in self.S_Block(block):
                    for c in cell.candidates:
                        if str(c) in prune_dict_row:
                            if prune_dict_row[str(c)] != cell.row_num:
                                prune_dict_row[str(c)] = -1
                        else:
                                prune_dict_row[str(c)] = cell.row_num
                        if str(c) in prune_dict_col:
                            if prune_dict_col[str(c)] != cell.col_num:
                                prune_dict_col[str(c)] = -1
                        else:
                                prune_dict_col[str(c)] = cell.col_num
            for key in list(prune_dict_row.keys()):
                if prune_dict_row[key] == -1: del prune_dict_row[key]
            for key in list(prune_dict_col.keys()):
                if prune_dict_col[key] == -1: del prune_dict_col[key]
            self.debugPrint(2, str(block) + " (r): " + str(prune_dict_row))
            self.debugPrint(2, str(block) + " (c): " + str(prune_dict_col))
            for cand in prune_dict_row:
                prune_count += self.pruneRowExcBlock(prune_dict_row[cand], block, int(cand))
            for cand in prune_dict_col:
                prune_count += self.pruneColExcBlock(prune_dict_col[cand], block, int(cand))
        return prune_count

    def pruneRowExcBlock(self, row_num, block_num, val):
        # Prunes val from the candidate lists of all cells in the block except those
        # in the block_num
        prune_count = 0
        for cell in self.S_Row(row_num):
            if cell.block_num != block_num and val in cell.candidates:
                prune_count += 1
                cell.candidates.discard(val)
                self.debugPrint(1, "- pruned " + str(val) + " from " + str(cell.row_num) + ", " + str(cell.col_num))
        return prune_count

    def pruneColExcBlock(self, col_num, block_num, val):
        # Prunes val from the candidate lists of all cells in the block except those
        # in the block_num
        prune_count = 0
        for cell in self.S_Col(col_num):
            if cell.block_num != block_num and val in cell.candidates:
                prune_count += 1
                cell.candidates.discard(val)
                self.debugPrint(1, "- pruned " + str(val) + " from " + str(cell.row_num) + ", " + str(cell.col_num))
        return prune_count

    def pruneGbhcbtRow(self):
        # if a candidate in a row occurs only in one block
        #     then remove that candidate from all cells in the block outside
        #     that row
        prune_count = 0
        for row in range(9):
            # Create dict of candidates that occur only in one block
            prune_dict = dict()
            for cell in self.S_Row(row):
                    for c in cell.candidates:
                        if str(c) in prune_dict:
                            if prune_dict[str(c)] != cell.block_num:
                                prune_dict[str(c)] = -1
                        else:
                                prune_dict[str(c)] = cell.block_num
            for key in list(prune_dict.keys()):
                if prune_dict[key] == -1: del prune_dict[key]
            self.debugPrint(2, str(row) + ": " + str(prune_dict))
            for cand in prune_dict:
                prune_count += self.pruneBlockExcRow(prune_dict[cand], row, int(cand))
        return prune_count

    def pruneBlockExcRow(self, block_num, row_num, val):
        # prunes val from the candidate lists of the two rows in the block
        # other than row.
        prune_count = 0
        for cell in self.S_Block(block_num):
            if cell.row_num != row_num and val in cell.candidates:
                prune_count += 1
                cell.candidates.discard(val)
                self.debugPrint(1, "- pruned " + str(val) + " from " + str(cell.row_num) + ", " + str(cell.col_num))
        return prune_count


    def pruneGbhcbtCol(self):
        # if a candidate in a col occurs only in one block
        #     then remove that candidate from all cells in the block outside
        #     that col
        prune_count = 0
        for col in range(9):
            # Create dict of candidates that occur only in one block
            prune_dict = dict()
            for cell in self.S_Col(col):
                    for c in cell.candidates:
                        if str(c) in prune_dict:
                            if prune_dict[str(c)] != cell.block_num:
                                prune_dict[str(c)] = -1
                        else:
                                prune_dict[str(c)] = cell.block_num
            for key in list(prune_dict.keys()):
                if prune_dict[key] == -1: del prune_dict[key]
            self.debugPrint(2, str(col) + ": " + str(prune_dict))
            for cand in prune_dict:
                prune_count += self.pruneBlockExcCol(prune_dict[cand], col, int(cand))
        return prune_count

    def pruneBlockExcCol(self, block_num, col_num, val):
        # prunes val from the candidate lists of the two rows in the block
        # other than row.
        prune_count = 0
        for cell in self.S_Block(block_num):
            if cell.col_num != col_num and val in cell.candidates:
                prune_count += 1
                cell.candidates.discard(val)
                self.debugPrint(1, "- pruned " + str(val) + " from " + str(cell.row_num) + ", " + str(cell.col_num))
        return prune_count

    def pruneMagicPairs(self):
        # If any pair of candidates appears twice in a block/row/col,
        # then the members of that pair can't appear anywhere else in that
        # block/row/col

        self.debugPrint(1, "Start pruneMagicPairs...")
        prune_count = 0

        # Prune Magic Pairs from blocks
        for i in range(9):
            cell_list = [cell for cell in self.S_Block(i)]
            mp_list = self.findMagicPairs(cell_list)
            for mp1, mp2 in mp_list:
                for cell in cell_list:
                    if cell != mp1 and cell != mp2:
                        c_len = len(cell.candidates)
                        cell.candidates -= mp1.candidates
                        num_pruned = c_len - len(cell.candidates)
                        if c_len != len(cell.candidates):
                            self.debugPrint(1, "- pruned " + str(num_pruned) + " from " + str(cell.row_num) + "," + str(cell.col_num) + " for mp: " + str(mp1.candidates))
                            prune_count += num_pruned

        # Prune Magic Pairs from rows
        for i in range(9):
            cell_list = [cell for cell in self.S_Row(i)]
            mp_list = self.findMagicPairs(cell_list)
            for mp1, mp2 in mp_list:
                for cell in cell_list:
                    if cell != mp1 and cell != mp2:
                        c_len = len(cell.candidates)
                        cell.candidates -= mp1.candidates
                        num_pruned = c_len - len(cell.candidates)
                        if c_len != len(cell.candidates):
                            self.debugPrint(1, "- pruned " + str(num_pruned) + " from " + str(cell.row_num) + "," + str(cell.col_num) + " for mp: " + str(mp1.candidates))
                            prune_count += num_pruned

        # Prune Magic Pairs from columns
        for i in range(9):
            cell_list = [cell for cell in self.S_Col(i)]
            mp_list = self.findMagicPairs(cell_list)
            for mp1, mp2 in mp_list:
                for cell in cell_list:
                    if cell != mp1 and cell != mp2:
                        c_len = len(cell.candidates)
                        cell.candidates -= mp1.candidates
                        num_pruned = c_len - len(cell.candidates)
                        if c_len != len(cell.candidates):
                            self.debugPrint(1, "- pruned " + str(num_pruned) + " from " + str(cell.row_num) + "," + str(cell.col_num) + " for mp: " + str(mp1.candidates))
                            prune_count += num_pruned

        self.metrics['pruneMagicPairs'] += prune_count
        self.debugPrint(1, 'Total pruned: ' + str(prune_count) + " xxx " + str(self.metrics['pruneMagicPairs']))
        return prune_count

    def findMagicPairs(self, cell_list):
        # Given a list of cells from a row/block/col
        # return a list of any magic pairs that it contains
        magic_pair_list = []
        for i in range(9):
            if len(cell_list[i].candidates) != 2:
                continue
            for j in range(i+1, 9):
                if len(cell_list[j].candidates) != 2:
                    continue
                union_candidates = cell_list[i].candidates | cell_list[j].candidates
                if len(union_candidates) == 2:
                    magic_pair_list += [[cell_list[i], cell_list[j]]]
        return magic_pair_list


    def pruneMagicTriplets(self):
        # if any group of three cells in row/col/block contains only three
        # candidates then none of those candidates can appear anywhere else
        # that row/col/block

        # for all blocks
        #   call findMagicTriplets and get list of mts
        #   for each mp
        #       prune the two candidates from all other cells in block

        # for all blocks
        #   call findMagicTriplets and get list of mts
        #   for each mp
        #       prune the two candidates from all other cells in block

        # for all blocks
        #   call findMagicTriplets and get list of mts
        #   for each mp
        #       prune the two candidates from all other cells in block

        # return count of candidates pruned
        self.debugPrint(1, "Start pruneMagicTriplets...")
        prune_count = 0

        # Prune Magic Triplets from blocks
        for i in range(9):
            cell_list = [cell for cell in self.S_Block(i)]
            mt_list = self.findMagicTriplets(cell_list)
            for mt_c, mt1, mt2, mt3 in mt_list:
                for cell in cell_list:
                    if cell != mt1 and cell != mt2 and cell != mt3:
                        c_len = len(cell.candidates)
                        cell.candidates -= mt_c
                        num_pruned = c_len - len(cell.candidates)
                        if c_len != len(cell.candidates):
                            self.debugPrint(1, "- pruned " + str(num_pruned) + " from " + str(cell.row_num) + "," + str(cell.col_num) + " for mt: " + str(mt_c))
                            prune_count += num_pruned

        # Prune Magic Triplets from rows
        for i in range(9):
            cell_list = [cell for cell in self.S_Row(i)]
            mt_list = self.findMagicTriplets(cell_list)
            for mt_c, mt1, mt2, mt3 in mt_list:
                for cell in cell_list:
                    if cell != mt1 and cell != mt2 and cell != mt3:
                        c_len = len(cell.candidates)
                        cell.candidates -= mt_c
                        num_pruned = c_len - len(cell.candidates)
                        if c_len != len(cell.candidates):
                            self.debugPrint(1, "- pruned " + str(num_pruned) + " from " + str(cell.row_num) + "," + str(cell.col_num) + " for mt: " + str(mt_c))
                            prune_count += num_pruned

        # Prune Magic Triplets from cols
        for i in range(9):
            cell_list = [cell for cell in self.S_Col(i)]
            mt_list = self.findMagicTriplets(cell_list)
            for mt_c, mt1, mt2, mt3 in mt_list:
                for cell in cell_list:
                    if cell != mt1 and cell != mt2 and cell != mt3:
                        c_len = len(cell.candidates)
                        cell.candidates -= mt_c
                        num_pruned = c_len - len(cell.candidates)
                        if c_len != len(cell.candidates):
                            self.debugPrint(1, "- pruned " + str(num_pruned) + " from " + str(cell.row_num) + "," + str(cell.col_num) + " for mt: " + str(mt_c))
                            prune_count += num_pruned

        self.metrics['pruneMagicTriplets'] += prune_count
        self.debugPrint(1, 'Total pruned: ' + str(prune_count) + " xxx " + str(self.metrics['pruneMagicTriplets']))
        return prune_count

    def findMagicTriplets(self,cell_list):
        # Given a list of cells from a row/block/col
        # return a list of any magic triplets that it contains
        magic_triplet_list = []
        for i in range(9):
            if not(1 < len(cell_list[i].candidates) < 4):
                continue
            for j in range(i+1, 9):
                if not(1 < len(cell_list[j].candidates) < 4):
                    continue
                for k in range(j+1, 9):
                    if not(1 < len(cell_list[k].candidates) < 4):
                        continue
                    union_candidates = cell_list[i].candidates | cell_list[j].candidates | cell_list[k].candidates
                    if len(union_candidates) == 3:
                        x = [[cell_list[i].row_num, cell_list[i].col_num], [cell_list[j].row_num, cell_list[j].col_num], [cell_list[k].row_num, cell_list[k].col_num]]
                        self.debugPrint(2, str(union_candidates) + ": " + str(x))
                        magic_triplet_list += [[union_candidates, cell_list[i], cell_list[j], cell_list[k]]]
        return magic_triplet_list


    def pruneMagicQuads(self):
        # if any group of four cells in row/col/block contains only four
        # candidates then none of those candidates can appear anywhere else
        # that row/col/block

        # for all blocks
        #   call findMagicQuads and get list of mts
        #   for each mp
        #       prune the two candidates from all other cells in block

        # for all blocks
        #   call findMagicQuads and get list of mts
        #   for each mp
        #       prune the two candidates from all other cells in block

        # for all blocks
        #   call findMagicQuads and get list of mts
        #   for each mp
        #       prune the two candidates from all other cells in block

        # return count of candidates pruned
        self.debugPrint(1, "Start pruneMagicQuads...")
        prune_count = 0
        # Prune Magic Quads from blocks
        for i in range(9):
            cell_list = [cell for cell in self.S_Block(i)]
            mq_list = self.findMagicQuads(cell_list)
            for mq_c, mq1, mq2, mq3, mq4 in mq_list:
                for cell in cell_list:
                    if cell != mq1 and cell != mq2 and cell != mq3 and cell != mq4:
                        c_len = len(cell.candidates)
                        cell.candidates -= mq_c
                        num_pruned = c_len - len(cell.candidates)
                        if c_len != len(cell.candidates):
                            self.debugPrint(1, "- pruned " + str(num_pruned) + " from " + str(cell.row_num) + "," + str(cell.col_num) + " for mq: " + str(mq_c))
                            prune_count += num_pruned

        # Prune Magic Quads from rows
        for i in range(9):
            cell_list = [cell for cell in self.S_Row(i)]
            mq_list = self.findMagicQuads(cell_list)
            for mq_c, mq1, mq2, mq3, mq4 in mq_list:
                for cell in cell_list:
                    if cell != mq1 and cell != mq2 and cell != mq3 and cell != mq4:
                        c_len = len(cell.candidates)
                        cell.candidates -= mq_c
                        num_pruned = c_len - len(cell.candidates)
                        if c_len != len(cell.candidates):
                            self.debugPrint(1, "- pruned " + str(num_pruned) + " from " + str(cell.row_num) + "," + str(cell.col_num) + " for mq: " + str(mq_c))
                            prune_count += num_pruned

        # Prune Magic Quads from cols
        for i in range(9):
            cell_list = [cell for cell in self.S_Col(i)]
            mq_list = self.findMagicQuads(cell_list)
            for mq_c, mq1, mq2, mq3, mq4 in mq_list:
                for cell in cell_list:
                    if cell != mq1 and cell != mq2 and cell != mq3 and cell != mq4:
                        c_len = len(cell.candidates)
                        cell.candidates -= mq_c
                        num_pruned = c_len - len(cell.candidates)
                        if c_len != len(cell.candidates):
                            self.debugPrint(1, "- pruned " + str(num_pruned) + " from " + str(cell.row_num) + "," + str(cell.col_num) + " for mq: " + str(mq_c))
                            prune_count += num_pruned

        self.metrics['pruneMagicQuads'] += prune_count
        self.debugPrint(1, 'Total pruned: ' + str(prune_count) + " xxx " + str(self.metrics['pruneMagicQuads']))
        return prune_count

    def findMagicQuads(self,cell_list):
        # Given a list of cells from a row/block/col
        # return a list of any magic quads that it contains
        magic_quad_list = []
        for i in range(9):
            if not(1 < len(cell_list[i].candidates) < 5):
                continue
            for j in range(i+1, 9):
                if not(1 < len(cell_list[j].candidates) < 5):
                    continue
                for k in range(j+1, 9):
                    if not(1 < len(cell_list[k].candidates) < 5):
                        continue
                    for m in range(k+1, 9):
                        if not(1 < len(cell_list[m].candidates) < 5):
                            continue
                        union_candidates = cell_list[i].candidates | cell_list[j].candidates | cell_list[k].candidates | cell_list[m].candidates
                        if len(union_candidates) == 4:
                            x = [[cell_list[i].row_num, cell_list[i].col_num], [cell_list[j].row_num, cell_list[j].col_num], [cell_list[k].row_num, cell_list[k].col_num], [cell_list[m].row_num, cell_list[m].col_num]]
                            self.debugPrint(2, str(union_candidates) + ": " + str(x))
                            magic_quad_list += [[union_candidates, cell_list[i], cell_list[j], cell_list[k], cell_list[m]]]
        return magic_quad_list


# ----------------------------------------------------- #
class S_Cell:
    def __init__(self, init_val, r, c):
        self.row_num = r
        self.col_num = c
        self.block_num = r // 3 * 3 + c // 3
        self.candidates = set()

        if init_val < 0 or init_val > 9:
            raise Exception("Matrix value is bad")
        self.val = init_val
        if self.val == 0:
            self.candidates = {1,2,3,4,5,6,7,8,9}

    def setVal(self,v):
        self.val = v
        self.candidates = set()

    def setCandidates(self,c_set):
        self.candidates = c_set
