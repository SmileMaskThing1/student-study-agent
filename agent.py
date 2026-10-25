
import json
import torch
from datetime import date

from tools import calculator, deadline_calculator, search_notes


def generate_response(messages, model, tokenizer, max_new_tokens=180):
    """
    Name: generate_response
    Description: Generates a response using the local language model.
    Parameters: messages, model, tokenizer, max_new_tokens.
    Returns: The generated text response.
    """

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
    Name: run_agent
    Description: Selects and executes an appropriate tool using the LLM.
    Parameters: user_request, model, tokenizer.
    Returns: The tool result or a generated response.
    """

    today = date.today().isoformat()

    routing_messages = [
        {
            "role": "system",
            "content": f"""
You are the decision-making component of a student study assistant.

Today's date is {today}.

Choose the appropriate tool for the user's request.

AVAILABLE TOOLS:

1. calculator
   Parameter: expression
   Evaluates basic arithmetic expressions.
   Supported operators: +, -, *, /, //, %, parentheses.
   Example:
   {{"tool": "calculator", "expression": "15 * 16"}}

2. deadline_calculator
   Parameter: date_text
   Calculates the days until a specified date.
   Date format: YYYY-MM-DD.
   Convert the requested date to this format.
   Example:
   {{"tool": "deadline_calculator", "date_text": "2030-01-01"}}

3. search_notes
   Parameter: query
   Searches the local notes file for relevant lines.
   Example:
   {{"tool": "search_notes", "query": "symmetric encryption"}}

If no tool is appropriate, select none:
{{"tool": "none"}}

Return exactly one valid JSON object.
Do not include Markdown or additional explanations.
Do not perform calculations yourself when the calculator is appropriate.
"""
        },
        {
            "role": "user",
            "content": user_request
        }
    ]

    # Ask the LLM to choose a tool.
    try:
        selection = generate_response(
            routing_messages,
            model,
            tokenizer,
            max_new_tokens=120
        )

        start = selection.find("{")
        end = selection.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object was found.")

        decision = json.loads(selection[start:end + 1])

        if not isinstance(decision, dict):
            raise ValueError("The response was not a JSON object.")

    except (json.JSONDecodeError, ValueError):
        return (
            "I couldn't determine a valid action from the model's response. "
            "Please rephrase your request."
        )
    except Exception as error:
        return (
            f"The model response could not be processed "
            f"({type(error).__name__}). Please try again."
        )

    tool_name = decision.get("tool")

    # Execute the selected tool.
    try:
        if tool_name == "calculator":

            expression = decision.get("expression")

            if not isinstance(expression, str) or not expression.strip():
                return "Error: The calculator requires a valid expression."

            tool_result = calculator(expression)

            # Preserve calculator errors instead of letting the LLM
            # reinterpret them as successful calculations.
            if isinstance(tool_result, str) and tool_result.startswith("Error:"):
                return tool_result

        elif tool_name == "deadline_calculator":

            date_text = decision.get("date_text")

            if not isinstance(date_text, str) or not date_text.strip():
                return "Error: A valid date is required."

            tool_result = deadline_calculator(date_text)

            if isinstance(tool_result, str) and tool_result.startswith("Error:"):
                return tool_result

        elif tool_name == "search_notes":

            query = decision.get("query")

            if not isinstance(query, str) or not query.strip():
                return "Error: The notes search requires a search query."

            # Return the actual results directly. This prevents the LLM
            # from contradicting or misrepresenting the contents of notes.
            return search_notes(query)

        elif tool_name == "none":

            # No tool is necessary; let the LLM answer normally.
            tool_result = None

        else:
            return (
                f"The model selected an unknown tool: {tool_name!r}. "
                "Please try rephrasing your request."
            )

    except Exception as error:
        return (
            f"Tool execution failed ({type(error).__name__}). "
            "Please check the input and try again."
        )

    # Generate the final answer for non-notes tools.
    if tool_result is None:
        final_content = user_request
    else:
        final_content = (
            f"Original request: {user_request}\n\n"
            f"Actual tool result: {tool_result}"
        )

    final_messages = [
        {
            "role": "system",
            "content": """
You are a helpful student study assistant.

Answer the user's request clearly and accurately.
For calculations and deadlines, use the provided tool result exactly.
Do not invent a different result.
If no tool was necessary, answer the original request normally.
"""
        },
        {
            "role": "user",
            "content": final_content
        }
    ]

    try:
        return generate_response(
            final_messages,
            model,
            tokenizer
        )
    except Exception as error:
        return (
            f"Could not generate the final response "
            f"({type(error).__name__}). Please try again."
        )
