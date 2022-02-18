from base64 import decode
from cmath import sqrt
import csv
import numpy as np
from pysat.solvers import Glucose3, Solver
from pysat.card import *

class SudokuSolver:

    # class to solve individual sudoku puzzles. it can generate the CNF based on the restrictions of a standard sudoku puzzle

    # encoding of literals is done by taking a 4-digit number base k*k and converting it to decimal. the most significant digit encodes
    # the sudoku number. the next digit encodes the row. the next digit encodes the column. the next digit encodes the possible value
    # of the square
    @staticmethod
    def extract_index(size, id, i, j, k):
        return (size*size*size*id + size*size*i + size*j + k + 1) # an offset of 1 is given to ensure that a literal does not get 0 value which is
                                                                  # illegal for PySat

    # decodes the literal value to a cell location on the sudoku board.
    @staticmethod
    def extract_location(val, size):
        id = int((val - 1)/(size*size*size))
        val = (val - 1) % (size*size*size)
        return (id, int(val/(size*size)), int((val/size) % size), int(val % size)) # returns (id, row, column, value)
    
    def __init__(self, sudoku, size, id): # constructor to initialize the object
        self.sudoku = sudoku # stores the sudoku board
        self.cnf = [] # stores the CNF
        self.restrictions = [] # stores the assumptions to be given to the CNF based on already filled squares of the board

        self.id = id # stores which sudoku board is being solved
        self.size = size # stores the size of the board (size = k*k)
        self.size_r = int(size ** 0.5) # stores the value of k
    
    def encode_restrictions(self, i, j): # encodes the assumptions based on the value at the (i, j)th square of the board
        res = [] # stores the literals
        for n in range(self.size):
            if(int(self.sudoku[i][j]) == n + 1): # finds the value of the (i, j)th square
                res.append(SudokuSolver.extract_index(self.size, self.id, i, j, n)) # if matched, set the corresponding literal to true
            else:
                res.append(-SudokuSolver.extract_index(self.size, self.id, i, j, n)) # else the literal must be false
        return res # returns the list of literals 
    
    def verify_cell(self): # encodes the CNF based on the condition that no cell should contain more than one value
        for i in range(self.size): # iterates over rows
            for j in range(self.size): # iterates over columns
                self.cnf.extend(CardEnc.equals(lits=(np.array(range(self.size)) + SudokuSolver.extract_index(self.size, self.id, i, j, 0)).tolist(), encoding=EncType.pairwise).clauses)
                # using the CardEnc.equals() function to ensure that exactly one literal out of the given list of literals is true 
    
    def verify_row(self): # encodes the CNF based on the condition that every row should contain all the k*k values
        for i in range(self.size): # iterates over rows
            for j in range(self.size): # iterates over values
                self.cnf.extend(CardEnc.equals(lits=(np.array(range(self.size))*self.size + SudokuSolver.extract_index(self.size, self.id, i, 0, j)).tolist(), encoding=EncType.pairwise).clauses)
                # using the CardEnc.equals() function to ensure that exactly one literal out of the given list of literals is true
    
    def verify_col(self): # encodes the CNF based on the condition that every column should contain all the k*k values
        for i in range(self.size): # iterates over columns
            for j in range(self.size): # iterates over values
                self.cnf.extend(CardEnc.equals(lits=(np.array(range(self.size))*self.size*self.size + SudokuSolver.extract_index(self.size, self.id, 0, i, j)).tolist(), encoding=EncType.pairwise).clauses)
                # using the CardEnc.equals() function to ensure that exactly one literal out of the given list of literals is true

    def verify_sub_block(self): # encodes the CNF based on the condition that every sub-block should contain all the k*k values
        for i_sb in range(self.size_r): # iterates over sub-block rows
            for j_sb in range(self.size_r): # iterates over sub_block columns
                cells = [] # stores the literals over which the restriction holds
                for i_r in range(self.size_r): # iterates over the rows inside the sub-block
                    for j_c in range(self.size_r): # iterates over the columns inside the sub-block
                        cells.append(SudokuSolver.extract_index(self.size, self.id, i_sb*self.size_r + i_r, j_sb*self.size_r + j_c, 0)) # set of literals belonging to one sub-block
                
                for n in range(self.size): # iterates over values
                    self.cnf.extend(CardEnc.equals(lits=(np.array(cells) + n).tolist(), encoding=EncType.pairwise).clauses)
                    # using the CardEnc.equals() function to ensure that exactly one literal out of the given list of literals is true

    
    def verify_sudoku(self): # wrapper function which encodes all the assumptions and builds the main CNF
        for i in range(0, self.size):
            for j in range(0, self.size):
                if(int(self.sudoku[i][j]) != 0): # if a clue is given
                    self.restrictions.extend(self.encode_restrictions(i, j)) # encoding all clues across the board
        self.verify_cell()      # build cnf
        self.verify_col()       # build cnf
        self.verify_row()       # build cnf
        self.verify_sub_block() # build cnf
    
    def display_sudoku(self): # displays the sudoku
        print("The Sudoku {0} board is: ".format(self.id + 1))
        print()
        for i in range(self.size):
            if(i != 0 and i % self.size_r == 0):
                for l in range(4*self.size + 3*self.size_r + 1):
                    print("-", end="")
                print()
                
            print(end="[  ")
            for j in range(self.size):
                if(j % self.size_r == 0 and j != 0):
                    print("|  ", end = "")
                if(int(self.sudoku[i][j]/10) == 0):
                    print(end=" ")
                print(self.sudoku[i][j], end="  ")
            print("]")
        print()
        print()