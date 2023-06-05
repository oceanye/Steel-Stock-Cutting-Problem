from ortools.linear_solver import pywraplp

# Create the linear solver with the SCIP backend.
solver = pywraplp.Solver.CreateSolver('SCIP')

# The length of the rolls we have.
roll_length = 10

# The lengths of the orders we need to cut.
order_lengths = [9, 7, 5, 3]

# The quantities of each order.
order_quantities = [5, 7, 3, 8]

# The maximum number of rolls that can be used.
# This should be greater than or equal to the sum of order_quantities.
max_rolls = sum(order_quantities)

# Decision variables: whether to use a roll or not, and how many of each order to cut from the roll.
use_roll = []
cut_orders = []

for i in range(max_rolls):
    use_roll.append(solver.IntVar(0, 1, 'use_roll[%i]' % i))
    cut_orders.append([])
    for j in range(len(order_lengths)):
        cut_orders[i].append(solver.IntVar(0, 1, 'cut_orders[%i][%i]' % (i, j)))

# Constraint: Each order's quantity must be satisfied.
for j in range(len(order_lengths)):
    solver.Add(solver.Sum([cut_orders[i][j] for i in range(max_rolls)]) >= order_quantities[j])

# Constraint: The total length cut from a roll must not exceed the roll's length.
for i in range(max_rolls):
    solver.Add(solver.Sum([cut_orders[i][j] * order_lengths[j] for j in range(len(order_lengths))]) <= roll_length * use_roll[i])

# Objective: Minimize the waste.
# Waste for each roll is the roll length minus the sum of the lengths of the cuts from the roll.
solver.Minimize(solver.Sum([use_roll[i] * roll_length - solver.Sum([cut_orders[i][j] * order_lengths[j] for j in range(len(order_lengths))]) for i in range(max_rolls)]))

# Solve the problem and print the solution.
result_status = solver.Solve()

if result_status == pywraplp.Solver.OPTIMAL:
    print('Solution found.')
    print('Minimum waste = ', solver.Objective().Value())
    total_waste = 0
    for i in range(max_rolls):
        if use_roll[i].solution_value() > 0:
            print('Roll', i, 'used with cuts:')
            total_cut_length = 0
            for j in range(len(order_lengths)):
                if cut_orders[i][j].solution_value() > 0:
                    print('  Order of length', order_lengths[j], 'x', cut_orders[i][j].solution_value())
                    total_cut_length += order_lengths[j] * cut_orders[i][j].solution_value()
            waste = roll_length - total_cut_length
            total_waste += waste
            print('  Waste for this roll:', waste)
    print('Total waste:', total_waste)
else:
    print('No solution found.')
