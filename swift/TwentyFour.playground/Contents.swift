import UIKit

enum Op {
    case num(Int)
    case add
    case sub
    case mul
    case div
}

struct State {
    var ops: [Op] = []
    var stack: [Int] = []
}

func findTarget(state: State, input: [Int], target: Int) -> State? {
    if state.stack.count == 1 && state.stack[0] == target {
        return state
    }
    
    if state.stack.count >= 2 {
        for op in [Op.add, Op.sub, Op.mul, Op.div] {
            var nextState = state
            let op1 = nextState.stack.removeLast()
            let op2 = nextState.stack.removeLast()
            switch op {
            case .add: nextState.stack.append(op1 + op2)
            case .sub: nextState.stack.append(op1 - op2)
            case .mul: nextState.stack.append(op1 * op2)
            case .div:
                if op2 == 0 || op1 % op2 != 0 {
                    return nil
                }
                else {
                    nextState.stack.append(op1 / op2)
                }
            case .num(let num): nextState.stack.append(num)
            }
            nextState.ops.append(op)
            if let answer = findTarget(state: nextState, input: input, target: target) {
                return answer
            }
        }
    }
    
    for num in 0..<input.count {
        var nextInput = input
        let nextNum = nextInput.remove(at: num)
        
        var nextState = state
        nextState.stack.append(nextNum)
        nextState.ops.append(.num(nextNum))
        if let answer = findTarget(state: nextState, input: nextInput, target: target) {
            return answer
        }
    }
    
    return nil
}


let input = [25, 75, 50, 100, 3, 6]
let target = 952
let s1 = State()

if let s2 = findTarget(state: s1, input: input, target: target) {
    var parts: [String] = []
    for i in s2.ops {
        switch i {
        case .add: parts.append("+")
        case .sub: parts.append("-")
        case .mul: parts.append("*")
        case .div: parts.append("/")
        case .num(let num): parts.append("\(num)")
        }
    }
    print(parts.joined(separator: " "))
}
else {
    print("No solution!")
}
