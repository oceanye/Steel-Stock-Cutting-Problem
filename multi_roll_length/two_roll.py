from ortools.linear_solver import pywraplp

# Create the linear solver with the SCIP backend.
solver = pywraplp.Solver.CreateSolver('SCIP_MIXED_INTEGER_PROGRAMMING')

# The lengths of the rolls we have.
roll_lengths = [12000, 10000]

# The lengths of the orders we need to cut.
#order_lengths = [805, 803, 8743, 8668, 2903, 2203, 2253, 2533, 2083, 1433, 3333, 1453, 3266]
order_lengths = [805, 803, 8743, 8668, 2903, 2203, 2253]

# The quantities of each order.
order_quantities = [10,12,1,15,2,3,15]
#order_quantities = [1, 3, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1]

# The maximum number of rolls that can be used.
# This should be greater than or equal to the sum of order_quantities.
max_rolls = sum(order_quantities)

# Decision variables: whether to use a roll of each type or not, and how many of each order to cut from the roll.
use_roll = []
cut_orders = []



for i in range(max_rolls):
    use_roll.append([])
    cut_orders.append([])
    for k in range(len(roll_lengths)):
        use_roll[i].append(solver.IntVar(0, 1, 'use_roll[%i][%i]' % (i, k)))
        cut_orders[i].append([])
        for j in range(len(order_lengths)):
            cut_orders[i][k].append(solver.IntVar(0, order_quantities[j], 'cut_orders[%i][%i][%i]' % (i, k, j)))



# Constraint: A roll can't be used for an order if the order is longer than the roll.
for i in range(max_rolls):
    for k in range(len(roll_lengths)):
        for j in range(len(order_lengths)):
            if order_lengths[j] > roll_lengths[k]:
                solver.Add(cut_orders[i][k][j] == 0)

# Constraint: Each order's quantity must be satisfied.
for j in range(len(order_lengths)):
    solver.Add(solver.Sum([cut_orders[i][k][j] for i in range(max_rolls) for k in range(len(roll_lengths))]) == order_quantities[j])

# Constraint: The total length cut from a roll must not exceed the roll's length.
# Also, a roll can only be of one type.
for i in range(max_rolls):
    for k in range(len(roll_lengths)):
        solver.Add(solver.Sum([cut_orders[i][k][j] * order_lengths[j] for j in range(len(order_lengths))]) <= roll_lengths[k] * use_roll[i][k])
    solver.Add(solver.Sum([use_roll[i][k] for k in range(len(roll_lengths))]) <= 1)

# Objective: Minimize the waste.
solver.Minimize(solver.Sum([use_roll[i][k] * roll_lengths[k] - solver.Sum([cut_orders[i][k][j] * order_lengths[j] for j in range(len(order_lengths))]) for i in range(max_rolls) for k in range(len(roll_lengths))]))



# Solve the problem and print the solution.
result_status = solver.Solve()

if result_status == pywraplp.Solver.OPTIMAL:
    print('Solution found.')
    print('Minimum waste = ', solver.Objective().Value())
    total_waste = 0
    for i in range(max_rolls):
        for k in range(len(roll_lengths)):
            if use_roll[i][k].solution_value() > 0:
                print('Roll', i, 'of length', roll_lengths[k], 'used with cuts:')
                total_cut_length = 0
                for j in range(len(order_lengths)):
                    if cut_orders[i][k][j].solution_value() > 0:
                        print('  Order of length', order_lengths[j], 'x', cut_orders[i][k][j].solution_value())
                        total_cut_length += order_lengths[j] * cut_orders[i][k][j].solution_value()
                waste = roll_lengths[k] - total_cut_length
                total_waste += waste
                print('  Waste for this roll:', waste)
    print('Total waste:', total_waste)
else:
    print('No solution found.')
