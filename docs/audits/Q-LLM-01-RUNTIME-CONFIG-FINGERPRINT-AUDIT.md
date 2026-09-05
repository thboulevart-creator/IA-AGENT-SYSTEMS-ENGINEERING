# Q-LLM-01 — OpenAI Runtime Client + Configuration Fingerprint Audit

**Block:** Runtime Client + Configuration Fingerprint  
**Branch:** `q-llm-01-runtime-fingerprint`  
**Scope:** no paid / real LLM inference performed  
**Audit mode:** adversarial static + local contract tests

## Objective

Make Q-LLM-01 executable and falsifiable before the real LLM smoke by ensuring that runtime behavior is explicitly configured, machine-checkable, and pair-comparable.

## Formal contract

A normal/perturbed pair must share one immutable `ExperimentConfiguration`. The fingerprint covers:

- OpenAI provider and Responses endpoint;
- requested model;
- timeout;
- `store:false`;
- structured-output schema, name and strictness;
- maximum output budget;
- pinned runtime-client revision;
- protocol hash;
- prompt-template hash;
- scenario identifier;
- seed;
- initial state;
- token/call budget;
- tools;
- permissions.

Condition-specific observation and mutation state are intentionally excluded from this immutable configuration fingerprint. They belong to the experimental condition layer and must be compared separately under the authorized-perturbation rule.

## Candidate implementation

- `experiments/q_llm_01/openai_client.py`
- `experiments/q_llm_01/fingerprint.py`
- `tests/q_llm_01/test_openai_runtime_contract.py`
- `tests/q_llm_01/test_fingerprint.py`

## Adversarial attacks performed

1. **Configuration aliasing / key-order attack** — canonical serialization is order-independent.
2. **Post-construction mutation attack** — nested configuration is recursively frozen; mutating the source mapping after construction does not mutate the recorded configuration.
3. **Unpinned runtime attack** — `UNPINNED` or missing client revision is rejected.
4. **Missing model identity attack** — a response without the actual returned model is rejected.
5. **Model substitution attack** — requested/returned model mismatch is rejected.
6. **Storage-policy attack** — a response that does not prove `store:false` is rejected.
7. **Incomplete-response attack** — any response status other than `completed` is rejected, with incomplete/error evidence retained in the exception path.
8. **Refusal attack** — refusal output is rejected and cannot become a usable action.
9. **Malformed structured-output attack** — missing/invalid `action` is rejected.
10. **Schema weakening attack** — runtime payload requires `json_schema` with `strict:true` and `additionalProperties:false`.
11. **Secret leakage attack** — configuration record contains no API-key field or API-key environment value.
12. **Pair-equivalence attack** — identical immutable configurations produce identical fingerprints; a seed mutation is detected and reported by field path.

## Evidence

GitHub Actions readiness run `33982243345` completed successfully on commit `bec90fedecc56dbd1e49979d3d49f94df14282ad`. Both the Q-LLM-01 readiness suite and RB-B regression suite completed successfully.

This evidence validates the local/runtime contract tests only. It is **not** evidence of real LLM inference.

## Runtime semantics

The client uses the Responses API with Structured Outputs (`json_schema`, strict mode), records the requested and returned model identities, requires `store:false` evidence, and refuses to treat incomplete/refused/malformed outputs as experimental observations.

No retry policy is introduced in this block: an invocation failure is a runtime failure rather than an opportunity to silently create a second experimental trial with different temporal/network conditions.

## Verdict

**PASS — local executable/falsifiable contract for this block.**

This PASS does **not** promote Q-LLM-01 to a real-LLM PASS. The real inference gate remains explicitly blocked until the paid API smoke is executed.

## Remaining boundary

Still blocked by design:

- actual OpenAI request/response execution;
- empirical verification that the selected model is available to the account at smoke time;
- empirical refusal/incomplete behavior against the live service;
- 20+ normal/perturbed pairs;
- S0/S1/S2 causal analysis;
- counterfactual/ablation;
- final Q-LLM-01 falsification.

Those are not weaknesses hidden by this block; they are explicitly deferred empirical gates.
