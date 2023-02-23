#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Bruce Han <superhxl@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Column generation with Docplex
"""
from docplex.mp.model import Model
import cplex

class CutModel():
    """Cut Problem model solved with column generation"""

    def __init__(self, size, amount, width):
        """Define the cut problem."""
        self.size = size
        self.amount = amount
        self.width = width

        self.pricing_prob = None
        self.pattens = [[0 for _ in range(len(size))]
                        for _ in range(len(size))]
        self.rmp, self.vars, self.ctns = self.create_rmp(size, amount, width)

    def create_rmp(self, size, amount, width):
        """Create the restricted master problem"""
        rmp = Model("rmp")
        var = rmp.continuous_var_list(range(len(size)), name="x")

        rmp.minimize(rmp.sum(var))

        for i in range(len(self.size)):
            self.pattens[i][i] = width // size[i]
        ctns = rmp.add_constraints([(width // size[i]) * var[i] >= amount[i]
                                    for i in range(len(size))])

        return rmp, var, ctns

    def create_pricing_problem(self, size, prices, width):
        """Create the prices problem mdl with prices, and return mdl"""
        mdl = Model("pricing")
        mdl.a = mdl.integer_var_list(
            range(len(size)),
            ub=[width // size[i] for i in range(len(size))],
            name="a")
        mdl.minimize(1 - mdl.dot(mdl.a, prices))
        mdl.add_constraint(mdl.dot(mdl.a, size) <= width)

        return mdl

    def update_pricing_problem(self, prices):
        """Update the prices problem mdl with prices"""
        expr = self.pricing_prob.objective_expr
        updated = [(var, -prices[u])
                   for u, var in enumerate(self.pricing_prob.a)]
        expr.set_coefficients(updated)

    def print_sol(self, sol):
        """Print the cut details in solution sol"""
        print("Current need %d" % sol.objective_value)
        for i, p in enumerate(self.pattens):
            if sol[self.vars[i]] > 0:
                print("\t", p, sol[self.vars[i]])

    def solve(self):
        """Solve the prolbem"""
        iter = 0
        while True:
            iter += 1
            self.rmp.export_as_lp("rmp_%d.lp" % iter)

            sol_rmp = self.rmp.solve()
            if not sol_rmp:
                print("Error, can't find solution.")
                break
            else:
                print("The current cut method is:")
                self.print_sol(sol_rmp)

            prices = self.rmp.dual_values(self.ctns)
            if self.pricing_prob:
                self.update_pricing_problem(prices)
            else:
                self.pricing_prob = self.create_pricing_problem(
                    self.size, prices, self.width)

            self.pricing_prob.export_as_lp("pricing_%d.lp" % iter)
            sol = self.pricing_prob.solve()

            new_pattern = None
            if sol:
                if sol.objective_value < 0:
                    print("The retuced cost is %6.3f" % sol.objective_value)
                    new_pattern = [
                        sol[self.pricing_prob.a[i]]
                        for i in range(len(self.size))
                    ]

            if new_pattern:
                print("New patten found", new_pattern)
                self.pattens.append(new_pattern)
                # Add one new variables, i.e., a new patten
                new_var = self.rmp.continuous_var(name="x_%d" % len(self.vars))
                self.vars.append(new_var)
                # Update constraints
                for n, ct in enumerate(self.ctns):
                    ct.lhs += new_pattern[n] * self.vars[-1]
                # Update objective function
                obj_expr = self.rmp.get_objective_expr()
                obj_expr += self.vars[-1]
            else:
                # No new patten, the best scheme found
                print("The best cut method is:")
                self.print_sol(sol_rmp)
                break


def main():
    width = 12000
    size = (4900, 5235, 7430,3330,4165,2790,3048,3035,4365,4065,4915,4960,250,400)
    amount = (4, 4, 2,4,4,2,2,4,2,4,4,2,12,5)

    m = CutModel(size, amount, width)
    m.solve()




if __name__ == "__main__":
    main()