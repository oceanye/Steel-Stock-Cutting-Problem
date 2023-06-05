from itertools import combinations
from ortools.linear_solver import pywraplp

# The lengths of the orders we need to cut.
order_lengths = [9, 7, 5, 3, 4]

# The quantities of each order.
order_quantities = [5, 7, 3, 8, 20]

# The maximum number of rolls that can be used.
# This should be greater than or equal to the sum of order_quantities.
max_rolls = sum(order_quantities)

# The possible roll lengths.
possible_roll_lengths = [8, 9, 10, 11, 12]

min_waste = float('inf')
min_waste_roll_lengths = []
min_quantity = float('inf')
optimal_roll_arrangement = []

# Iterate over all combinations of two roll lengths
for roll_length_comb in combinations(possible_roll_lengths, 2):

    # Create the linear solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Decision variables: whether to use a roll or not, and how many of each order to cut from the roll.
    use_roll = []
    cut_orders = []

    for i in range(max_rolls):
        use_roll.append([])
        cut_orders.append([])
        for k in range(2):  # Two roll lengths in the combination
            use_roll[i].append(solver.IntVar(0, 1, 'use_roll[%i][%i]' % (i, k)))
            cut_orders[i].append([])
            for j in range(len(order_lengths)):
                cut_orders[i][k].append(solver.IntVar(0, 1, 'cut_orders[%i][%i][%i]' % (i, k, j)))

    # Constraint: Each order's quantity must be satisfied.
    for j in range(len(order_lengths)):
        solver.Add(solver.Sum([cut_orders[i][k][j] for i in range(max_rolls) for k in range(2)]) >= order_quantities[j])

    # Constraint: The total length cut from a roll must not exceed the roll's length.
    # Also, a roll can only be of one type.
    for i in range(max_rolls):
        for k in range(2):
            solver.Add(solver.Sum([cut_orders[i][k][j] * order_lengths[j] for j in range(len(order_lengths))]) <= roll_length_comb[k] * use_roll[i][k])
        solver.Add(solver.Sum([use_roll[i][k] for k in range(2)]) <= 1)

    # Objective: Minimize the waste.
    # Waste for each roll is the roll length minus the sum of the lengths of the cuts from the roll.
    solver.Minimize(solver.Sum([use_roll[i][k] * roll_length_comb[k] - solver.Sum([cut_orders[i][k][j] * order_lengths[j] for j in range(len(order_lengths))]) for i in range(max_rolls) for k in range(2)]))

    # Solve the problem.
    result_status = solver.Solve()

    if result_status == pywraplp.Solver.OPTIMAL:
        waste = solver.Objective().Value()
        quantity = sum([use_roll[i][k].solution_value() for i in range(max_rolls) for k in range(2)])
        if waste < min_waste or (waste == min_waste and quantity < min_quantity):
            min_waste = waste
            min_waste_roll_lengths = roll_length_comb
            min_quantity = quantity
            optimal_roll_arrangement = [[cut_orders[i][k][j].solution_value() for j in range(len(order_lengths))] for i in range(max_rolls) for k in range(2)]

print('Optimal roll lengths:', min_waste_roll_lengths)
print('Minimum waste:', min_waste)
print('Minimum quantity:', min_quantity)
print('Roll arrangement:')
for i in range(max_rolls):
    if sum(optimal_roll_arrangement[i]) > 0:
        print('Roll', i+1, 'used with cuts:')
        for j in range(len(order_lengths)):
            if optimal_roll_arrangement[i][j] > 0:
                print('  Order of length', order_lengths[j], 'x', optimal_roll_arrangement[i][j])
print('Total waste:', min_waste * min_quantity)
