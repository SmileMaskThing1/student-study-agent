
import ast
import operator
import re
from datetime import date, datetime
from pathlib import Path


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

    if not isinstance(expression, str) or len(expression) > 200:
        return "Error: Invalid expression."

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

        if sum(1 for _ in ast.walk(tree)) > 50:
            return "Error: Expression is too complex."

        return evaluate(tree)

    except (
        ValueError, SyntaxError, ZeroDivisionError,
        OverflowError, TypeError, RecursionError
    ) as error:
        return f"Error: {error}"


def deadline_calculator(date_text: str):
    """
    Name: deadline_calculator
    Description: Calculates days until a specified date.
    Parameters: date_text (str), a date in YYYY-MM-DD format.
    Returns: Days remaining or an error message.
    """
    if not isinstance(date_text, str):
        return "Error: Enter a date in YYYY-MM-DD format."

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text):
        return "Error: Enter a date in YYYY-MM-DD format."

    try:
        target_date = datetime.strptime(
            date_text, "%Y-%m-%d"
        ).date()
    except ValueError:
        return "Error: That is not a valid date."

    days_remaining = (target_date - date.today()).days

    if days_remaining > 0:
        return f"{days_remaining} days remaining."
    elif days_remaining == 0:
        return "The deadline is today."
    else:
        return f"The deadline was {-days_remaining} days ago."


def search_notes(query: str):
    """
    Name: search_notes
    Description: Searches local study notes for matching lines.
    Parameters: query (str), the topic or terms to search for.
    Returns: The most relevant note lines or a helpful message.
    """
    if not isinstance(query, str) or not query.strip():
        return "Error: Enter a topic to search for."

    notes_path = Path(__file__).with_name("notes.txt")

    try:
        contents = notes_path.read_text(encoding="utf-8")
    except OSError:
        return "Error: Could not open notes.txt."

    query_words = set(re.findall(r"\w+", query.lower()))

    if not query_words:
        return "Error: Enter a valid search term."

    exact_matches = []
    partial_matches = []

    for line_number, line in enumerate(contents.splitlines(), start=1):
        note_words = set(re.findall(r"\w+", line.lower()))
        score = len(query_words & note_words)

        if score == len(query_words):
            exact_matches.append((score, line_number, line.strip()))
        elif score > 0:
            partial_matches.append((score, line_number, line.strip()))

    # Prefer lines containing every query term.
    # Fall back to partial matches if no exact matches exist.
    matches = exact_matches if exact_matches else partial_matches
    matches.sort(key=lambda item: (-item[0], item[1]))

    if not matches:
        return "No matching notes found."

    return "\n".join(
        f"Line {line_number}: {line}"
        for score, line_number, line in matches[:5]
    )
