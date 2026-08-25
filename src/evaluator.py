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

        i += 1

    tokens.append(["END"])

    return tokens

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