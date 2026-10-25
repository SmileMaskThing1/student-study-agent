
import json
import torch
from datetime import date

from tools import calculator, deadline_calculator, search_notes


def generate_response(messages, model, tokenizer, max_new_tokens=180):
    """Generate a response using the loaded language model."""

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False
        )

    new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

    return tokenizer.decode(
        new_tokens,
        skip_special_tokens=True
    ).strip()


def run_agent(user_request, model, tokenizer):
    """
    Ask the LLM to select a tool, execute the selection,
    and generate a response using the tool result.
    """

    today = date.today().isoformat()

    routing_messages = [
        {
            "role": "system",
            "content": f"""
You are the tool-selection component of a student study assistant.

Today's date is {today}.

Choose the most appropriate action for the user's request.

Available tools:

1. calculator
   Parameter: expression
   Evaluates basic arithmetic expressions.
   Supported operators: +, -, *, /, //, %, parentheses.
   Example: {{"tool": "calculator", "expression": "15 * 16"}}

2. deadline_calculator
   Parameter: date_text
   Calculates days until a date.
   The date must use YYYY-MM-DD format.
   Convert the user's requested date to this format.
   Example: {{"tool": "deadline_calculator", "date_text": "2030-01-01"}}

3. search_notes
   Parameter: query
   Searches the local study notes file for relevant lines.
   Example: {{"tool": "search_notes", "query": "asymmetric encryption"}}

If none of these tools is appropriate, choose none.
Example: {{"tool": "none"}}

Return exactly one JSON object with a tool name and its required
parameter, or the tool name none. Do not use Markdown.
Do not calculate answers yourself when a tool is appropriate.
"""
        },
        {
            "role": "user",
            "content": user_request
        }
    ]

    # The LLM decides which tool to use.
    selection = generate_response(
        routing_messages, model, tokenizer, max_new_tokens=120
    )

    # Parse the JSON returned by the LLM.
    try:
        start = selection.find("{")
        end = selection.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found.")

        decision = json.loads(selection[start:end + 1])

        if not isinstance(decision, dict):
            raise ValueError("The response is not a JSON object.")

    except (json.JSONDecodeError, ValueError):
        return (
            "I couldn't determine a valid action from the model's response. "
            "Please rephrase your request."
        )

    tool_name = decision.get("tool")

    # Execute the tool chosen by the LLM.
    try:
        if tool_name == "calculator":
            expression = decision.get("expression")

            if not isinstance(expression, str) or not expression.strip():
                return "The calculator was selected without a valid expression."

            tool_result = calculator(expression)

        elif tool_name == "deadline_calculator":
            date_text = decision.get("date_text")

            if not isinstance(date_text, str):
                return "The deadline calculator was selected without a valid date."

            tool_result = deadline_calculator(date_text)

        elif tool_name == "search_notes":
            query = decision.get("query")

            if not isinstance(query, str) or not query.strip():
                return "The notes search was selected without a valid query."

            tool_result = search_notes(query)

        elif tool_name == "none":
            tool_result = (
                "No tool was selected. Answer the user's request directly "
                "without claiming that a tool was used."
            )

        else:
            return (
                f"The model selected an unknown tool: {tool_name!r}. "
                "Please try rephrasing your request."
            )

    except Exception as error:
        tool_result = (
            f"Tool execution failed ({type(error).__name__}). "
            "Explain that the operation could not be completed."
        )

    # Ask the LLM to answer using the original request and tool result.
    final_messages = [
        {
            "role": "system",
            "content": """
You are a helpful student study assistant.

Answer the user's original request clearly.
When a tool result is provided, use that result rather than
calculating or inventing a different result.
If the tool reports an error or no matching notes, explain that honestly.
Do not claim that a tool was used if no tool was selected.
"""
        },
        {
            "role": "user",
            "content": (
                f"Original request: {user_request}\n\n"
                f"Tool result: {tool_result}"
            )
        }
    ]

    return generate_response(final_messages, model, tokenizer)
