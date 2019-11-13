type Operator = "+" | "-" | "*" | "/";
const Operators: Set<Operator> = new Set(["+", "-", "*", "/"]);

type ExprElement = number | Operator;
type Expr = ExprElement[];

type ExprNode = OpNode | number;

function complexity(op: ExprNode): number {
    return typeof op === "number" ? op : op.complexity;
}

function normalize(op: ExprNode): ExprNode {
    return typeof op === "number" ? op : op.normalize();
}

class OpNode {
    private operand1: ExprNode;
    private operand2: ExprNode;
    private op: Operator;

    constructor(op: Operator, operand1: ExprNode, operand2: ExprNode) {
        this.op = op;
        this.operand1 = operand1;
        this.operand2 = operand2;
    }

    public isCommutative(): boolean {
        return this.op === "+" || this.op === "*";
    }

    private gather(): ExprNode[] {
        const res: ExprNode[] = [];
        if (typeof this.operand1 !== "number" && this.operand1.op === this.op) {
            res.push(...this.operand1.gather());
        } else {
            res.push(this.operand1);
        }

        if (typeof this.operand2 !== "number" && this.operand2.op === this.op) {
            res.push(...this.operand2.gather());
        } else {
            res.push(this.operand2);
        }

        res.sort((n1, n2) => complexity(n1) - complexity(n2));
        return res;
    }

    public normalize(): ExprNode {
        const operands = this.gather().map(normalize);
        return operands.reduceRight((node, cur) => {
            return new OpNode(this.op, cur, node);
        });
    }

    public get complexity(): number {
        return complexity(this.operand1) + complexity(this.operand2) + 1000;
    }

    public asExpression(): Expr {
        const operand1: Expr = typeof this.operand1 === "number" ? [this.operand1] : this.operand1.asExpression();
        const operand2: Expr = typeof this.operand2 === "number" ? [this.operand2] : this.operand2.asExpression();
        return [...operand1, ...operand2, this.op];
    }

    public toString() {
        const operand1: string = typeof this.operand1 === "number" ? this.operand1.toString() : `(${this.operand1.toString()})`;
        const operand2: string = typeof this.operand2 === "number" ? this.operand2.toString() : `(${this.operand2.toString()})`;
        return `${operand1} ${this.op} ${operand2}`;
    }
}

function makeSolver(
    target: number,
    operators: Set<Operator>,
    requireAllNumbers: boolean = true
): (numbers: number[]) => IterableIterator<Expr> {

    return function* findSolutions(
        numbers: number[], cur: Expr = [], stack: number[] = []
    ): IterableIterator<Expr> {
        if (stack.length > 0) {
            const val = stack[stack.length - 1];
            // the target is always positive so we can stop if the result goes negative for a bit. there will always be
            // a similar way to get there that does not go negative.
            if (val < 0) {
                return;
            }

            // any time the expression goes fractional for a bit, we can stop. the target is always an integer. if
            // there's a way to get there, there will be a way to express it that does not require fractions. these
            // solutions will be redundant.
            if (!Number.isInteger(val)) {
                return;
            }
        }

        if ((!requireAllNumbers || numbers.length === 0) && stack.length === 1) {
            if (stack[0] === target) {
                yield cur;
            }
        }

        for (let i = 0; i < numbers.length; i++) {
            const nextExpression = [...cur];
            nextExpression.push(numbers[i]);

            const nextNumbers = [...numbers];
            nextNumbers.splice(i, 1);

            const nextStack = [...stack];
            nextStack.push(numbers[i]);

            yield* findSolutions(nextNumbers, nextExpression, nextStack);
        }

        // OpNodes are only valid if the stack has 2 values to pop off
        if (stack.length > 1) {
            for (const op of operators) {
                const nextExpression = [...cur];
                nextExpression.push(op);

                const nextStack = [...stack];
                try {
                    nextStack.push(evaluateElement(op, nextStack));
                    yield* findSolutions(numbers, nextExpression, nextStack);
                } catch (e) {
                }
            }
        }
    }
}


function* generateExprs(
    numbers: number[],
    operators: Set<Operator>,
    requireAllNumbers: boolean = true,
    cur?: Expr,
    stackDepth: number = 0
): IterableIterator<Expr> {
    if (!cur) {
        cur = [];
    }

    if ((!requireAllNumbers || numbers.length === 0) && stackDepth === 1) {
        yield cur;
    }

    for (let i = 0; i < numbers.length; i++) {
        const nextExpression = [...cur];
        nextExpression.push(numbers[i]);

        const nextNumbers = [...numbers];
        nextNumbers.splice(i, 1);

        for (const expr of generateExprs(nextNumbers, operators, requireAllNumbers, nextExpression, stackDepth + 1)) {
            yield expr;
        }
    }

    // OpNodes are only valid if the stack has 2 values to pop off
    if (stackDepth > 1) {
        for (const op of operators) {
            const nextExpression = [...cur];
            nextExpression.push(op);
            for (const expr of generateExprs(numbers, operators, requireAllNumbers, nextExpression, stackDepth - 1)) {
                yield expr;
            }
        }
    }
}

function evaluate(expr: Expr): number {
    const stack: number[] = [];

    for (const el of expr) {
        const next = evaluateElement(el, stack);
        if (!Number.isInteger(next)) {
            throw new Error("expression results in a fraction");
        }
        stack.push(next);
    }

    if (stack.length !== 1) {
        throw new Error("invalid expression");
    }
    return stack[0];
}

function evaluateElement(el: ExprElement, stack: number[]): number {
    if (typeof el === "number") {
        return el;
    }

    const n2: number | undefined = stack.pop();
    const n1: number | undefined = stack.pop();
    if (n1 === undefined || n2 === undefined) {
        throw new Error("invalid expression");
    }

    switch (el) {
        case "+":
            return n1 + n2;
        case "-":
            return n1 - n2;
        case "*":
            return n1 * n2;
        case "/":
            if (n2 === 0) {
                throw new Error("divide by zero");
            }
            return n1 / n2;
        default:
            throw new Error("invalid operator " + el);
    }
}

function toExprNode(expr: Expr): ExprNode {
    const stack: ExprNode[] = [];

    for (const el of expr) {
        if (typeof el === "number") {
            stack.push(el);
        } else {
            const n2: ExprNode | undefined = stack.pop();
            const n1: ExprNode | undefined = stack.pop();
            if (!n1 || !n2) {
                throw new Error("invalid expression");
            }

            stack.push(new OpNode(el, n1, n2));
        }
    }

    if (stack.length !== 1) {
        throw new Error("invalid expression");
    }

    return stack[0];
}

const slns: Set<string> = new Set();
const exprs = makeSolver(619, Operators, false)([25, 3, 8, 6, 10, 4]);
let matches: number = 0;
for (const expr of exprs) {
    const exprNode = toExprNode(expr);
    const normalized = normalize(exprNode);
    if (typeof normalized === "number") {
        slns.add(`${normalized}`);
    } else {
        slns.add(`${normalized.asExpression().join(" ")} == ${normalized.toString()}`);
    }
    matches++;
}
console.log(matches, slns.size);
console.log(slns);
