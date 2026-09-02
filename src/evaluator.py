"""
HIT137 Assignment 2 - Question 2

operators: + - * / % ^
parenthesis
unary negation -x, --x, -(x + y), x * -y etc
no unary +
implicit multiplication

precedence (lowest to highest binding):
+ -
* / % and implicit multiplication
unary -
^

useful links
https://en.wikipedia.org/wiki/Binary_expression_tree
"""

import os
import sys

operators = "+-*/%^"

# ---------------------------------------------------------------------------
# Tokeniser (Erik's version, with two bug fixes - see comments)
# ---------------------------------------------------------------------------

def tokenise(e: str) -> list[tuple]:
    tokens = []

    # split into tokens (TYPE, VALUE) end with (END, None)

    i = 0

    while i < len(e):
        char = e[i]

        if char.isdigit():
            # read until a non-digit character, then check for a decimal place
            # if there is a decimal place, read all digits after the decimal place

            start = i

            # FIX: was "i + 1 < len(e)" missing on the lookahead below, which let
            # e[i + 1] run past the end of the string for a number at the
            # very end of the line (e.g. "3+5" with no trailing character).
            while i + 1 < len(e) and e[i + 1].isdigit():
                i += 1

            # FIX: must check i + 1 < len(e) before reading e[i + 1], not i < len(e).
            if i + 1 < len(e) and e[i + 1] == '.':
                i += 1  # consume the '.'

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

Each parse_* function takes (tokens, pos) and returns (node, new_pos).
Every level calls the *next tighter* level to get its operands, and
parentheses recurse all the way back to the loosest level (parse_add_sub).

Node shapes (matching Erik's evaluate_tree / display_tree):
  {"type": "number", "value": <float>}
  {"type": "unary", "operand": <node>}
  {"type": "operation", "op": <str>, "left": <node>, "right": <node>}
"""

def parse_add_sub(tokens, pos):
    # Level 1 (loosest): + -

    left, pos = parse_mul_div(tokens, pos)

    while tokens[pos][0] == "OP" and tokens[pos][1] in ("+", "-"):
        op = tokens[pos][1]
        pos += 1
        right, pos = parse_mul_div(tokens, pos)
        left = {"type": "operation", "op": op, "left": left, "right": right}

    return left, pos


def parse_mul_div(tokens, pos):
    # Level 2: * / % and implicit multiplication

    left, pos = parse_unary(tokens, pos)

    while True:
        t_type, t_val = tokens[pos]
    
        if t_type == "OP" and t_val in ("*", "/", "%"):
            pos += 1
            right, pos = parse_unary(tokens, pos)
            left = {"type": "operation", "op": t_val, "left": left, "right": right}

        elif t_type == "LPAREN":
            # implicit multiplication, e.g. 2(3+4) or (2)(3)
            right, pos = parse_unary(tokens, pos)
            left = {"type": "operation", "op": "*", "left": left, "right": right}

        else:
            break

    return left, pos


def parse_unary(tokens, pos):
    # Level 3: prefix unary minus (unary + is an error)

    t_type, t_val = tokens[pos]

    if t_type == "OP" and t_val == "-":
        pos += 1
        operand, pos = parse_unary(tokens, pos)  # allows --5
        return {"type": "unary", "operand": operand}, pos

    if t_type == "OP" and t_val == "+":
        raise RuntimeError("Unary + is not supported")

    return parse_power(tokens, pos)


def parse_power(tokens, pos):
    # Level 4 (tightest): ^, right associative

    base, pos = parse_primary(tokens, pos)

    if tokens[pos][0] == "OP" and tokens[pos][1] == "^":
        pos += 1
        # exponent parsed via parse_unary so "2^-3" and right-associativity
        # ("2^3^2" == "2^(3^2)") both work
        exponent, pos = parse_unary(tokens, pos)
        return {"type": "operation", "op": "^", "left": base, "right": exponent}, pos

    return base, pos


def parse_primary(tokens, pos):
    # A number literal, or a parenthesised sub-expression.

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


def build_tree(tokens):
    # Parse the full token list into one tree, or raise a RuntimeError.

    node, pos = parse_add_sub(tokens, 0)

    if tokens[pos][0] != "END":
        raise RuntimeError(f"unexpected trailing token {tokens[pos]}")

    return node


# ---------------------------------------------------------------------------
# Evaluator (Erik's version - unary fixed to recurse into "operand")
# ---------------------------------------------------------------------------

def evaluate_tree(node: dict):
    if node["type"] == "number": 
        return node["value"]

    # FIX: unary negation must negate a sub-tree ("operand"), not a bare
    # "value" - otherwise -(3 + 4) and --5 can't be represented/evaluated.
    if node["type"] == "unary":
        return -evaluate_tree(node["operand"])

    if node["type"] == "operation":
        # recursively evaluate the tree, from the first operation to the last
        left, right = evaluate_tree(node["left"]), evaluate_tree(node["right"])

        # perform the operation on the left and right values
        if node["op"] == "+": return left + right
        if node["op"] == "-": return left - right
        if node["op"] == "*": return left * right
        if node["op"] == "/": return left / right   # raises ZeroDivisionError on /0
        if node["op"] == "%": return left % right    # raises ZeroDivisionError on %0
        if node["op"] == "^": return left ** right


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def format_number(value) -> str:
    """
    Round to 4 decimal places, trimming trailing zeros
    (2.66666... -> "2.6667", 2.5 -> "2.5").
    """
    return f"{value:.4f}".rstrip("0").rstrip(".")


def display_tokens(tokens: list) -> str:
    # tokenise() returns this single sentinel on a tokenising failure
    if tokens == [("ERROR", None)]:
        return "ERROR"

    parts = []

    for t_type, value in tokens:
        if value is None:
            parts.append(f"[{t_type}]")

        else:
            parts.append(f"[{t_type}:{value}]")   # FIX: no spaces around ':'

    return " ".join(parts)


def display_tree(node: dict) -> str:
    if node["type"] == "number":
        return format_number(node["value"])  # FIX: was raw str(value) e.g. "3.0"

    if node["type"] == "unary":
        return f"(neg {display_tree(node['operand'])})"  # FIX: recurse, don't print a bare value

    if node["type"] == "operation": # use the same recursion technique as evaluate_tree for displaying the tree
        return f"({node['op']} {display_tree(node['left'])} {display_tree(node['right'])})"


# ---------------------------------------------------------------------------
# Per-expression pipeline: tokenise -> build_tree -> evaluate_tree
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# File-level interface
# ---------------------------------------------------------------------------

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