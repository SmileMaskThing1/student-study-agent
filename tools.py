
import ast
import operator

def calculator(expression: str):
    """
    Name: calculator
    Description: Evaluates basic mathematical expressions.
    Parameters: expression (str), a mathematical expression.
    Returns: The calculated result or an error message.
    """

    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
    }

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in operations:
            left = evaluate(node.left)
            right = evaluate(node.right)
            return operations[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.USub, ast.UAdd)
        ):
            value = evaluate(node.operand)
            return -value if isinstance(node.op, ast.USub) else value

        raise ValueError("Unsupported mathematical expression.")

    try:
        tree = ast.parse(expression, mode="eval")
        return evaluate(tree)
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as error:
        return f"Error: {error}"
