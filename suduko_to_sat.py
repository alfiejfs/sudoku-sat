import os


def formulate_cnf_clauses(grid):
    """
    This function takes an input Suduko grid and will output a list of disjunctive clauses
    that represent the Suduko problem as a CNF problem.

    This has 9 * 9 * 9 = 721 variables (one variable for each number in each possible square).
    """
    return generate_row_clauses() + generate_column_clauses() + generate_box_clauses() \
            + generate_initial_assignment_clauses(grid) + generate_single_assignment_clauses()


def generate_row_clauses():
    """
    This function generates all the CNF clauses for the constraints of each row
    """
    clauses = []
    # Stating that at least one variable in the row j must have number i
    for i in range(1, 10): # i represnting number
        for j in range(9): # j representing row
            clause = [get_variable(j, k, i) for k in range(9)] # k represents column
            clauses.append(clause) 

    # Stating that at most one variable in the row j must have number i
    for i in range(1, 10): # i representing the number
        for j in range(9): # j representing the row
            for k in range(9): # k representing one column
                for l in range(k + 1, 9): # l representing another column
                    if k != l:
                        clauses.append([-get_variable(j, k, i), -get_variable(j, l, i)])

    return clauses


def generate_column_clauses():
    """
    This function generates all the CNF clauses for the constraints of each column
    """
    clauses = []
    # Stating that at least one variable in the column j must have number i
    for i in range(1, 10): # i represnting number
        for j in range(9): # j representing column
            clause = [get_variable(k, j, i) for k in range(9)] # k represents column
            clauses.append(clause) 

    # Stating that at most one variable in the column j must have number i
    for i in range(1, 10): # i representing the number
        for j in range(9): # j representing the column
            for k in range(9): # k representing one row
                for l in range(k + 1, 9): # l representing another row
                    if k != l:
                        clauses.append([-get_variable(k, j, i), -get_variable(l, j, i)])

    return clauses


def generate_box_clauses():
    """
    This function generates all the CNF clauses for the constraints of each 3 by 3 box
    """
    clauses = []
    # Stating that at least one variable in the box j must have number j
    for i in range(1, 10): # i representing number
        for j in range(9): # j representing box index
            clause = [get_box_variable(j, k, i) for k in range(9)] # k represents index into box
            clauses.append(clause) 

    # Stating that at most one variable in the column i must have number j
    for i in range(1, 10): # i representing the number
        for j in range(9): # j representing box index
            for k in range(9): # k representing index into box
                for l in range(k + 1, 9): # l representing another representing index into box
                    if k != l:
                        clauses.append([-get_box_variable(j, k, i), -get_box_variable(j, l, i)])
    
    return clauses


def generate_initial_assignment_clauses(grid):
    """
    This function generates all the DNF clauses to ensure that the solution has the original assignment
    """
    clauses = []
    for i, row in enumerate(grid):
        for j, element in enumerate(row):
            if element is None:
                continue
            clauses.append([get_variable(i, j, element)])
    return clauses


def generate_single_assignment_clauses():
    """
    This function generates all the DNF clauses to ensure that each square only has a single variable
    """
    clauses = []
    
    # Ensuring every cell has at least one variable
    for i in range(9): # represents the row
        for j in range(9): # represents the col
            clause = []
            for k in range(1, 10): # represents the number
                clause.append(get_variable(i, j, k)) # ensuring one of them is true
            clauses.append(clause)

    # Ensuring every cell has at most one variable
    for i in range(9): # represents the row
        for j in range(9): # represents the col
            clause = []
            for k in range(1, 10): # represents the number
                for l in range(k + 1, 10): # represents another number
                    clauses.append([-get_variable(i, j, k), -get_variable(i, j, l)])

    return clauses


def get_box_variable(box_num, index_in_box, number):
    """
    Encodes boxes (0-9) and an index in the box (0-9) to its canonical variable
    """

    # Determine the row and column of the top-left element of the box
    box_row = box_num // 3
    box_col = box_num % 3
    
    # Determine the row and column within the box
    row_in_box = index_in_box // 3
    col_in_box = index_in_box % 3
    
    # Calculate the canonical (x, y) position
    x = box_row * 3 + row_in_box
    y = box_col * 3 + col_in_box
    
    return get_variable(x, y, number)


def get_variable(row, column, number):
    """
    Encodes a row column and number to its corresponding SAT variable.

    NOTE: We want to avoid assigning 0 to a variable (as this is bad for DIMAC format), so we add 1
    """
    return row * 81 + column * 9 + (number - 1) + 1


def get_row_col_num(variable):
    """
    Decodes a SAT variable back to its corresponding row, column, and number.
    """
    variable -= 1  # Undo the addition of 1 in get_variable

    number = variable % 9 + 1
    variable //= 9

    column = variable % 9
    variable //= 9

    row = variable

    return row, column, number


if __name__ == "__main__":
    # Sample grid
    grid = [
        [None, None, None, 3, 2, None, None, None, 4],
        [None, 8, 1, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, 1, None, 7, None, 5, None],
        [2, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, 8, None, None, None],
        [4, 2, None, None, 6, None, None, None, None],
        [None, None, None, None, None, None, 9, 1, None],
        [6, None, None, None, None, None, 3, None, None]
    ]

    cnf = formulate_cnf_clauses(grid)
    
    with open("output.txt", "w") as file:
        for clause in cnf:
            file.write(" ".join(map(str, clause)) + " 0\n")

    print(f"DIMACS CNF formula generated with {len(cnf)} clauses. Output in output.txt.")

    if not os.path.exists("input.txt"):
        print("No input to check. Exiting.")

    """
    Format of input is the solution copied from https://msoos.github.io/cryptominisat_web/.
    """
    with open("input.txt", "r") as file:
        lines = map(lambda line: line.strip()[2:], file.readlines())
        variables = map(int, " ".join(lines).split(" "))
        assignments = filter(lambda v: v > 0, variables)

        for assignment in assignments:
            row, column, number = get_row_col_num(assignment)
            grid[row][column] = number

        for line in grid:
            print(" ".join(map(str, line)))
        