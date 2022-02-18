Ensure that all the contents of the zip folder remain in the same folder.

In the first question (Q1.py), when the code is executed, it prompts the user for the size of the sudoku, and by default has “TestCase/sudoku1.csv” as the sudoku input. To change the input it must be done in the source code itself (Q1.py - line number - 22 - csv_sudoku variable). Even if the value of size of sudoku(k) is given wrong our code will print out the solved sudoku pair nevertheless, because it extracts the size from the csv file. Run the code in Terminal so that you can interact with the code.

In the second question (Q2.py), when the code is executed, it prompts the user for the size of sudoku(k) and then gives out the sudoku pair (unsolved) in the terminal as well as the output file (Q2_Output.csv). To solve a sudoku-tuple instead of a pair, you can change it from the source code (Q2.py - line number - 9 - NUMBER_OF_SUDOKUS variable).
