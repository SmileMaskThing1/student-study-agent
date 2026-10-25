# Student Study Assistant

## 1. Project overview

The Student Study Assistant is an LLM-based agent that helps students with small study-related tasks. A user submits a natural-language request, the language model selects an appropriate tool when needed, Python executes that tool, and the agent returns a response.

**Problem addressed:** Students may need to perform simple calculations, find out how many days remain until a deadline, or locate information in saved course notes.

**Intended users:** Students who want help with these study tasks.

## 2. Model and technologies

- **Model:** `Qwen/Qwen2.5-3B-Instruct`
- **Language:** Python
- **Libraries:** PyTorch, Hugging Face Transformers, and Accelerate
- **Development environment:** Google Colab with a compatible GPU runtime (a T4 GPU was used during development)
- **Inference:** The model is downloaded and run in the notebook runtime rather than called through Hugging Face hosted inference.

## 3. Tools

The project has three tools. Each tool's docstring in `tools.py` describes its name, purpose, parameters, and return value.

### `calculator(expression: str)`

Evaluates a supported mathematical expression.

- **Parameter:** `expression`, such as `"15 * 16"`.
- **Returns:** The calculated result or an error message.
- **Supported operations:** Addition, subtraction, multiplication, division, floor division, modulo, unary plus/minus, and parentheses.
- **Validation:** Rejects unsupported syntax and expressions that exceed the implementation's size/complexity limits.

### `deadline_calculator(date_text: str)`

Calculates how many days remain until a specified date, or how many days have passed if the date is in the past.

- **Parameter:** `date_text` in `YYYY-MM-DD` format.
- **Returns:** A day count, a message that the deadline is today, or an error message for an invalid date.
- **Note:** The calculation uses the date reported by the Python runtime, so the result changes as time passes.

### `search_notes(query: str)`

Searches the local `notes.txt` file for relevant lines.

- **Parameter:** `query`, a topic or phrase.
- **Returns:** Matching note lines, a no-results message, or an error message if the file cannot be opened.
- **Matching approach:** The tool first prioritizes lines that contain all query terms. If there are no such lines, it falls back to partial word matches. It is a simple word-based search, not semantic search.
- **File requirement:** Keep `notes.txt` in the same directory as `tools.py`.

## 4. How the agent works

1. The user submits a natural-language request.
2. The LLM receives descriptions of the available tools and chooses a tool and its parameter, or chooses `none` when no tool is appropriate.
3. The Python program parses the model's JSON selection and dispatches the selected tool.
4. The selected tool returns a result or an error message.
5. For calculator and deadline requests, the LLM formats the tool result into a response. For notes search, the agent returns the actual search results directly so that the LLM cannot misrepresent them.

The LLM makes the tool-selection decision. The `if` statements in `agent.py` dispatch the tool selected by the model; they do not select tools by matching keywords in the user's original request.

## 5. PEAS

- **Performance measure:** Appropriate tool selection, correct tool results, relevant responses, and graceful handling of invalid requests or tool failures.
- **Environment:** A student interacting with the assistant, the loaded language model, Python runtime, available tools, and local notes file.
- **Actuators:** Selecting and executing a tool and returning a text response.
- **Sensors:** The user's message, the model's tool-selection output, and results or errors returned by tools.

## 6. Environment properties

1. **Partially observable:** The agent only sees the current request and tool outputs, not the student's full context or intentions.
2. **Deterministic (for a fixed runtime configuration):** Generation uses `do_sample=False`, and the tools have defined behavior for the same inputs, although the model can still make incorrect decisions or interpretations.
3. **Episodic:** Each call processes one request without retaining earlier requests as conversational memory.
4. **Dynamic:** The current date changes over time and the contents of `notes.txt` can change between requests.
5. **Discrete:** The agent chooses from a finite set of named tools or chooses not to use a tool.
6. **Single-agent:** One LLM-based agent selects actions; the user supplies requests but is not another agent inside the program.
7. **Known:** The available tools and their expected input formats are defined in the code, although the model can still make mistakes.

## 7. Agent type

The assistant is primarily a **goal-based agent**. It interprets the user's goal and selects a tool intended to achieve it. This fits the environment because the actions are discrete and documented, while the environment is partially observable: the agent must act using the limited information in the current request and tool results.

## 8. Setup and running

The project was developed and tested in Google Colab.

1. Create/open a Colab notebook and select **Runtime → Change runtime type → T4 GPU** (or another compatible GPU available to the runtime).
2. Install the required libraries:

   ```python
   !pip install -U transformers accelerate
   ```

   PyTorch is also required; Colab normally includes it. Install it separately if it is missing from your environment.

3. Place `agent.py`, `tools.py`, and `notes.txt` in the same working directory.
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

5. Import the agent and try requests:

   ```python
   from agent import run_agent

   print(run_agent("What is 15 multiplied by 16?", model, tokenizer))
   print(run_agent("How many days until 2030-01-01?", model, tokenizer))
   print(run_agent("Search my notes for asymmetric encryption.", model, tokenizer))
   ```

The first model load downloads several gigabytes of model files and may take time. Available GPU memory and setup requirements depend on the runtime. `notes.txt` must be present for the notes-search tool to return course content.

## 9. Error handling

The agent and tools handle several failure cases:

- **Malformed tool-selection output:** If the model's response cannot be parsed as a JSON object, the agent returns a message asking the user to rephrase the request.
- **Unknown tool selection:** If the model names an unavailable tool, the agent returns an unknown-tool message rather than attempting to execute it.
- **Invalid or missing parameters:** The agent checks tool parameters, while the tools validate expressions, dates, and search queries.
- **Tool execution failure:** Exceptions during tool execution are caught and converted into an error message.
- **No matching notes:** The notes tool reports that no matching notes were found.
- **Missing notes file:** The notes tool reports that it could not open `notes.txt`.
- **Potentially misleading generated summaries:** Notes-search results are returned directly instead of being passed through the LLM for summarization. This avoids the model contradicting the actual search results.

See [`tests.md`](tests.md) for the test cases and recorded results.

## 10. Stage 3 improvements

Two improvements were made after testing:

1. **Prevent notes-result misrepresentation.** Initially, the LLM sometimes claimed there were no specific symmetric-encryption notes even though the notes tool had returned the matching line. The agent was changed to return the notes-search results directly. The retest returned the matching line accurately.
2. **Improve notes-search relevance.** The search tool was changed to prioritize lines containing all query terms before considering partial matches. A search for `symmetric encryption` then returned the specific line: `Symmetric encryption uses the same key for encryption and decryption.`

A calculator regression check after these changes still returned `240` for `15 * 16`.

## 11. Known limitations

- The LLM can still choose an inappropriate tool or generate an incorrect parameter.
- Tool selection relies on the model returning valid JSON in the requested format; malformed output is reported rather than automatically retried.
- Notes search is based on word overlap and cannot reliably understand synonyms, context, or paraphrases.
- The agent does not retain conversational history between calls.
- The generated wording for calculator and deadline results can still be imperfect, although the underlying tool result is used.
- The example `notes.txt` contains only a small set of sample notes; users should replace or extend it with their own material.

## 12. Evaluation

The initial functional checks covered the calculator, deadline calculator, notes search, and a general question. Additional cases exercised invalid dates, empty search results, a missing notes file, and an unknown tool selection. Stage 3 evaluation and the two resulting improvements are documented in [`tests.md`](tests.md).
