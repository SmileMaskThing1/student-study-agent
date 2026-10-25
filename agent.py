
import json
import torch
from tools import calculator


def generate_response(messages, model, tokenizer, max_new_tokens=150):
    """Generate a response using the loaded language model."""

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
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
    Ask the LLM to select a tool, execute its selection,
    and generate a response for the user.
    """

    routing_messages = [
        {
            "role": "system",
            "content": """
You are the tool-selection component of a student study assistant.

Available tool:
1. calculator: evaluates basic mathematical expressions.

For mathematical calculations, select the calculator and provide
a valid arithmetic expression using numbers and supported operators.
For example, a request for 15 percent of 240 can use 240 * 0.15.

Do not calculate the answer yourself. The calculator will do that.

For requests that do not require a calculation, select none.

Return exactly one JSON object, without Markdown:
{"tool": "calculator", "expression": "15 * 16"}

Or:
{"tool": "none", "expression": null}
"""
        },
        {
            "role": "user",
            "content": user_request
        }
    ]

    # The LLM decides which tool to use.
    selection = generate_response(
        routing_messages, model, tokenizer, max_new_tokens=100
    )

    try:
        start = selection.find("{")
        end = selection.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found.")

        decision = json.loads(selection[start:end + 1])

    except (json.JSONDecodeError, ValueError):
        return (
            "I couldn't determine which tool to use. "
            "Please rephrase your request."
        )

    tool_name = decision.get("tool")

    # Execute the tool selected by the LLM.
    if tool_name == "calculator":
        expression = decision.get("expression")

        if not isinstance(expression, str) or not expression.strip():
            return "The calculator was selected without a valid expression."

        result = calculator(expression)

        tool_result = f"Calculator result: {result}"

    elif tool_name == "none":
        tool_result = "No tool was needed for this request."

    else:
        return f"Unsupported tool selected by the model: {tool_name}"

    # Generate the final answer using the original request and tool result.
    final_messages = [
        {
            "role": "system",
            "content": """
You are a helpful student study assistant.
Answer the user's original request clearly.
When a calculator result is provided, use that result rather
than calculating the answer again.
Be honest if a tool reports an error.
"""
        },
        {
            "role": "user",
            "content": (
                f"Original request: {user_request}\n"
                f"{tool_result}"
            )
        }
    ]

    return generate_response(final_messages, model, tokenizer)
