#!/usr/bin/python

from itertools import combinations_with_replacement, permutations, product
import sys
from decimal import *

def add(s):
    (o2, o1) = (s.pop(), s.pop())
    return o1 + o2

def sub(s):
    (o2, o1) = (s.pop(), s.pop())
    return o1 - o2

def mul(s):
    (o2, o1) = (s.pop(), s.pop())
    return o1 * o2

def div(s):
    (o2, o1) = (s.pop(), s.pop())
    return o1 / o2

operators = [
    { 'type': 'op', 'commutative': True,  'sym': '+', 'run': add },
    { 'type': 'op', 'commutative': False, 'sym': '-', 'run': sub },
    { 'type': 'op', 'commutative': True,  'sym': '*', 'run': mul },
    { 'type': 'op', 'commutative': False, 'sym': '/', 'run': div }
]

# The constant lambda needs to be created in a function because loops don't
# create a scope. Without the function, the closure will capture the loop
# variable, which will always be 9 when we try to run the lambda
def const(n):
    return lambda s: Decimal(n)
numbers = [{ 'type': 'num', 'sym': str(n), 'run': const(n) } for n in range(0, 10)]

def generate_equations(number_set):
    sorted_permutations = sorted(set([ns for ns in permutations(number_set)]))
    prev = None
    for cur in sorted_permutations:
        if cur == prev:
            continue
        prev = cur
        ns = [numbers[c] for c in cur]
        for os in product(operators, repeat=3):
            # 5 possible forms:
            yield [ns[0], ns[1], os[0], ns[2], os[1], ns[3], os[2]]
            yield [ns[0], ns[1], os[0], ns[2], ns[3], os[1], os[2]]
            yield [ns[0], ns[1], ns[2], os[0], ns[3], os[1], os[2]]
            yield [ns[0], ns[1], ns[2], os[0], os[1], ns[3], os[2]]
            yield [ns[0], ns[1], ns[2], ns[3], os[0], os[1], os[2]]

def to_string(eq):
    return ' '.join([e['sym'] for e in eq])

def evaluate_equation(eq, verbose=False):
    def eval_step(stack, eq_element):
        if verbose:
            print "\t\tevaluating %s with stack %s" % (eq_element['sym'], stack)
        result = eq_element['run'](stack)
        stack.append(result)
        return stack
    try:
        return reduce(eval_step, eq, []).pop()
    except ZeroDivisionError:
        return -1

def solve_set(candidate_set):
    solutions = []
    for candidate_equation in generate_equations(candidate_set):
        if evaluate_equation(candidate_equation) == 24:
            solutions.append(candidate_equation)
    return solutions

def solve_all():
    good_sets = 0
    for candidate_set in combinations_with_replacement(range(1, 10), 4):
        solutions = solve_set(candidate_set)
        if len(solutions) > 1:
            solutions_string = '\n\t'.join([to_string(s) for s in solutions])
            print "%s has solutions: \n\t%s" % (candidate_set, solutions_string)
            good_sets += 1

    print "found %s sets with a solution" % (good_sets)


def solve_argv():
    candidate_set = [int(sys.argv[i]) for i in range(1, 5)]
    solutions = solve_set(candidate_set)
    if len(solutions) > 1:
        solutions_string = '\n\t'.join([to_string(s) for s in solutions])
        print "%s has %d solutions: \n\t%s" % (candidate_set, len(solutions), solutions_string)

solve_argv()