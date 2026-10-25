# Student Study Assistant

## 1. Project Description

The Student Study Assistant is an AI agent powered by a Large Language Model (LLM). It helps students with basic study tasks by interpreting a request, selecting an appropriate tool when needed, executing the tool in Python, and generating a response based on the result.

**Problem addressed:** Students may need quick calculations, help finding the number of days until a deadline, or a way to locate relevant information in saved course notes.

**Intended users:** Students who need help with these study-related tasks.

## 2. Model and Technologies

- **Model:** `Qwen/Qwen2.5-3B-Instruct`
- **Language:** Python
- **Libraries:** PyTorch and Hugging Face Transformers
- **Development environment:** Google Colab with a compatible GPU runtime
- **Inference:** The model is downloaded and loaded in the runtime; the agent does not use Hugging Face hosted inference.

## 3. Available Tools

Each tool's docstring in `tools.py` describes its name, purpose, parameters, and return value.

### `calculator(expression: str)`

- **Purpose:** Evaluates supported arithmetic expressions.
- **Parameter:** `expression` — a string containing an expression, such as `"15 * 16"`.
- **Returns:** The calculated result or an error message.
- **Supported operations:** Addition, subtraction, multiplication, division, floor division, modulo, unary plus/minus, and parentheses.

### `deadline_calculator(date_text: str)`

- **Purpose:** Calculates how many days remain until a date, or how many days have passed if the date is in the past.
- **Parameter:** `date_text` — a date in `YYYY-MM-DD` format.
- **Returns:** The number of days remaining, a message that the deadline is today, or an error message if the date is invalid.
- **Note:** The result uses the current date reported by the Python runtime.

### `search_notes(query: str)`

- **Purpose:** Searches the local `notes.txt` file for lines containing words that overlap with the query.
- **Parameter:** `query` — a topic or phrase to search for.
- **Returns:** Up to five matching lines, a message if there are no matches, or an error message if the notes file cannot be opened.
- **Limitation:** This is a simple word-overlap search, not a semantic search system. Keep `notes.txt` in the same directory as `tools.py` and `agent.py`.

## 4. How the Agent Works

1. The user submits a natural-language request.
2. The LLM receives descriptions of the available tools and chooses a tool with its parameter, or chooses `none` if a tool is not needed.
3. The Python program parses the model's JSON selection and dispatches the selected tool.
4. The tool returns a result or an error message.
5. The LLM generates a final response using the original request and tool result.

The LLM makes the tool-selection decision. The `if` statements in `agent.py` dispatch the tool selected by the model; they do not choose a tool by matching keywords in the user's request.

## 5. PEAS Description

- **Performance measure:** Appropriate tool selection, correct tool results, relevant responses, and graceful handling of invalid requests or tool failures.
- **Environment:** A student interacting with the assistant, the loaded language model, Python runtime, three tools, and the local notes file.
- **Actuators:** Selecting and executing a tool and returning a text response to the user.
- **Sensors:** The user's message, the model's tool-selection output, and the result or error returned by a tool.

## 6. Environment Properties

1. **Partially observable:** The agent sees the current request and tool outputs but does not know the student's full context or intentions beyond the information provided.
2. **Mostly deterministic:** Generation uses `do_sample=False`, and the tools have defined behavior for the same inputs, though the model can still make mistakes and runtime behavior may vary.
3. **Episodic:** Each call processes one request without retaining earlier requests as conversational memory.
4. **Dynamic:** The current date changes over time, and the contents of `notes.txt` can change between requests.
5. **Discrete:** The agent chooses from a finite set of named tools or chooses not to use a tool.
6. **Single-agent:** One LLM-based agent selects actions; the user supplies requests but is not another agent inside the program.
7. **Known:** The available tools and their expected input formats are defined in the code, although the model can still make mistakes when selecting or using them.

## 7. Agent Type

The assistant is primarily a **goal-based agent**. It interprets the user's goal and selects a tool intended to help achieve it. This fits the environment because the available actions are discrete and documented, while the environment is partially observable: the agent must act using the limited information in the current request and the results returned by its tools.

## 8. Setup and Running

The project was developed and tested in Google Colab.

1. Open a Colab notebook and select **Runtime → Change runtime type → T4 GPU** (or another compatible GPU available to you).
2. Install the libraries:

   ```python
   !pip install -U transformers accelerate
   ```

   PyTorch is also required; Colab normally includes it. Install it separately if your environment does not have it.

3. Put `agent.py`, `tools.py`, and `notes.txt` in the same working directory.
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

5. Import the agent and make a request:

   ```python
   from agent import run_agent

   print(run_agent("What is 15 multiplied by 16?", model, tokenizer))
   print(run_agent("How many days until 2030-01-01?", model, tokenizer))
   print(run_agent("Search my notes for asymmetric encryption.", model, tokenizer))
   ```

The first model load downloads model files and may require several gigabytes of storage. Actual hardware and memory requirements depend on the runtime available.

## 9. Error Handling and Known Failure Cases

The agent and tools handle several failure cases:

- **Malformed tool-selection output:** If the model's response cannot be parsed as a JSON object, the agent returns a message asking the user to rephrase the request.
- **Unknown tool selection:** If the model names a tool that is not available, the agent returns a message identifying the unknown tool rather than attempting to execute it.
- **Invalid or missing parameters:** The agent checks that tool parameters have the expected string form and are not empty where required. The tools validate expressions, dates, and search queries and return error messages for invalid input.
- **Tool execution failure:** Exceptions during tool execution are caught and converted into an error result for the final response.
- **No matching notes:** The notes tool returns a message if no lines match the query.
- **Missing notes file:** The notes tool reports that it could not open `notes.txt`.

### Failure cases tested

The following cases were tested through the agent or by testing its tool-dispatch handling:

1. An invalid date (`2026-13-40`) produced an invalid-date error.
2. Searching the sample notes for `quantum computing` returned no matching results.
3. Temporarily removing `notes.txt` caused the tool to report that the file could not be opened; the test restored the file afterward.
4. Simulating a model selection of `unknown_tool` produced an unknown-tool message instead of crashing.

### Known limitations

The model may still select an inappropriate tool, provide an incorrect expression or date, or misunderstand the request. The notes search only matches overlapping words, so it may miss relevant information phrased differently. The final natural-language response is generated by the LLM and may not describe the tool result perfectly, so important answers should be checked. The agent does not retain conversation history and does not automatically retry a failed tool selection.

## 10. Initial Functional Checks

The initial functional checks covered:

- A multiplication request using the calculator.
- A date request using the deadline calculator.
- A request to search the notes for a topic.
- A general study question that did not require a tool.

All four checks worked as expected during development. The failure cases listed in Section 9 were also exercised. A more systematic evaluation with at least ten test cases and at least two improvements based on test results is planned for Stage 3.
