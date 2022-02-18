from base64 import decode
from cmath import sqrt
from pysat.solvers import Glucose3, Solver
from pysat.card import *
import csv
import numpy as np
import sudokuSolver as ss

def no_overlaps(size, n): # adds the clauses to the CNF corresponding to the restriction
                          # that the same cell should not have identical values across the sudoku boards
    cnf = []
    for i in range(size):
        for j in range(size):
            for k in range(size):
                cnf.extend(CardEnc.atmost(lits=((np.array(range(n))*size*size*size) + (i*size*size + j*size + k + 1)).tolist(), bound=1, encoding=EncType.pairwise).clauses)
    return cnf

contents = [] # stores contents of the csv file
cnf = [] # stores the final CNF
restrictions = [] # stores the assumptions
sudokus = [] # stores SudokuSolver objects 
csv_sudoku = "TestCases/sudoku1.csv" # stores file name

file = open(csv_sudoku) # storing csv file into the contents array
csvreader = csv.reader(file)
for row in csvreader:
    contents.append(row)
file.close()

n_sudokus = int(len(contents)/len(contents[0])) # number of sudokus can be determined by dividing number of rows by number of columns
k = int(input("Enter size of sudoku: ")) # size of sudoku is the number of elements in one row
size = len(contents[0]) # length of row in a sudoku puzzle

for i in range(n_sudokus): 
    sudokus.append(ss.SudokuSolver(contents[i*size:(i+1)*size], size, i)) # initialize sudoku boards
    sudokus[i].verify_sudoku() # get their assumptions and CNF

    cnf.extend(sudokus[i].cnf) # merge the CNF across all boards
    restrictions.extend(sudokus[i].restrictions) # merge the assumptions across all boards

cnf.extend(no_overlaps(size, n_sudokus)) # add the additional clauses

m = Solver(name="g3", bootstrap_with=cnf)
result = m.solve(assumptions=restrictions) # solve with assumptions

if(result): # if the sudoku has a model
    for i in m.get_model(): # decoding the results
        if (i < 0): # if negative literal, it does not appear in the board
            continue
        loc = ss.SudokuSolver.extract_location(i, size) # decoding location from literal value
        sudokus[loc[0]].sudoku[loc[1]][loc[2]] = loc[3] + 1 # updating sudoku boards
    
    for i in range(n_sudokus): 
        sudokus[i].display_sudoku() # display all boards
else:
    print("No solutions") # no solutions

m.delete() # delete solver