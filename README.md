# Student Study Assistant

## 1. Project Description

The Student Study Assistant is a prototype AI agent powered by a Large Language Model (LLM). It helps students with simple study-related requests and can use a calculator tool to evaluate supported mathematical expressions.

**Problem addressed:** Students sometimes need quick answers to basic calculations while studying.

**Intended users:** Students who want help with simple calculations and study questions.

**Current scope:** The agent currently has one tool, `calculator`. Searching course notes and calculating deadlines are possible future extensions; they are not implemented yet.

## 2. Model and Technologies

- **Model:** `Qwen/Qwen2.5-3B-Instruct`
- **Language:** Python
- **Libraries:** PyTorch, Hugging Face Transformers
- **Execution environment:** Google Colab (the model is loaded in the notebook)

## 3. PEAS Description

- **Performance measure:** Whether the agent selects the calculator when needed, returns correct calculation results, provides relevant responses, and handles invalid requests or tool errors without crashing.
- **Environment:** A student sends a request to the Python-based assistant; the agent has access to its LLM and the calculator tool.
- **Actuators:** Selecting a tool, calling the calculator, and returning a text response to the user.
- **Sensors:** The user's request, the model's tool-selection output, and the calculator's result or error message.

## 4. Environment Properties

1. **Partially observable:** The agent only receives the current request and tool output; it does not know the student's full context or everything the student may need.
2. **Deterministic:** For a fixed model, prompt, and runtime configuration, generation uses deterministic decoding (`do_sample=False`), and the calculator returns a predictable result for a supported expression.
3. **Episodic:** Each request is processed independently, and previous requests are not retained as conversation history.
4. **Static:** The prototype does not interact with a live, changing external environment while processing a request.
5. **Discrete:** The agent chooses between a small set of actions, currently using the calculator or selecting no tool.
6. **Single-agent:** One LLM-based agent interprets the request and chooses an action; the user provides requests but is not another agent in the program.
7. **Known:** The available tool and its supported operations are defined in the code, although the LLM can still make mistakes when selecting or using the tool.

## 5. Agent Type

The prototype is primarily a **goal-based agent**. It interprets the user's requested goal and chooses whether to call the calculator to help accomplish it. This fits the current environment because each request is processed independently, the available actions are discrete, and the tool's behavior is defined. The environment is only partially observable because the agent has access only to the information supplied in the current request and returned by its tool.

## 6. Current Tool

### `calculator(expression: str)`

- **Purpose:** Evaluates a supported arithmetic expression.
- **Parameter:** `expression` — a string containing a mathematical expression.
- **Returns:** The calculated result, or an error message when the expression is unsupported or the calculation fails.

The LLM chooses whether to use the calculator and provides the expression. Python executes the selected tool; the program does not select the tool by searching the user's request for keywords.

## 7. Current Limitations

- The agent has only one tool.
- The LLM may produce invalid tool-selection output or an incorrect expression.
- The calculator supports only a limited set of arithmetic operations.
- The prototype does not retain conversation history.
- The model is loaded and run through a Colab notebook; the project is not yet packaged as a standalone application.

## 8. Planned Extensions

Possible future tools include a deadline calculator and a search tool for local course notes. These features will be added and documented only after they are implemented and tested.
