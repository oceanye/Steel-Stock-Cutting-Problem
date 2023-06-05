from ortools.linear_solver import pywraplp

# The lengths of the orders we need to cut.
order_lengths = [9, 7, 5, 3]

# The quantities of each order.
order_quantities = [5, 7, 3, 8]

# The maximum number of rolls that can be used.
# This should be greater than or equal to the sum of order_quantities.
max_rolls = sum(order_quantities)

# The possible roll lengths.
possible_roll_lengths = [8, 9, 10, 11, 12]

min_waste = float('inf')
min_waste_roll_length = 0
min_quantity = float('inf')

# Iterate over the possible roll lengths.
for roll_length in possible_roll_lengths:

    # Create the linear solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

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

    # Solve the problem.
    result_status = solver.Solve()

    if result_status == pywraplp.Solver.OPTIMAL:
        waste = solver.Objective().Value()
        quantity = sum([use_roll[i].solution_value() for i in range(max_rolls)])
        if waste < min_waste or (waste == min_waste and quantity < min_quantity):
            min_waste = waste
            min_waste_roll_length = roll_length
            min_quantity = quantity

print('Optimal roll length:', min_waste_roll_length)
print('Minimum waste:', min_waste)
print('Minimum quantity:', min_quantity)
