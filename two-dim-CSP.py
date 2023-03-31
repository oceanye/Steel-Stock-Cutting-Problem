import random
from ortools.linear_solver import pywraplp

# Generate random demands in meters
demands = [random.uniform(3, 8) for _ in range(100)]

# Define the problem
solver = pywraplp.Solver('Two-Dimensional Cutting Stock Problem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

# Define the decision variables
x = {}
for i in range(2):
    for j in range(len(demands)):
        x[(i,j)] = solver.IntVar(0, solver.infinity(), f'x[{i},{j}]')

# Define the objective function
solver.Minimize(solver.Sum(x[(i,j)] for i in range(2) for j in range(len(demands))))

# Define the constraints
for j in range(len(demands)):
    solver.Add(8*x[(0,j)] + 12*x[(1,j)] >= demands[j])

# Solve the problem
status = solver.Solve()

# Print the optimal solution
if status == pywraplp.Solver.OPTIMAL:
    print("Optimal Solution:")
    parent_rolls = [0, 0]
    waste = [0, 0]
    for i in range(2):
        roll_length = 12 if i == 0 else 8
        print(f"Parent Roll {i+1} Length: {roll_length} - small rolls :", end=' ')
        rolls = []
        for j in range(len(demands)):
            if int(x[(i,j)].solution_value()) > 0:
                rolls.extend([j+1] * int(x[(i,j)].solution_value()))
                waste[i] += roll_length - int(x[(i,j)].solution_value() * demands[j])
                print(f"{j+1}", end='+')
        print(f" - waste:{waste[i]:.0f}")
        parent_rolls[i] = len(rolls)

    total_parent_rolls = sum(parent_rolls)
    print(f"\n{total_parent_rolls} parent rolls are needed.")
    for i in range(2):
        roll_length = 12 if i == 0 else 8
        print(f"Parent roll {i+1} contains {parent_rolls[i]} small rolls of length {roll_length}.")
    print(f"Total waste: {sum(waste):.0f} meters")
