# RB-B — Experimental Protocol E1–E4

**Status:** PROTOCOL DRAFT / NOT EXECUTED / NOT VALIDATED  
**Parent:** `docs/02-EXPERIMENTAL-AGENT-BOUNDARY.md`  
**Purpose:** operationalize E1–E4 and fix one common, machine-verifiable objective for S0/S1/S2 without prematurely validating the current agent anatomy.

> **Core rule:** this protocol tests competing explanations. It must not be designed so that S2 wins by definition.

---

## 1. Experimental question

The narrow question is:

> Does the ability of a runtime system to select a subsequent action from an observed result produce a measurable behavioral distinction from a deterministic workflow and a one-shot model-generated plan?

Secondary question:

> Can external verification distinguish actual task success from a reported or tool-reported success?

This protocol does **not** attempt to prove a final definition of "agent".

---

## 2. Common objective

All three systems receive the same initial workspace and the same source artifact.

### Objective O1 — Verified artifact transformation

> **Read a supplied source text file, create the required output artifact containing the canonical transformation of that source, and establish through an independent verifier that the output exactly matches the canonical expected content.**

### Canonical transformation

For source text `source.txt`:

1. read UTF-8 text;
2. remove leading and trailing whitespace;
3. convert all characters to lowercase;
4. write the resulting text to `artifact.txt` using UTF-8;
5. verify exact byte-for-byte equality between `artifact.txt` and the independently computed expected transformation.

The transformation is intentionally deterministic and trivial to verify.

### Machine-verifiable success

Success requires **all** of the following:

```text
source.txt exists
AND
artifact.txt exists
AND
artifact.txt bytes == canonical_transform(source.txt) bytes
AND
independent verifier returns PASS
```

The model's statement that the task is complete is never a success criterion.

### Why this objective

It provides:

- one real external effect (file creation/modification);
- deterministic ground truth;
- an observable tool boundary;
- an independently computable expected result;
- an injectable external-state change;
- a simple repair action;
- no requirement for domain knowledge, RAG, memory, or multi-agent orchestration.

---

## 3. Fixed environment

Each run starts from a fresh isolated workspace containing:

```text
/source.txt
```

The source content is generated from a fixed scenario seed and is known to the test harness, but the expected transformed output is **not supplied directly to the model**.

The available capabilities are exactly:

```text
READ_SOURCE
WRITE_ARTIFACT
CHECK_ARTIFACT
REPAIR_ARTIFACT
```

`CHECK_ARTIFACT` computes the canonical transformation independently and compares it with the actual artifact.

`REPAIR_ARTIFACT` rewrites the artifact using the canonical transformation. It exists so that E2 can test whether an observed mismatch can causally alter a subsequent action.

No persistent memory, RAG, vector database, multi-agent orchestration, learning, or external web service is allowed.

---

## 4. System variants

### S0 — Deterministic workflow

The complete execution path is fixed before runtime:

```text
READ_SOURCE
    ↓
WRITE_ARTIFACT
    ↓
CHECK_ARTIFACT
    ↓
TERMINATE
```

No runtime observation changes the path.

### S1 — One-shot LLM plan

The model receives the objective and available tool descriptions once and produces a complete action plan before execution.

The runtime executes that plan without asking the model for a new decision after an observation.

```text
OBJECTIVE
   ↓
LLM
   ↓
PLAN
   ↓
EXECUTE PLAN
   ↓
TERMINATE
```

If the plan itself contains conditional instructions, those conditions must be explicit in the plan before execution. The model is not allowed to generate a new plan from a runtime observation.

### S2 — Closed-loop adaptive system

The model/runtime may select the next action after each observation.

```text
OBJECTIVE
   ↓
DECIDE
   ↓
ACT
   ↓
OBSERVE
   ↓
DECIDE AGAIN
   ↓
ACT / TERMINATE
```

S2 may use `REPAIR_ARTIFACT` when a valid observation establishes that repair is required.

---

## 5. Critical fairness rule

The variants must share, as far as technically possible:

- objective text;
- source input;
- tool implementations;
- permissions;
- workspace;
- verifier;
- failure injection;
- maximum wall-clock budget;
- maximum action budget;
- model identity and generation configuration for S1/S2;
- logging format.

The unavoidable difference is the **timing and availability of runtime decision-making**.

Because S2 may require additional model calls, total model calls, tokens, latency and cost must be recorded. A raw success-rate advantage alone must not be attributed to adaptation if it can be explained by additional computation.

---

## 6. Run identity and trace

Every run receives a unique `run_id`.

The harness must record independently of model prose:

```text
run_id
experiment_id
system_variant
objective_version
scenario_id
random_seed
model/configuration (if applicable)
initial_workspace_hash
initial_state
planned_actions (S1/S2 when available)
authorized_actions
actual_tool_calls
execution_statuses
raw tool results
external workspace state after each action where observable
verification result
retry/action count
model call count
input/output token counts where available
elapsed time
cost where available
termination reason
final workspace hash
final outcome
```

The model's narrative is supplementary evidence only.

---

## 7. Ground-truth oracle

The experiment harness is the source of truth for final success.

For O1, the oracle computes:

```text
expected = canonical_transform(source.txt)
actual = bytes(artifact.txt)
```

and returns:

```text
PASS  if actual == expected
FAIL  otherwise
```

The oracle must not use the model's interpretation of the tool result.

A run whose final state cannot be inspected by the oracle is **BLOCKED**, not PASS.

---

# E1 — Normal baseline

## 8. Purpose

Determine whether S0, S1 and S2 behave differently on an ordinary successful task before introducing an adaptive challenge.

## 9. Scenario

Initial workspace:

```text
source.txt = fixed UTF-8 test content
artifact.txt = absent
```

No failures or external mutations occur.

Expected successful path:

```text
READ_SOURCE → WRITE_ARTIFACT → CHECK_ARTIFACT → PASS
```

## 10. Procedure

Run each variant against the same set of scenario seeds.

Minimum:

- 20 runs per variant;
- same scenario seed set across variants;
- fresh isolated workspace per run.

## 11. Measures

Primary:

- oracle success rate;
- false success rate;
- false failure rate.

Secondary:

- action count;
- model calls;
- token usage;
- latency;
- cost;
- termination reason.

## 12. Interpretation rule

E1 alone cannot establish that S2 is more agentic.

A difference in efficiency or success may result from prompting, model variance, implementation quality, or additional computation.

E1 is a baseline only.

---

# E2 — Observation-induced branch

## 13. Purpose

Test whether an observation can **causally change a subsequent runtime action**.

## 14. Controlled perturbation

After `WRITE_ARTIFACT` successfully executes, but before the next decision/check, the harness deliberately corrupts `artifact.txt` by changing at least one byte.

The corruption is deterministic from the scenario seed and is recorded by the harness.

The objective remains unchanged: final artifact must equal the canonical transformation.

The expected observation is therefore:

```text
CHECK_ARTIFACT → FAIL / MISMATCH
```

The valid recovery action is:

```text
REPAIR_ARTIFACT
```

followed by:

```text
CHECK_ARTIFACT → PASS
```

## 15. Expected structural behavior

S0:

```text
WRITE → CHECK → TERMINATE
```

It must not acquire a new runtime branch.

S1:

The pre-generated plan executes as written. It may succeed only if the plan happened to contain a recovery path in advance.

That case is recorded as **pre-planned conditional behavior**, not runtime replanning.

S2:

After observing the mismatch, it is permitted to select `REPAIR_ARTIFACT` and then verify again.

## 16. Causal adaptation criterion

A run demonstrates **observation-dependent adaptation** only if all are true:

1. the post-write environment differs from the unperturbed case;
2. the system receives the resulting observation;
3. the subsequent action differs because of that observation;
4. the altered action improves or appropriately resolves the objective;
5. the action difference is not explainable solely by random variation or a prewritten conditional path.

This is the key evidence sought by E2.

## 17. Procedure

Minimum:

- 20 runs per variant;
- paired scenario seeds between normal and perturbed conditions;
- identical initial state before the controlled corruption.

Record the exact action sequence before and after the injected observation.

## 18. Primary measures

- probability of selecting `REPAIR_ARTIFACT` after mismatch;
- probability of correct final verification;
- number of post-observation actions;
- inappropriate continuation;
- premature termination;
- loops/retries;
- time/cost overhead.

## 19. Interpretation

If S2 adapts and S0 does not, that is evidence for a **runtime behavioral distinction**.

It is not yet proof that this distinction is sufficient to define an agent.

---

# E3 — False-success injection

## 20. Purpose

Test whether the system distinguishes a reported success from externally verified success.

## 21. Injection

The tool layer returns:

```text
status = SUCCESS
```

while the actual side effect is deliberately absent or incorrect.

The independent oracle still observes the real workspace.

Example:

```text
WRITE_ARTIFACT
  ↓
TOOL REPORT: SUCCESS
  ↓
REALITY: artifact missing
```

## 22. Required behavior

The system must not obtain a final PASS solely from the misleading tool response.

The independent verifier must return FAIL/BLOCKED according to the actual state.

## 23. Procedure

Minimum:

- 20 runs per applicable variant;
- same injection mechanism;
- fresh workspace per run.

## 24. Measures

- false success rate;
- verifier agreement with ground truth;
- whether recovery is attempted;
- whether termination reason is correct;
- number of unverified claims of completion.

## 25. Critical decision rule

If a system reports success while the oracle establishes failure, the run is a **false-success failure**, regardless of the model's explanation.

If the oracle itself cannot inspect the final state, the run is **BLOCKED**.

E3 directly tests the candidate invariant:

> **Reported success is not equivalent to verified success.**

---

# E4 — Tool failure

## 26. Purpose

Measure failure handling separately from the narrower question of adaptation.

Recovery is not assumed to be part of the definition of an agent.

## 27. Failure scenarios

Use four deterministic injections:

```text
E4-A — tool unavailable
E4-B — timeout
E4-C — malformed response
E4-D — deterministic execution error
```

Each scenario is run independently.

## 28. Expected policy

The implementation must define before execution:

- which failures are retryable;
- maximum retry count;
- whether an alternate action is permitted;
- when termination is required;
- what final state is considered controlled failure.

The experiment does not assume that retry is always correct.

## 29. Procedure

Minimum:

- 20 runs per failure type per variant where the variant supports the relevant behavior;
- same injected fault across paired runs;
- fresh workspace.

## 30. Measures

- controlled recovery rate;
- incorrect retry rate;
- excessive retry rate;
- correct termination rate;
- unauthorized action rate;
- final state integrity;
- latency/cost.

## 31. Interpretation

A system that stops safely after an unrecoverable failure may be behaving correctly even if it does not achieve the original objective.

Therefore E4 must report at least:

```text
OBJECTIVE OUTCOME
+
CONTROL/POLICY OUTCOME
```

These must not be collapsed into a single success percentage.

---

# 32. Cross-experiment classification

Every run receives one primary outcome classification:

```text
PASS
FAIL
BLOCKED
```

Then one or more failure classifications where applicable:

```text
F1 Objective failure
F2 Execution failure
F3 Observation failure
F4 Decision failure
F5 Verification failure
F6 Recovery failure
F7 Governance failure
F8 Instrumentation failure
```

A run can be objectively unsuccessful while being correctly governed. Do not classify that automatically as a system defect without considering the experiment's intended failure condition.

---

# 33. Statistical caution

The initial sample size of 20 runs is a **minimum experimental convention**, not a claim that 20 runs establish a general law.

No percentage from these experiments becomes an architectural invariant by itself.

For small samples, report raw counts alongside percentages.

For any claim that one variant is materially better, report uncertainty and competing explanations rather than relying only on point estimates.

---

# 34. Confounders to monitor

The following can create a false appearance of architectural superiority:

- different model versions;
- different prompts;
- different tool descriptions;
- different tool implementations;
- different token budgets;
- different number of model calls;
- different latency budgets;
- different action budgets;
- hidden state carried between runs;
- different initial workspaces;
- verifier leakage of the expected answer;
- failure injection occurring at different execution points;
- implementation bugs in one variant;
- model stochasticity.

Any unresolved confounder that could change the conclusion must be recorded.

---

# 35. Evidence ledger

For every claim, record:

| Claim | Experiment | Raw evidence | Alternative explanation | Status |
|---|---|---|---|---|
| Observation can change a subsequent action | E2 | TBD | TBD | UNKNOWN |
| Closed-loop execution differs behaviorally from one-shot planning | E2 | TBD | TBD | UNKNOWN |
| Reported success differs from verified success | E3 | TBD | TBD | UNKNOWN |
| Recovery is a separable capability | E4 | TBD | TBD | UNKNOWN |
| The current anatomy's loop is the minimal useful abstraction | E1–E4 | TBD | TBD | UNKNOWN |

No status may be upgraded without recorded evidence.

---

# 36. Exit criteria for E1–E4

The experimental phase is complete only when:

1. O1 is implemented exactly enough to be machine-verifiable;
2. S0, S1 and S2 are reproducibly instantiated;
3. the oracle is independent from model-reported success;
4. E1 has been executed;
5. E2 has been executed with controlled paired perturbations;
6. E3 has been executed with false-success injection;
7. E4 has been executed across the defined failure types;
8. all runs have independent traces;
9. PASS/FAIL/BLOCKED classifications are preserved;
10. confounders are documented;
11. competing explanations are recorded;
12. no architectural conclusion is stronger than the evidence supports.

---

# 37. Decision gate after E1–E4

Possible outcomes are deliberately plural.

### Outcome A — Boundary supported

Evidence shows that observation-dependent runtime decisions create a reproducible behavioral distinction that cannot be adequately explained by fixed planning or random variation.

Then revisit `01-AGENT-ANATOMY.md` and consider narrowing/refining the agent distinction.

### Outcome B — Boundary weakened

The experiments show that S2's apparent advantage is largely explained by extra computation, prompting, model capability, or another factor.

Then revise the hypothesis instead of privileging the loop.

### Outcome C — Boundary unresolved

The evidence is insufficient or confounded.

Keep the anatomy V0 unchanged and design a narrower experiment.

### Outcome D — Verification principle strongly supported

E3 repeatedly demonstrates that external ground truth can disagree with model/tool-reported success.

Then consider promoting the relevant verification principle to a validated invariant, subject to the project's evidence rules.

---

# 38. What happens next

After E1–E4:

```text
RAW RUNS
   ↓
TRACE INTEGRITY CHECK
   ↓
FAILURE CLASSIFICATION
   ↓
CLAIM-BY-CLAIM ANALYSIS
   ↓
ALTERNATIVE EXPLANATIONS
   ↓
ARCHITECTURE REVISION DECISION
```

Only after this gate may `01-AGENT-ANATOMY.md` be revised.

The next implementation artifact is therefore the **experimental harness**, not Agent #1 itself.

---

## 39. Status

**RB-B E1–E4 PROTOCOL: DRAFT / NOT EXECUTED / NOT VALIDATED.**

The common objective and protocol are now fixed as an experimental baseline, but their adequacy remains falsifiable.
