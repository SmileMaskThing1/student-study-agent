
# Student Study Assistant

## Project Description
A study assistant powered by a Large Language Model (LLM).
It answers student questions and uses a calculator tool
for mathematical calculations.

Planned extensions include calculating deadlines and searching
local course notes.

## Model
- Qwen/Qwen2.5-3B-Instruct
- Python
- PyTorch
- Hugging Face Transformers

## PEAS

- Performance Measure: Correct tool selection, accurate results,
  relevant answers, and appropriate error handling.
- Environment: A user interacting with the study assistant.
- Actuators: Executing available tools and returning responses.
- Sensors: User messages and tool results.

## Environment Properties

1. Partially observable: The agent only receives the information
   provided in the user's request.
2. Deterministic: The current prototype uses deterministic
   generation settings and a deterministic calculator.
3. Episodic: Each request is processed independently without
   retaining conversation history.
4. Static: The environment does not change during an individual
   request.
5. Discrete: Tool selections and actions are discrete choices.
6. Single-agent: One LLM-based agent handles each request.
7. Known: The available tools and their supported operations
   are defined in the program.

## Agent Type

Goal-based agent. The LLM interprets the user's goal and selects
the calculator when a calculation is needed.

## Current Tool

- calculator: Evaluates supported mathematical expressions
  and reports errors when a calculation cannot be completed.

## Current Limitations

The prototype has only one tool. The model may produce an invalid
tool selection or an incorrect expression. Additional tools and
more robust error handling are planned for later stages.
