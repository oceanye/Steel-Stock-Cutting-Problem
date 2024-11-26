from ortools.linear_solver import pywraplp

def solve_cutting_stock(wanted_list, stock_length):
    solver = pywraplp.Solver.CreateSolver('SCIP')

    num_wanted = len(wanted_list)
    num_stock = [solver.NumVar(0, solver.infinity(), 'stock{}'.format(i)) for i in range(num_wanted)]

    objective = solver.Objective()
    for i in range(num_wanted):
        objective.SetCoefficient(num_stock[i], 1)
    objective.SetMinimization()

    # Constraints
    for i in range(num_wanted):
        constraint = solver.Constraint(wanted_list[i][0], wanted_list[i][0])
        constraint.SetCoefficient(num_stock[i], stock_length / wanted_list[i][1])

    solver.Solve()

    solution = []
    for i in range(num_wanted):
        quantity = num_stock[i].solution_value()
        remaining_length = stock_length - (quantity * wanted_list[i][1])
        combined_length = [wanted_list[i][1]] * int(quantity)
        total_length = stock_length * quantity
        solution.append([remaining_length, combined_length, total_length])

    return solution

# Example usage
wanted_list = [(3, 3), (4, 2)]  # List of desired quantities and lengths of smaller bars
stock_length = 6  # Length of the parent stock bar

solution = solve_cutting_stock(wanted_list, stock_length)
print("Cutting pattern:")
total_parent_length = 0
for i, result in enumerate(solution):
    remaining_length = result[0]
    combined_length = result[1]
    total_length = result[2]
    total_parent_length += total_length
    print(f"Split {i+1}: Remaining Length: {remaining_length}m, Combined Length: {combined_length}, Total Length: {total_length}m")

print(f"Total Parent Length Used: {total_parent_length}m")
