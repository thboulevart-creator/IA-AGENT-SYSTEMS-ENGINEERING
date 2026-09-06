# Q-LLM-01-R — LLM Runtime Readiness & Causal Harness

**Status:** EXECUTION / READINESS AUDIT

## Research question

Can the repository provide a vendor-neutral, auditable runtime boundary that can host a real LLM in Q-LLM-01 without exposing harness-only causal information or losing the model's raw inference evidence?

This block does **not** test whether an LLM adapts. It tests whether the experimental infrastructure is ready to test that claim honestly.

## Acceptance criteria

1. A real-LLM client boundary is vendor-neutral and does not require a specific provider.
2. The model-visible request contains only declared system instructions, objective, tools, observation, and prior observations/history.
3. Harness-only identifiers, mutation controls, hidden state, expected repair, and post-perturbation ground truth are rejected before inference.
4. Model-selected actions are checked against the runtime authorization set.
5. Raw model output and inference metadata are retained alongside the normalized action.
6. The captured exchange is trace-safe and associated with the exact decision that consumed the observation.
7. One-shot planning cannot silently substitute for S2 runtime adaptation.
8. Tests attempt to falsify the boundary, not merely exercise the happy path.
9. No vendor credential or provider-specific implementation is required for this readiness block.

## Non-goals

- No claim of real LLM adaptation.
- No claim of model quality, intelligence, or generality.
- No network inference is simulated as if it were real inference.
- A test double may validate adapter mechanics, but cannot satisfy Q-LLM-01's real-inference gate.

## Adversarial checks

- forbidden-key injection at top level;
- forbidden-key injection nested in observation/history;
- unauthorized model action;
- loss of raw response;
- loss of inference metadata;
- trace serialization failure;
- accidental one-shot adaptation path;
- model-input contamination by harness state.

## Verdict rule

**PASS** requires executable evidence that all readiness tests pass and that no critical boundary attack succeeds.

**FAIL** requires a demonstrated boundary violation.

**BLOCKED** applies if the readiness tests cannot actually be executed in an available runtime.

A PASS here still leaves Q-LLM-01 itself BLOCKED until an authenticated real LLM inference runtime produces the required paired evidence.
