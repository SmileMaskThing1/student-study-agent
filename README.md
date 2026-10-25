# Student Study Assistant

## 1. Project Description

The Student Study Assistant is an LLM-powered agent intended to help students with small study-related tasks. It uses a language model to interpret a request, select an available tool when appropriate, execute that tool in Python, and formulate a response using the tool's result.

**Problem addressed:** Students may need quick calculations, help checking the time remaining until a deadline, or a way to find relevant information in their saved course notes.

**Intended users:** Students who want help with these basic study tasks.

## 2. Model and Technologies

- **Model:** `Qwen/Qwen2.5-3B-Instruct`
- **Language:** Python
- **Libraries:** PyTorch, Hugging Face Transformers
- **Environment used during development:** Google Colab with a GPU runtime
- **Inference approach:** The model is downloaded and loaded into the runtime using Transformers; the agent does not depend on Hugging Face hosted inference.

## 3. Available Tools

### `calculator(expression: str)`

- **Purpose:** Evaluates supported arithmetic expressions.
- **Parameter:** `expression` — a string such as `"15 * 16"`.
- **Returns:** The calculated result, or an error message for unsupported expressions or calculation errors.
- **Supported operations:** Addition, subtraction, multiplication, division, floor division, modulo, and unary plus/minus, with parentheses.

### `deadline_calculator(date_text: str)`

- **Purpose:** Calculates how many days remain until a date, or how many days have passed if the date is in the past.
- **Parameter:** `date_text` — a date in `YYYY-MM-DD` format.
- **Returns:** A message with the number of days remaining, a message that the deadline is today, or an error message if the date is invalid.
- **Note:** The calculation uses the current date reported by the Python runtime.

### `search_notes(query: str)`

- **Purpose:** Searches the local `notes.txt` file for lines that share words with a query.
- **Parameter:** `query` — a topic or phrase to search for.
- **Returns:** Up to five matching lines, a message when no matching lines are found, or an error message if the notes file cannot be opened.
- **Search method:** This is a simple word-overlap search, not a semantic search system. Place `notes.txt` in the same directory as `tools.py` and `agent.py`.

Each tool's docstring in `tools.py` documents its name, purpose, parameters, and return value.

## 4. How the Agent Works

1. The user enters a natural-language request.
2. The LLM receives descriptions of the available tools and selects a tool with the appropriate parameter, or selects `none` if no tool is needed.
3. The Python program parses the model's JSON selection and dispatches the selected tool.
4. The selected tool runs and returns a result or an error message.
5. The LLM generates a final response using the original request and tool result.

The model makes the tool-selection decision. The `if` statements in `agent.py` dispatch the selected tool; they do not choose a tool by matching keywords in the user's request.

## 5. PEAS Description

- **Performance measure:** Appropriate tool selection, correct tool results, relevant final answers, and graceful handling of invalid requests or tool failures.
- **Environment:** A student interacting with the assistant, the loaded language model, the Python runtime, the three tools, and the local notes file.
- **Actuators:** Selecting and executing a tool and returning a text response to the user.
- **Sensors:** The user's message, the model's tool-selection output, and the result or error returned by a tool.

## 6. Environment Properties

1. **Partially observable:** The agent sees the current request and tool outputs, but it does not know the student's full context or intentions beyond the information provided.
2. **Deterministic (with limitations):** The model uses deterministic decoding (`do_sample=False`) and the tools have defined behavior for the same inputs, although model output may still be incorrect and runtime behavior can vary.
3. **Episodic:** Each call processes one request without retaining previous requests as conversational memory.
4. **Dynamic:** The current date changes over time, and the contents of `notes.txt` can be changed between requests.
5. **Discrete:** The agent selects from a finite set of named tools or chooses not to use a tool.
6. **Single-agent:** One LLM-based agent selects actions; the user supplies requests but is not another agent inside the program.
7. **Known:** The available tools and their input formats are defined in the code, even though the model can still make selection or argument mistakes.

## 7. Agent Type

The assistant is primarily a **goal-based agent**. It interprets the user's requested goal and selects a tool that can help achieve it. This is appropriate because the available actions are discrete and documented, while the environment is partially observable: the agent must act using the limited information supplied in the current request and the results returned by its tools.

## 8. Setup and Running

The current development workflow uses Google Colab.

1. Open a Colab notebook and select **Runtime → Change runtime type → T4 GPU** (or another available compatible GPU).
2. Install the required packages:

   ```python
   !pip install -U transformers accelerate
   ```

   PyTorch is also required. Colab normally provides it in the runtime; install it separately if using an environment where it is absent.

3. Make sure `agent.py`, `tools.py`, and `notes.txt` are in the same working directory.
4. Load the model and tokenizer:

   ```python
   import torch
   from transformers import AutoTokenizer, AutoModelForCausalLM

   MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

   tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
   model = AutoModelForCausalLM.from_pretrained(
       MODEL_NAME,
       torch_dtype="auto",
       device_map="auto"
   )
   ```

5. Reload the project modules if they were previously imported, then call the agent:

   ```python
   import importlib
   import tools
   import agent

   importlib.reload(tools)
   importlib.reload(agent)

   from agent import run_agent

   print(run_agent("What is 15 multiplied by 16?", model, tokenizer))
   print(run_agent("How many days until 2030-01-01?", model, tokenizer))
   print(run_agent("Search my notes for asymmetric encryption.", model, tokenizer))
   ```

The first model load downloads the model files and may take time and several gigabytes of storage. The precise runtime requirements depend on the available hardware and memory.

## 9. Error Handling and Known Failure Cases

The agent returns a message if it cannot parse a JSON tool selection or if the model selects an unknown tool. It checks that the required tool parameter is a non-empty string where applicable, and tool execution exceptions are converted into an error result. The tools also report invalid expressions, invalid dates, missing notes files, and searches that return no matches.

The agent can still fail if the LLM chooses the wrong tool, returns malformed JSON, supplies an incorrect expression or date, or misunderstands the user's intent. The notes search only matches overlapping words, so it may miss relevant information expressed using different terms. The final response also depends on the model and may inaccurately describe a tool result; users should verify important answers. The current version does not retain conversation history and does not automatically retry failed tool selection.

## 10. Current Testing

Initial functional checks were run for:

- A multiplication request using the calculator.
- A date request using the deadline calculator.
- A topic request using the notes search.
- A general study question that does not require a tool.

These checks confirmed that the agent could complete those example requests. Further systematic tests should cover invalid inputs, missing files, malformed model output, unknown tool names, and cases where the agent selects the wrong tool. The Stage 3 evaluation should record at least ten test cases, including failures, and document at least two resulting improvements.
