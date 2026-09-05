# Experimental Agent Boundary — RB-B

**Status:** DRAFT / EXPERIMENT SPECIFICATION — NOT VALIDATED  
**Role:** determine experimentally whether a runtime adaptive loop provides a meaningful architectural distinction between a predefined workflow, a one-shot LLM plan, and a closed-loop agent.

> **Core rule:** this experiment must not prove a preferred architecture by definition. It must create observable conditions under which competing classifications can succeed, fail, or become indistinguishable.

---

## 1. Why this block exists

The adversarial review identified a central unresolved question in `01-AGENT-ANATOMY.md`:

> What, if anything, distinguishes a workflow, an LLM-generated plan, and an adaptive agent at runtime?

The current anatomy treats the closed loop as the most important candidate distinction, but this remains a hypothesis.

Therefore we will not yet rewrite the anatomy. We will first test the boundary experimentally.

---

## 2. Claims under test

### C1 — Runtime adaptation

**Claim:** a system that can alter its next action based on an observation has a materially different execution property from a system whose execution path is fixed after planning.

**Status:** HYPOTHESIS.

### C2 — Closed-loop behavior

**Claim:** meaningful adaptation requires a loop in which observation can influence a subsequent decision/action.

**Status:** HYPOTHESIS.

### C3 — Plan/execution distinction

**Claim:** a model-generated plan is not evidence that the corresponding actions were executed.

**Status:** STRONG METHODOLOGICAL CLAIM; operational validation required.

### C4 — External verification

**Claim:** model-reported success should not be treated as equivalent to externally verified success when an external source of truth is available.

**Status:** INVARIANT CANDIDATE; experiment required.

### C5 — Minimality

**Claim:** a useful experimental agent can be constructed without persistent memory, RAG, multi-agent orchestration, or other non-essential complexity.

**Status:** HYPOTHESIS.

### C6 — Autonomy classification

**Claim:** autonomy can be characterized more reliably by observable behavioral axes than by a single ordinal A0–A5 scale.

**Status:** HYPOTHESIS; not changed in the anatomy yet.

---

## 3. Experimental systems

We construct three systems for the same objective and environment.

### S0 — Deterministic workflow

Execution path is fully specified before runtime.

```text
INPUT
  ↓
STEP A
  ↓
STEP B
  ↓
STEP C
  ↓
OUTPUT
```

No runtime choice changes the predefined path.

### S1 — One-shot model planning

The model may choose or generate a multi-step plan once. The runtime then executes that plan without model-driven replanning.

```text
OBJECTIVE
  ↓
MODEL
  ↓
PLAN
  ↓
EXECUTE PLAN
  ↓
RESULT
```

### S2 — Closed-loop adaptive system

The system may choose the next action after observing the result of the previous action.

```text
OBJECTIVE
  ↓
DECIDE
  ↓
ACT
  ↓
OBSERVE
  ↓
UPDATE
  ↓
DECIDE
  ↓
ACT
  ↓
...
  ↓
VERIFY
  ↓
TERMINATE
```

The critical experimental variable is not the presence of an LLM. It is whether observations can causally influence subsequent runtime action selection.

---

## 4. Common objective

All three systems must solve the same small, machine-verifiable task.

Initial target class:

> Create a specified artifact from a supplied input, then establish through an external check that the artifact satisfies a predefined property.

The exact task must be selected so that:

- the objective is unambiguous;
- success is machine-verifiable;
- at least one tool/action is required;
- at least one failure can be injected;
- the task is small enough to understand completely;
- no domain-specific expertise is required to interpret the result.

The task definition itself must not give S2 an advantage by encoding the desired answer in advance.

---

## 5. Controlled variables

Keep constant across S0, S1 and S2 as far as practical:

- objective;
- input;
- available tools;
- tool implementations;
- environment;
- permissions;
- verification target;
- initial state;
- execution budgets;
- failure injections;
- success criteria.

The principal independent variable is the runtime decision structure.

---

## 6. Required instrumentation

Every run must distinguish at minimum:

```text
MODEL INTENT
      ↓
PROPOSED ACTION
      ↓
AUTHORIZED ACTION
      ↓
EXECUTED ACTION
      ↓
OBSERVED RESULT
      ↓
VERIFIED RESULT
      ↓
FINAL SYSTEM STATE
```

These records must not be reconstructed solely from the model's natural-language report.

At minimum record:

- run identifier;
- system variant;
- objective identifier/version;
- input identifier;
- initial state;
- model/configuration identifier where applicable;
- selected action;
- authorization decision;
- tool invocation;
- execution status;
- tool response;
- external state after action where observable;
- verification result;
- retry count;
- elapsed time;
- termination reason;
- final outcome.

---

## 7. Primary metrics

### 7.1 Outcome correctness

- true success;
- true failure;
- false success;
- false failure.

### 7.2 Execution behavior

- number of actions;
- unnecessary actions;
- retries;
- timeout rate;
- execution errors;
- budget consumption.

### 7.3 Adaptation

For S2, measure:

- decisions changed after observation;
- recovery attempts;
- successful recoveries;
- inappropriate continuation;
- premature termination;
- infinite/excessive loops.

### 7.4 Reproducibility

Repeat the same scenario under controlled conditions and measure outcome variance and behavioral variance.

### 7.5 Verification integrity

Measure whether final success agrees with the independent source of truth.

---

## 8. Experiment E1 — Baseline boundary

Run S0, S1 and S2 on the normal successful task.

### Question

Does the closed-loop structure produce behavior that is observably different from deterministic workflow execution and one-shot model planning?

### Required result

Do not declare S2 "more agentic" merely because it has more steps or an LLM loop.

We need evidence that observation-dependent decisions materially affect behavior.

---

## 9. Experiment E2 — Observation-induced branch

Change the environment after the first action so that the originally expected next step is no longer appropriate.

Example structure:

```text
Expected observation → Action B
Unexpected observation → Action C
```

S0 must retain its predefined path.

S1 must retain the already-generated plan unless its implementation explicitly includes runtime replanning.

S2 is allowed to choose differently after observation.

### Question

Can adaptation be demonstrated as a causal consequence of observation rather than as random variation?

---

## 10. Experiment E3 — False success injection

Inject a deliberately misleading result:

```text
TOOL RESPONSE:
status = SUCCESS

EXTERNAL REALITY:
expected side-effect absent
```

The independent verifier must be able to detect the mismatch where a source of truth exists.

### Question

Does the system distinguish:

```text
reported success
```

from:

```text
verified success
```

### Failure condition

Any system that declares success solely because the model or unverified tool response says success must be recorded as a false-success failure.

---

## 11. Experiment E4 — Tool failure

Inject:

- unavailable tool;
- timeout;
- malformed response;
- deterministic execution error.

Measure whether the system:

- retries appropriately;
- chooses an alternative action where allowed;
- updates state correctly;
- terminates when recovery is impossible;
- avoids uncontrolled repetition.

This experiment does not assume that recovery is required for the definition of an agent. It measures recovery as a separate system capability.

---

## 12. Experiment E5 — Reproducibility / nondeterminism

Run identical scenarios repeatedly.

At least 20 runs should be used for any claim about behavioral frequency, unless an earlier experiment establishes that fewer runs are sufficient for a specific deterministic property.

Record:

- outcome;
- action sequence;
- termination reason;
- cost;
- latency;
- verification result.

The purpose is to distinguish:

```text
architectural adaptation
```

from:

```text
model stochastic variation
```

---

## 13. Experiment E6 — Complexity budget

For the first experimental agent, prohibit unless a test demonstrates necessity:

- persistent memory;
- RAG/vector database;
- multi-agent orchestration;
- long-term learning;
- unnecessary external services.

The goal is not to claim these components are bad.

The goal is to determine whether they are necessary to expose the target mechanism.

---

## 14. Failure classification

Every failure must be classified before architectural conclusions are drawn.

### F1 — Objective failure

The system did not achieve the required objective.

### F2 — Execution failure

The intended action was not correctly executed.

### F3 — Observation failure

The system received or represented an incorrect observation.

### F4 — Decision failure

The system had sufficient valid information but selected an inappropriate next action.

### F5 — Verification failure

The system incorrectly accepted or rejected the outcome.

### F6 — Recovery failure

A defined recoverable condition was not handled according to policy.

### F7 — Governance failure

The system exceeded permissions, budget, or other explicit constraints.

### F8 — Instrumentation failure

The experiment cannot establish what actually happened.

F8 is particularly important: an unobservable run must not be converted into PASS by interpretation.

---

## 15. Decision rules

### Rule D1 — No architectural claim from one successful run

A single success demonstrates capability, not a general invariant.

### Rule D2 — No agent classification from labels

The presence of an LLM, tool loop, framework, or "agent" label is not sufficient evidence.

### Rule D3 — No false PASS from missing evidence

If execution or verification cannot establish the outcome, classify the result as **BLOCKED / INCONCLUSIVE**, not PASS.

### Rule D4 — No consensus-as-proof

Agreement between ChatGPT, Grok, or any other model is not evidence of the architectural claim.

### Rule D5 — Preserve competing explanations

If an observed advantage of S2 could be explained by model capability, better prompting, additional computation, or another confounder, record the alternative explanation and design a follow-up experiment.

### Rule D6 — Do not prematurely redefine "agent"

The experiments may invalidate the current definition, refine it, or leave it unresolved.

All three outcomes are valid research results.

---

## 16. Expected evidence table

| Claim | Minimum evidence sought | Status before experiment |
|---|---|---|
| Runtime observation can alter action choice | E2/E3 controlled observation | HYPOTHESIS |
| Closed-loop behavior is architecturally distinct | Repeated controlled comparison | HYPOTHESIS |
| Plan ≠ execution | Instrumented execution trace | STRONG CLAIM / VERIFY |
| Reported success ≠ verified success | False-success injection | INVARIANT CANDIDATE |
| Persistent memory is unnecessary for Agent #1 | Complexity-budget experiment | HYPOTHESIS |
| Recovery is separable from adaptation | Failure experiment | HYPOTHESIS |
| Autonomy should use orthogonal axes | Comparative measurements | HYPOTHESIS |

---

## 17. What this block must NOT decide

This block must not yet decide:

- the final definition of an agent;
- the final anatomy;
- whether an LLM is required;
- the final autonomy taxonomy;
- whether memory is useful in production;
- the architecture of the Agent Factory;
- the number of agents required before generalization;
- the preferred model provider;
- a production architecture.

Those questions remain open unless evidence directly resolves a narrow sub-question.

---

## 18. Exit criteria

RB-B is complete only when:

1. S0, S1 and S2 are implemented or otherwise reproducibly instantiated;
2. the common objective is machine-verifiable;
3. action/execution/observation/verification are independently instrumented;
4. E1–E4 have been executed;
5. failures are classified without hiding uncertainty;
6. at least one controlled comparison tests observation-induced adaptation;
7. at least one false-success injection tests verification independence;
8. the results are recorded with enough evidence to reproduce the conclusion;
9. competing interpretations are explicitly documented;
10. only then is `01-AGENT-ANATOMY.md` reconsidered.

E5 and E6 are recommended before freezing the next anatomy version, but they are not allowed to block the narrowest conclusion if E1–E4 already resolve it.

---

## 19. Next decision gate

After the experiments:

```text
RESULTS
   ↓
CLAIM-BY-CLAIM CLASSIFICATION
   ↓
SUPPORTED / REFUTED / UNKNOWN / BLOCKED
   ↓
ANATOMY V0 REVISION DECISION
   ↓
ONLY IF JUSTIFIED:
ANATOMY V0.1
   ↓
MINIMAL AGENT #1 DESIGN
```

The next block must therefore consume **experimental evidence**, not merely another model's architectural opinion.

---

## 20. Status

**RB-B STATUS: SPECIFICATION DRAFT / NOT EXECUTED / NOT VALIDATED.**

No claim in this document becomes an invariant merely because it is written here.
