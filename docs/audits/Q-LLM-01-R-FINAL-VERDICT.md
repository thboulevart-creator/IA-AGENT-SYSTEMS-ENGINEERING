# Q-LLM-01-R — Final Adversarial Verdict

**Verdict: PASS**

## Research question

Can the repository provide a vendor-neutral, auditable runtime boundary that can host a real LLM in Q-LLM-01 without exposing harness-only causal information or losing raw inference evidence?

## Executed evidence

- Branch: `q-llm-01-r-runtime-readiness`
- Tested head: `8826d9778ac969853d187fbfb3309f3afb8cda2f`
- Base: `main @ e89ac8aee33503c5473dab83d6e0a3653634ce96`
- GitHub Actions run: `33975189008`
- Python runtime: CPython 3.12.14
- Unit/adversarial suite: **19 tests, 19 passed**
- Existing RB-B regression suite remained green.
- Formal E1: 20 runs × S0/S1/S2, audit PASS.
- Formal E2: 20 paired runs × S0/S1/S2, causal audit PASS.
- CI job completed successfully.
- Formal evidence artifacts were successfully uploaded.

The CI execution log records the six Q-LLM-01-R readiness tests executing successfully, followed by the existing 13 RB-B tests, for 19 total tests with `OK`.

## Readiness controls validated

1. **Vendor-neutral inference boundary** — `InferenceClient` is a protocol; no provider is hard-coded.
2. **Declared model-visible request** — `LLMRequest` contains system instructions, objective, allowed tools, observation, and history.
3. **Information barrier** — forbidden harness metadata is rejected before `infer()` is called, including nested keys.
4. **Authorization boundary** — a model-selected action outside the allowed action set is rejected.
5. **Raw evidence preservation** — raw model response and inference metadata are retained in `last_exchange`.
6. **Trace integration** — RB-B decision events capture the model exchange associated with the decision.
7. **No implicit one-shot path** — `plan()` is explicitly rejected by the LLM provider so Q-LLM-01 adaptation cannot silently become pre-planning.
8. **Regression safety** — the pre-existing RB-B suite and formal E1/E2 execution remained successful.

## Adversarial determination

The first execution attempt exposed a test-discoverability weakness: the new readiness tests used `pytest` while CI invokes `unittest discover`, so they were initially absent from the 13-test result. This was treated as an evidence defect, not ignored.

The tests were converted to `unittest` and `tests/q_llm_01/__init__.py` was added so CI discovery is explicit. A fresh PR run was then forced by closing/reopening the draft PR, and the corrected suite executed the six new readiness tests. All six passed.

The earlier successful run was **not** accepted as readiness evidence. The corrected run is the evidence used for this verdict.

## Scope boundary

This PASS establishes **runtime/harness readiness only**. It does not establish real-LLM adaptive behavior.

Q-LLM-01 itself remains **BLOCKED** until an authenticated real LLM inference runtime is connected and the locked paired causal experiment is executed. Scripted controllers, mocks, or manually authored responses remain insufficient for that future verdict.

The Q-LLM-01 protocol continues to require real inference, information-barrier enforcement, counterfactual/ablation attacks, independent verification, and sufficient paired executions before any LLM-adaptation PASS.

## Branch integrity

Work remains isolated on `q-llm-01-r-runtime-readiness`. `main` and protected RB-B branches were not modified. PR #2 remains draft and unmerged.
