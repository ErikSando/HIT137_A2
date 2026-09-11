"""
HIT137 Assignment 2 - Question 2
"""

import os
import sys

operators = "+-*/%^"

def tokenise(e: str) -> list[tuple]: # split into tokens (TYPE, VALUE) end with (END, None)
    tokens = []
    i = 0

    while i < len(e):
        char = e[i]

        if char.isdigit():
            # read until a non-digit character, then check for a decimal place
            # if there is a decimal place, read all digits after the decimal place

            start = i

            while i + 1 < len(e) and e[i + 1].isdigit():
                i += 1

            if i + 1 < len(e) and e[i + 1] == '.':
                i += 1

                # a '.' with no digit after it (e.g. "3.") is not a valid number literal -> treat the whole line as a tokenising error
                if i + 1 >= len(e) or not e[i + 1].isdigit():
                    print(f"Error in tokenise: Invalid number literal '{e[start:i + 1]}'")
                    return [("ERROR", None)]

                while i + 1 < len(e) and e[i + 1].isdigit():
                    i += 1

            tokens.append(("NUM", e[start: i + 1]))

        elif char in operators:
            tokens.append(("OP", char))

        elif char == '(':
            tokens.append(("LPAREN", char))

        elif char == ')':
            tokens.append(("RPAREN", char))

        else:
            if not char.isspace(): # other characters are not supported
                print(f"Error in tokenise: Invalid character '{char}'")
                return [("ERROR", None)]

        i += 1

    tokens.append(("END", None))

    return tokens

"""
Parser - builds the tree from the tokens (recursive descent)
"""

def parse_add_sub(tokens, pos): # Level 1: + -
    left, pos = parse_mul_div(tokens, pos)

    while tokens[pos][0] == "OP" and tokens[pos][1] in ("+", "-"):
        op = tokens[pos][1]
        pos += 1
        right, pos = parse_mul_div(tokens, pos)
        left = {"type": "operation", "op": op, "left": left, "right": right}

    return left, pos

def parse_mul_div(tokens, pos): # Level 2: * / % and implicit multiplication
    left, pos = parse_unary(tokens, pos)

    while True:
        t_type, t_val = tokens[pos]
    
        if t_type == "OP" and t_val in ("*", "/", "%"):
            pos += 1
            right, pos = parse_unary(tokens, pos)
            left = {"type": "operation", "op": t_val, "left": left, "right": right}

        elif t_type == "LPAREN": # implicit multiplication
            right, pos = parse_unary(tokens, pos)
            left = {"type": "operation", "op": "*", "left": left, "right": right}

        else:
            break

    return left, pos

def parse_unary(tokens, pos): # Level 3: unary minus (unary + is an error)
    t_type, t_val = tokens[pos]

    if t_type == "OP" and t_val == "-":
        pos += 1
        operand, pos = parse_unary(tokens, pos)  # allows --5
        return {"type": "unary", "operand": operand}, pos

    if t_type == "OP" and t_val == "+":
        raise RuntimeError("Unary + is not supported")

    return parse_power(tokens, pos)

def parse_power(tokens, pos): # Level 4: exponentiation ^, right associative
    base, pos = parse_primary(tokens, pos)

    if tokens[pos][0] == "OP" and tokens[pos][1] == "^":
        pos += 1
        exponent, pos = parse_unary(tokens, pos)
        return {"type": "operation", "op": "^", "left": base, "right": exponent}, pos

    return base, pos

def parse_primary(tokens, pos): # A number literal, or a parenthesised sub-expression.
    t_type, t_val = tokens[pos]

    if t_type == "NUM":
        return {"type": "number", "value": float(t_val)}, pos + 1

    if t_type == "LPAREN":
        pos += 1
        node, pos = parse_add_sub(tokens, pos)  # recurse back to the top

        if tokens[pos][0] != "RPAREN":
            raise RuntimeError("expected closing parenthesis")

        pos += 1

        return node, pos

    raise RuntimeError(f"unexpected token {tokens[pos]}")

# Parse the full token list into one tree, or raise a RuntimeError.
def build_tree(tokens):
    node, pos = parse_add_sub(tokens, 0)

    if tokens[pos][0] != "END":
        raise RuntimeError(f"unexpected trailing token {tokens[pos]}")

    return node

def evaluate_tree(node: dict):
    if node["type"] == "number": 
        return node["value"]

    if node["type"] == "unary":
        return -evaluate_tree(node["operand"])

    if node["type"] == "operation":
        # recursively evaluate the tree, from the first operation to the last
        left, right = evaluate_tree(node["left"]), evaluate_tree(node["right"])

        # perform the operation on the left and right values
        if node["op"] == "+": return left + right
        if node["op"] == "-": return left - right
        if node["op"] == "*": return left * right
        if node["op"] == "/": return left / right   # raises ZeroDivisionError on / 0
        if node["op"] == "%": return left % right    # raises ZeroDivisionError on % 0
        if node["op"] == "^": return left ** right

def format_number(value) -> str: # return a string of the number with 4 decimal places and removed trailing zeros
    return f"{value:.4f}".rstrip("0").rstrip(".")

def display_tokens(tokens: list) -> str:
    if tokens == [("ERROR", None)]: # check for a tokenising error
        return "ERROR"

    parts = []

    for t_type, value in tokens:
        if value is None:
            parts.append(f"[{t_type}]")

        else:
            parts.append(f"[{t_type}:{value}]")

    return " ".join(parts)

def display_tree(node: dict) -> str:
    if node["type"] == "number":
        return format_number(node["value"])

    if node["type"] == "unary":
        return f"(neg {display_tree(node['operand'])})"

    if node["type"] == "operation": # use the same recursion technique as evaluate_tree for displaying the tree
        return f"({node['op']} {display_tree(node['left'])} {display_tree(node['right'])})"

# For each expression: tokenise, build a tree dict and string, and evaluate the expression
def process_expression(expr_text: str) -> dict:
    tokens = tokenise(expr_text)

    if tokens == [("ERROR", None)]:
        return {"input": expr_text, "tree": "ERROR", "tokens": "ERROR", "result": "ERROR"}

    tokens_str = display_tokens(tokens)

    try:
        tree = build_tree(tokens)

    except RuntimeError as e:
        print("Error in build_tree:", e) # print the error
        return {"input": expr_text, "tree": "ERROR", "tokens": tokens_str, "result": "ERROR"}

    tree_str = display_tree(tree)

    try:
        value = evaluate_tree(tree)
    except ZeroDivisionError:
        return {"input": expr_text, "tree": tree_str, "tokens": tokens_str, "result": "ERROR"}

    return {"input": expr_text, "tree": tree_str, "tokens": tokens_str, "result": float(value)}

def evaluate_file(input_path: str) -> list[dict]:
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        lines = f.read().splitlines()

    results = [process_expression(line.strip("\r\n")) for line in lines]

    output_dir = os.path.dirname(os.path.abspath(input_path))
    output_path = os.path.join(output_dir, "output.txt")

    blocks = []
    for r in results:
        result_display = r["result"] if r["result"] == "ERROR" else format_number(r["result"])
        blocks.append(
            f"Input: {r['input']}\n"
            f"Tree: {r['tree']}\n"
            f"Tokens: {r['tokens']}\n"
            f"Result: {result_display}"
        )

    with open(output_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n\n".join(blocks) + "\n")

    return results

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else input("Input path: ")
    evaluate_file(path)
    print(f"Done. Results written to output.txt (based on {path}).")
