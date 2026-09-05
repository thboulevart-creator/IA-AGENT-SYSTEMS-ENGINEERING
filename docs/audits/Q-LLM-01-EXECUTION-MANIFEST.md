# Q-LLM-01 — Execution Manifest

**Status:** READY FOR REAL-LLM EXECUTION / BILLING GATED  
**Branch:** `q-llm-01-execution-ready`  
**Protected branches:** untouched

## 1. Execution portal

```text
REAL LLM INFERENCE
        │
        ├── API authenticated
        ├── model/version fixed
        ├── inference configuration fixed
        ├── observation controlled
        └── real calls
              │
              ▼
        Q-LLM-01 EXECUTION
```

The repository may proceed through every preparation and adversarial stage while this portal is closed. No Q-LLM-01 PASS may cross the portal without successful real inference evidence.

## 2. Declared runtime

| Parameter | Locked value / rule |
|---|---|
| Provider | OpenAI Responses API |
| API endpoint | `https://api.openai.com/v1/responses` |
| Default model | `gpt-5.6-luna` |
| Credential | GitHub repository secret `OPENAI_API_KEY` |
| Storage | `store: false` |
| Output protocol | strict JSON Schema |
| Decision vocabulary | RB-B authorized actions + `TERMINATE` |
| Max output tokens | 64 |
| Client timeout | 60 seconds |
| Inference mode | one real call per S2 decision |
| One-shot planning | forbidden |
| Raw response capture | required in runtime exchange evidence |

The exact model identifier returned by the API must be recorded and must match the declared model for a PASS. If the requested model is unavailable or silently substituted, the run is not admissible until the model identity is reconciled.

## 3. Model-visible boundary

The model receives only:

- declared system instructions;
- objective;
- authorized action vocabulary;
- current external observation;
- prior observed history.

The model must not receive:

- experiment condition;
- mutation identifier;
- mutation hook or harness state;
- perturbation instruction;
- expected repair action;
- post-perturbation ground truth;
- hidden run labels encoding normal/perturbed status.

The adapter recursively rejects the explicitly forbidden keys before invoking the client.

## 4. Decision contract

The model must return one strict JSON object:

```json
{"action":"<AUTHORIZED_ACTION_OR_TERMINATE>"}
```

The runtime converts `TERMINATE` to the RB-B `None` termination action. Any unauthorized or malformed action is rejected; it is not silently repaired by the harness.

## 5. Causal execution

For each pair:

```text
same initial state
       │
       ├──────────── normal ────────────┐
       │                                │
       └──── perturbed after WRITE ─────┤
                                        ▼
                              first causal observation
                                        │
                              real LLM decision
                                        │
                              action execution
                                        │
                              independent verification
```

The causal decision is the first LLM decision after the first observation that exposes the controlled external difference. The audit must not use a later repaired observation to manufacture causality.

## 6. Execution sample

Minimum real-LLM S2 sample:

- 20 paired normal/perturbed runs;
- identical scenario IDs within each pair;
- identical seeds/configuration where the runtime exposes them;
- identical initial workspace state;
- identical model/version;
- identical prompt/instructions;
- identical authorized tools;
- identical action budget;
- controlled perturbation only after `WRITE_ARTIFACT` and before the causal observation.

If stochastic variation prevents causal discrimination, increase repetitions rather than lowering the evidentiary threshold.

## 7. Required controls

### S0 — negative control

No observation-conditioned decision path.

### S1 — preplanned control

A prewritten repair path may succeed but cannot count as LLM adaptation.

### S2 — real LLM

The LLM must select the first post-observation action from the observed state.

## 8. Adversarial gate before final verdict

The execution evidence must survive the Q-LLM-01 attacks, with special attention to:

- preplanning;
- condition/metadata leakage;
- framework/tool leakage;
- seed/sampling mismatch;
- context mismatch;
- ineffective or misplaced perturbation;
- tool-claim substitution;
- observation tampering;
- unexplained first decision divergence;
- repair without causal observation;
- systematic repair;
- counterfactual observation ablation;
- alternative explanations.

## 9. Billing gate

The latest isolated smoke invocation reached the real OpenAI endpoint and was rejected with `credit_balance_exhausted`. Therefore the runtime is authenticated and wired but **not executable for inference while the API organization has no available credit**.

This is an infrastructure gate, not experimental evidence for or against LLM adaptation.

## 10. Verdict discipline

- Runtime preparation complete: **PASS** when repository tests and static contracts pass.
- Real inference smoke: **BLOCKED** until an authenticated call completes successfully.
- Q-LLM-01 causal experiment: **BLOCKED** until the minimum real-LLM evidence exists.
- Q-LLM-01 final PASS: forbidden before the full causal and adversarial audit succeeds.

No simulation, scripted provider, manually authored response, or conceptual result may substitute for the real inference gate.
