from pysat.solvers import Glucose3, Solver
from pysat.card import *
import csv
import numpy as np
import random
import sudokuSolver as ss
import time

DUMMY_VAR = 0 # dummy literal
NUMBER_OF_SUDOKUS = 2 # stores the number of sudokus in the sudoku-tuple. since the assignment asks for sudoku pair, it is two by default
sudokus = [] # stores SudokuSolver objects
blank = [] # stores sudoku boards, all filled with zero
cnf = [] # stores the CNF
generating_restrictions = [] # stores the assumptions while generating random puzzle
maximizing_restrictions = [] # stores the assumptions in the finished puzzle

k = int(input("Enter size of sudoku: "))
DUMMY_VAR = k*k*k*k*k*k*NUMBER_OF_SUDOKUS + 1 # the dummy literal is bigger than all relevant literals in the CNF

def no_overlaps(size, n): # adds the clauses to the CNF corresponding to the restriction
                          # that the same cell should not have identical values across the sudoku boards
    cnf = []
    for i in range(size):
        for j in range(size):
            for k in range(size):
                cnf.extend(CardEnc.atmost(lits=((np.array(range(n))*size*size*size) + (i*size*size + j*size + k + 1)).tolist(), bound=1, encoding=EncType.pairwise).clauses)
    return cnf

def random_generate(): # randomly adds clues to the board
    val = 1
    while (val <= k*k): # adding values from 1 to k*k

        flag = True # used for repeating iteration when values clash
        while (flag):
            row = random.randint(1, NUMBER_OF_SUDOKUS*k*k) - 1 # selecting random row
            col = random.randint(1, k*k) - 1 # selecting random column
            id = int(row/(k*k)) # finding sudoku board

            if(sudokus[id].sudoku[(row - id*k*k)][col] != 0): # if a clash occurs
                continue # repeat iteration
                
            sudokus[id].sudoku[(row - id*k*k)][col] = val # else update value
            flag = False # value changed successfuly
        
        val = val + 1 # move onto the next value

def create_maximal(): # creates maximal sudoku from the solution
    for i in range(NUMBER_OF_SUDOKUS*k*k*k*k):
        maximizing_restrictions[i] = -maximizing_restrictions[i] # make the literal false
        if(m.solve(assumptions=maximizing_restrictions)): # check if a solution still exists
            maximizing_restrictions[i] = -maximizing_restrictions[i] # if it does exist, the puzzle loses uniqueness. make it true again
        else: # remove the clue from the board
            tmp = (clue_order[i]) * (k*k)
            loc = ss.SudokuSolver.extract_location(tmp + 1, k*k)
            sudokus[loc[0]].sudoku[loc[1]][loc[2]] = 0
            maximizing_restrictions[i] = DUMMY_VAR # the assumption is removed by changing it to the dummy literal

blank = [[[0 for i in range(k*k)] for j in range(k*k)] for l in range(NUMBER_OF_SUDOKUS)] # initialize blank board

for i in range(NUMBER_OF_SUDOKUS):
    sudokus.append(ss.SudokuSolver(blank[i], k*k, i)) # initialize sudokus

random_generate() # add random clues to tuple
for i in range(NUMBER_OF_SUDOKUS):
        sudokus[i].verify_sudoku() # generate CNF and restrictions
        cnf.extend(sudokus[i].cnf) # merge all CNFs
        generating_restrictions.extend(sudokus[i].restrictions)
    
cnf.extend(no_overlaps(k*k, NUMBER_OF_SUDOKUS)) # extends CNF

m = Solver(name="g3", bootstrap_with=cnf)
m.solve(assumptions=generating_restrictions)

for i in m.get_model(): # finish the sudokus
    if (i < 0):
        continue
    loc = ss.SudokuSolver.extract_location(i, k*k)
    sudokus[loc[0]].sudoku[loc[1]][loc[2]] = loc[3] + 1

#clue_order = np.random.permutation(k*k*k*k*NUMBER_OF_SUDOKUS).tolist() # specify a random order to remove clues to increase randomness
#clue_order = range(k*k*k*k*NUMBER_OF_SUDOKUS) # no randomness in the removal of clues - they are removed one after the other from the start

# comment out from here
head = 0
tail = k*k*k*k*NUMBER_OF_SUDOKUS - 1
clue_order = []
for i in range(k*k*k*k*NUMBER_OF_SUDOKUS): # a pseudorandom order of removing clues. it alernates between the start and the end of the sudoku-tuple
    if (i % 2 == 0):
        clue_order.append(head)
        head = head + 1
    else:
        clue_order.append(tail)
        tail = tail - 1
# to here to try out other clue orders


for i in clue_order:
    i = i * (k*k)
    loc = ss.SudokuSolver.extract_location(i + 1, k*k)
    maximizing_restrictions.append(i + sudokus[loc[0]].sudoku[loc[1]][loc[2]]) # add the true literal to the assumptions list

create_maximal() # create maximal sudoku

for i in range(NUMBER_OF_SUDOKUS):
    sudokus[i].display_sudoku() # display sudokus
    mode = 'a' # append to the file for all but the first iteration
    if(i == 0): # rewrite file for the first iteration
        mode = 'w'
    with open('Q2_Output.csv', mode, newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(sudokus[i].sudoku)

m.delete() # delete solver