"""
operators: + - * / % ^
parenthesis
unary negation -x, --x, -(x + y), x * -y etc
no unary +
implicit multiplication

precedence:
^,
unary -,
* / % and implicit multiplication,
+ -

useful links
https://en.wikipedia.org/wiki/Binary_expression_tree
"""

operators = "+-*/%^"

def tokenise(e: str) -> list[list]:
    tokens = []

    # split into tokens [TYPE : VALUE] end with [END]

    l = len(e)
    i = 0

    while i < l:
        char = e[i]

        if char.isdigit():
            start = i

            while i + 1 < l and e[i + 1].isdigit():
                i += 1

            if i < l and e[i] == '.':
                i += 1

                while i + 1 < l and e[i + 1].isdigit():
                    i += 1

            tokens.append(["NUM", e[start : i + 1]])

        elif char in operators:
            tokens.append(["OP", char])

        elif char == '(':
            tokens.append(["LPAREN", char])

        elif char == ')':
            tokens.append(["RPAREN", char])

        else:
            if not char.isspace():
                print(f"Invalid character: '{char}'")
                return ["ERROR"]

        i += 1

    tokens.append(["END"])

    return tokens

def evaluate_tree(node: dict):
    if node["type"] == "number":
        return node["value"]

    if node["type"] == "unary":
        return -node["value"]

    if node["type"] == "operation":
        left, right = evaluate_tree(node["left"]), evaluate_tree(node["right"])

        if node["op"] == "+": return left + right
        if node["op"] == "-": return left - right
        if node["op"] == "*": return left * right
        if node["op"] == "/": return left / right
        if node["op"] == "%": return left % right
        if node["op"] == "^": return left ** right

def display_tree(node: dict):
    if node["type"] == "number":
        return str(node["value"])

    if node["type"] == "unary":
        return f"(neg {node["value"]})"

    if node["type"] == "operation":
        return f"({node["op"]} {display_tree(node["left"])} {display_tree(node["right"])})"

#region Ideas and testing

"""
the goal is to create one large dictionary to be the tree, example:

expression: 3 + 5 * 2

tree = {
    "type": "operation",
    "op": "+",
    "left": {
        "type": "number",
        "value": 3
    },
    "right": {
        "type": "operation",
        "op": "*",
        "left": {
            "type": "number",
            "value": 5
        },
        "right": {
            "type": "number",
            "value": 2
        },
    }
}

or maybe numbers can be simplified, and the recursive evaluator checks first if it is a plain number
not sure how to check if a variable is of a number type (int or float)

if we use that approach, the tree would look like:

tree = {
    "type": "operation",
    "op": "+",
    "left": 3,
    "right": {
        "type": "operation",
        "op": "*",
        "left": 5,
        "right": 2
    }
}

operator precendences and parenthesis need to be considered when constructing the tree
"""

"""
EVALUATOR TEST
expression: 0.4 * 5 ^ 2 + 6 / 2 - 5 % 3
should be evaluated as
0.4 * 25 + 6 / 2 - 5 % 3
10 + 6 / 2 - 5 % 3
10 + 3 - 5 % 3
10 + 3 - 2
13 - 2
11
"""

tree = {
    "type": "operation",
    "op": "-",
    "left": {
        "type": "operation",
        "op": "+",
        "left": {
            "type": "operation",
            "op": "*",
            "left": {
                "type": "number",
                "value": 0.4
            },
            "right": {
                "type": "operation",
                "op": "^",
                "left": {
                    "type": "number",
                    "value": 5
                },
                "right": {
                    "type": "number",
                    "value": 2
                }
            }
        },
        "right": {
            "type": "operation",
            "op": "/",
            "left": {
                "type": "number",
                "value": 6
            },
            "right": {
                "type": "number",
                "value": 2
            }
        }
    },
    "right": {
        "type": "operation",
        "op": "%",
        "left": {
            "type": "number",
            "value": 5
        },
        "right": {
            "type": "number",
            "value": 3
        }
    }
}

print("Tree:", display_tree(tree))
print("Result:", evaluate_tree(tree))

#endregion

def evaluate_file(input_path: str) -> list[dict]:
    f = open(input_path, "r")
    expressions = f.readlines()
    f.close()

    for e in expressions:
        tokens = tokenise(e)
        print(*tokens)

while True:
    input_path = input("Input path: ")
    evaluate_file(input_path)