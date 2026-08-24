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
"""

digits = "0123456789"

def evaluate_file(input_path: str) -> list[dict]:
    f = open(input_path, "r")
    expressions = f.readlines()
    f.close()

    tokens = []

    for e in expressions:
        # split into tokens [TYPE : VALUE] end with [END]

        value = 0
        is_number = False
        in_decimals = False
        dp = 1

        t_type = "NUM"

        for char in e:
            if char in digits:
                if in_decimals:
                    is_number = True
                    value += int(char) / (10 ** dp)
                    dp += 1

                else:
                    is_number = True
                    value *= 10
                    value += int(char)

            elif char == ".":
                is_number = True
                in_decimals = True

            else:
                if is_number:
                    tokens.append(["NUM", value])
                    is_number = False
                    in_decimals = False
                    value = 0
                    dp = 1

        if is_number:
            tokens.append(["NUM", value])
            is_number = False
            in_decimals = False
            value = 0
            dp = 1

    tokens.append(["END"])

    print(tokens)

while True:
    input_path = input("Input path: ")
    evaluate_file(input_path)