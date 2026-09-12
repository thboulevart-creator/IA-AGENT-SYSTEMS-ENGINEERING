# Q-LLM-01 execution boundary

This directory is reserved for the real-LLM execution layer.

The protocol intentionally separates:

1. runtime orchestration;
2. model inference;
3. observation delivery;
4. external-state verification;
5. adversarial audit.

A real inference run is mandatory for the Q-LLM-01 final verdict. Mocked model responses, scripted decisions, or hand-authored traces may validate harness mechanics but cannot establish the research claim.

The model adapter must receive only the declared system instructions, objective, available tools, history, and runtime observations. Experiment condition, mutation metadata, scenario labels encoding the condition, and hidden harness state are forbidden inputs.

The adapter must return a machine-readable action proposal and preserve the raw model response as evidence. The runtime, not the model, authorizes and executes the action.
