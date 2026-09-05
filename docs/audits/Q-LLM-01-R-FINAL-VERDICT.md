# Q-LLM-01-R — Final Adversarial Verdict

**Verdict: BLOCKED**

## Research question

Can the repository provide a vendor-neutral, auditable runtime boundary that can host a real LLM in Q-LLM-01 without exposing harness-only causal information or losing raw inference evidence?

## Work completed

- Created a vendor-neutral `InferenceClient` protocol and `LLMRequest` / `LLMResponse` boundary.
- Created `LLMDecisionProvider` conforming to the existing RB-B `DecisionProvider` action contract.
- Added an explicit information barrier rejecting harness-only identifiers, perturbation metadata, hidden state, expected repair, and post-perturbation ground truth before inference.
- Added runtime authorization checking for model-selected actions.
- Added raw model response and inference metadata capture.
- Added RB-B decision-trace capture of the model exchange.
- Added adversarial tests for leakage, nested leakage, unauthorized actions, raw-output preservation, and one-shot planning.
- Locked the readiness acceptance contract in `docs/audits/Q-LLM-01-R-PROTOCOL.md`.
- Created draft PR #2 against `main`; no merge was performed.

## Adversarial finding

The implementation contains a potentially executable readiness test suite, but the available session environment cannot execute the repository checkout or retrieve a GitHub Actions run for the new branch. A direct local clone was also unavailable because outbound network resolution is not available in the execution container.

The repository's workflow is configured to run on pull requests and on the readiness branch, but no workflow run is observable for the readiness commits through the available GitHub Actions interface.

Therefore the critical acceptance requirement — **actual execution evidence that the readiness tests pass** — is missing.

## Why this is BLOCKED, not PASS

Static inspection shows the intended controls are present, but static inspection is not execution evidence. The project rule is explicit: missing evidence is never PASS.

## Why this is BLOCKED, not FAIL

No executable test result demonstrates that the adapter boundary is broken. The absence is an evidence/execution limitation, not a falsifying result.

## Required condition to reopen

Execute the repository test suite for this branch in a real Python 3.12 runtime, including at minimum:

- `tests/q_llm_01/test_adapter_readiness.py`;
- the existing RB-B unit suite;
- the existing E1/E2 regression suite;
- trace serialization coverage for the new `model_exchange` field.

Then record the exact command, environment, commit SHA, test count, failures, and CI run/artifact evidence.

## Scope boundary

This BLOCKED verdict does not change Q-E2's prior PASS and does not unblock Q-LLM-01. Q-LLM-01 still requires a real authenticated LLM inference runtime and the full paired causal experiment.

## Branch integrity

Work remains isolated on `q-llm-01-r-runtime-readiness`. The protected `main` and prior E2 branches were not modified. PR #2 remains draft and unmerged.
