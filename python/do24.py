from collections import defaultdict
from functools import cmp_to_key

import itertools


class Node:
    @staticmethod
    def parse(expr):
        stack = []
        for pos, elt in enumerate(expr):
            if type(elt) == int:
                stack.append(ConstNode(elt))
            elif len(stack) < 2:
                return None
            else:
                arg1 = stack.pop()
                arg2 = stack.pop()
                if elt == '+':
                    stack.append(AdditionNode(arg2, arg1))
                elif elt == '-':
                    stack.append(SubtractionNode(arg2, arg1))
                elif elt == '*':
                    stack.append(MultiplicationNode(arg2, arg1))
                elif elt == '/':
                    stack.append(DivisionNode(arg2, arg1))
                else:
                    return None

        if len(stack) != 1:
            return None

        return stack[0]

    def evaluate(self):
        pass

    def normalize(self):
        return self

    def as_tuple(self):
        pass


class ConstNode(Node):
    sort_order = 0

    def __init__(self, value):
        if type(value) != int:
            raise TypeError(f"invalid constant {value}")
        self.value = value

    def evaluate(self):
        return self.value

    def as_tuple(self):
        return self.value,

    def as_string(self):
        return str(self.value)


class OperatorNode(Node):
    def __init__(self, arg1, arg2, op):
        if not isinstance(arg1, Node) or not isinstance(arg2, Node):
            raise TypeError("arguments must be Nodes")

        self.arg1 = arg1
        self.arg2 = arg2
        self.op = op

    def find_similar_operands(self, node, accum):
        if isinstance(node, self.__class__):
            self.find_similar_operands(node.arg1, accum)
            self.find_similar_operands(node.arg2, accum)
        else:
            accum.append(node)

    def as_tuple(self):
        return (*self.arg1.as_tuple(), *self.arg2.as_tuple(), self.op)

    def as_string(self):
        operands = []
        self.find_similar_operands(self.arg1, operands)
        self.find_similar_operands(self.arg2, operands)
        return "(" + f" {self.op} ".join(op.as_string() for op in operands) + ")"

class CommutativeNode(OperatorNode):
    def __init__(self, arg1, arg2, op):
        super(CommutativeNode, self).__init__(arg1, arg2, op)


class NonCommutativeNode(OperatorNode):
    def __init__(self, arg1, arg2, op):
        super(NonCommutativeNode, self).__init__(arg1, arg2, op)


class AdditionNode(CommutativeNode):
    sort_order = 1

    def __init__(self, arg1, arg2):
        super(AdditionNode, self).__init__(arg1, arg2, "+")

    def evaluate(self):
        v1 = self.arg1.evaluate()
        v2 = self.arg2.evaluate()
        return v1 + v2

    def normalize(self):
        arg1 = self.arg1.normalize()
        arg2 = self.arg2.normalize()

        operands = []
        self.find_similar_operands(arg1, operands)
        self.find_similar_operands(arg2, operands)

        def compare(op1, op2):
            if op1.sort_order != op2.sort_order:
                return op1.sort_order - op2.sort_order
            if isinstance(op1, ConstNode) and isinstance(op2, ConstNode):
                return op1.value - op2.value
            return op1.evaluate() - op2.evaluate()

        sorted_operands = sorted(operands, key=cmp_to_key(compare))

        next = AdditionNode(sorted_operands[0], sorted_operands[1])
        for op in sorted_operands[2:]:
            next = AdditionNode(next, op)
        return next


class MultiplicationNode(CommutativeNode):
    sort_order = 2

    def __init__(self, arg1, arg2):
        super(MultiplicationNode, self).__init__(arg1, arg2, "*")

    def evaluate(self):
        return self.arg1.evaluate() * self.arg2.evaluate()

    def normalize(self):
        arg1 = self.arg1.normalize()
        arg2 = self.arg2.normalize()

        if isinstance(arg1, ConstNode) and arg1.value == 1:
            return arg2
        elif isinstance(arg2, ConstNode) and arg2.value == 1:
            return arg1

        operands = []
        self.find_similar_operands(arg1, operands)
        self.find_similar_operands(arg2, operands)

        def compare(op1, op2):
            if op1.sort_order != op2.sort_order:
                return op1.sort_order - op2.sort_order
            if isinstance(op1, ConstNode) and isinstance(op2, ConstNode):
                return op1.value - op2.value
            return op1.evaluate() - op2.evaluate()

        sorted_operands = sorted(operands, key=cmp_to_key(compare))

        next = MultiplicationNode(sorted_operands[0], sorted_operands[1])
        for op in sorted_operands[2:]:
            next = MultiplicationNode(next, op)

        return next


class SubtractionNode(NonCommutativeNode):
    sort_order = 1

    def __init__(self, arg1, arg2):
        super(SubtractionNode, self).__init__(arg1, arg2, "-")

    def evaluate(self):
        return self.arg1.evaluate() - self.arg2.evaluate()

    def normalize(self):
        arg1 = self.arg1.normalize()
        arg2 = self.arg2.normalize()
        return SubtractionNode(arg1, arg2)


class DivisionNode(NonCommutativeNode):
    sort_order = 4

    def __init__(self, arg1, arg2):
        super(DivisionNode, self).__init__(arg1, arg2, "/")

    def evaluate(self):
        return self.arg1.evaluate() / self.arg2.evaluate()

    def normalize(self):
        arg1 = self.arg1.normalize()
        arg2 = self.arg2.normalize()
        if isinstance(arg2, ConstNode) and arg2.value == 1:
            return arg1
        return DivisionNode(arg1, arg2)


def evaluate(expr):
    stack = []
    for pos, elt in enumerate(expr):
        if type(elt) == int:
            stack.append(elt)
        elif len(stack) < 2:
            return None
        else:
            arg1 = stack.pop()
            arg2 = stack.pop()
            if elt == '+':
                stack.append(arg2 + arg1)
            elif elt == '-':
                stack.append(arg2 - arg1)
            elif elt == '*':
                stack.append(arg2 * arg1)
            elif elt == '/':
                if arg1 == 0:
                    return None
                if arg2 % arg1 != 0:
                    return None
                stack.append(arg2 / arg1)
            else:
                return None

    if len(stack) != 1:
        return None

    return stack[0]


def stringify(expr):
    stack = []
    for pos, elt in enumerate(expr):
        if type(elt) == int:
            stack.append(str(elt))
        elif len(stack) < 2:
            return None
        else:
            arg2 = stack.pop()
            arg1 = stack.pop()
            stack.append(f"({arg1} {elt} {arg2})")

    if len(stack) != 1:
        return None

    return stack[0]


ops = ['+', '-', '*', '/']


def main():
    num_digits = 4
    digits = range(1, 10)
    target = 24

    ops_perms = list(itertools.product(ops, repeat=num_digits - 1))
    digit_perms = list(itertools.product(digits, repeat=num_digits))

    for digit_perm in digit_perms:
        print_hits(digit_perm, ops_perms, target)


def main_one(digit_perm, target):
    num_digits = len(digit_perm)
    ops_perms = list(itertools.product(ops, repeat=num_digits - 1))

    print_hits(digit_perm, ops_perms, target)


def print_hits(digit_perm, ops_perms, target):
    # print(f"TRYING: {digit_perm}")
    all_exprs = set()
    for ops_perm in ops_perms:
        exprs = (digit_perm[:2] + perm for perm in itertools.permutations(digit_perm[2:] + ops_perm))
        for expr in exprs:
            all_exprs.add(expr)
    hits = [expr for expr in all_exprs if evaluate(expr) == target]

    if len(hits) > 0:
        # normalized = defaultdict(list)
        # for hit in hits:
        #     node = Node.parse(hit)
        #     normed = node.normalize()
        #     tup = normed.as_tuple()
        #     normalized[tup].append(node)
        #
        # print(f"HIT: {digit_perm} - (len {len(normalized)})")
        # for _, hit in normalized.items():
        #     h = hit[0].normalize()
        #     print(f"\t{h.as_tuple()} :: {h.as_string()} has {len(hit)} similar solutions")
        #     for h in hit:
        #         print(f"\t\t{h.as_tuple()} :: {h.as_string()}")

        print(f"HIT: {digit_perm} - (len {len(hits)})")
        # for hit in hits:
        #     print(f"\t{hit} :: {stringify(hit)}")


if __name__ == "__main__":
    # print(f"normalize([2, 1, '+', 3, '+', 3, '-']) = {normalize([2, 1, '+', 3, '+', 3, '-'])}")
    # print(f"normalize([1, 2, '+', 3, '+', 3, '-']) = {normalize([1, 2,  3, '+', '+', 3, '-'])}")
    # print(f"normalize([1, 3, '+', 2, '+', 3, '-']) = {normalize([1, 3, '+', 2, '+', 3, '-'])}")
    # main_one((1, 2, 1, 8), 24)
    # main_one((1, 1, 6, 2), 24)
    main()
