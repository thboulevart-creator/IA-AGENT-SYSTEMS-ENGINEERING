# RB-B-HARNESS-CONTROL-01 — Harness Control Gate

**Status:** CONTROL IMPLEMENTED / LOCAL CONTROL TESTS PASS / E1–E4 NOT YET VALIDATED
**Parent:** `RB-M8 — RULE-PROMOTION-GATE`
**Scope:** experimental harness only
**Foundations modified:** NONE

## 1. Objective

Make the RB-B harness capable of supporting a controlled E1–E4 experiment without allowing the implementation to encode the desired E2 result or collapse execution evidence into runner claims.

The four controls from RB-M8 are:

1. observer independence is architectural, not a provenance label;
2. external state is distinct from system knowledge;
3. requested action, executed action, external side effect and verified property remain distinct;
4. the harness coordinates the experiment but is not the authority for objective truth.

## 2. Corrections implemented

### 2.1 External observer

`experiments/rb_b/observer.py` introduces `ExternalObserver`, which independently reads the workspace and computes file hashes. Tool claims are carried separately from observed external state.

The observer therefore does not merely replay the runner's status claim.

### 2.2 Runtime decision neutrality

`ScriptedDecisionProvider` no longer receives or branches on the experiment identifier or fault plan. Recovery is selected from the observed runtime result (`CHECK_ARTIFACT` failure), not from knowledge that the current run is E2.

The provider remains a deterministic structural stand-in, not an LLM. Therefore this control gate does not establish LLM behavior.

### 2.3 Explicit temporal order

The runner now enforces:

```text
PROPOSE
→ AUTHORIZE
→ EXECUTE
→ EXTERNAL MUTATION (if scenario requires)
→ OBSERVE
→ NEXT DECISION
```

For E2, the corruption is applied before the corresponding external observation is delivered to the decision loop.

### 2.4 Evidence-layer separation

The trace now records separately:

```text
ACTION REQUESTED
ACTION AUTHORIZED
ACTION EXECUTED
TOOL CLAIM
EXTERNAL STATE OBSERVED
OBJECTIVE VERIFIED
```

The final outcome is computed by the O1 oracle from the workspace rather than from model/provider prose or the tool's success claim.

### 2.5 E4 fail-closed behavior

Tool execution errors and malformed responses now terminate the run as controlled tool failure rather than causing the runner to continue automatically to `CHECK_ARTIFACT`.

No automatic retry policy is claimed. This is a deliberate, predeclared fail-closed policy for this narrow harness.

### 2.6 Trace serialization

Binary tool payloads are encoded for JSONL trace persistence rather than causing the harness itself to fail during result serialization.

## 3. Control tests

The control test suite verifies:

- byte-exact independent oracle behavior;
- missing artifact classified as objective `FAIL` rather than `BLOCKED`;
- observer detects absent external artifact despite a tool claim of success;
- all three variants complete the normal baseline successfully;
- E2 mutation occurs before the observation of the affected action;
- S2 performs repair only after the observed verification failure;
- the decision provider has no experiment input;
- E3 preserves tool `SUCCESS` while the independent oracle returns `FAIL`;
- E4 execution failure terminates before the fixed path proceeds to verification.

Local execution result on the control revision:

```text
8 tests
8 passed
0 failed
```

Additional local smoke execution covered E1/E2 across S0/S1/S2 and E3/E4 fault injection. These smoke runs are recorded only as implementation checks; they are **not** treated as the formal E1–E4 experimental dataset.

Observed structural smoke behavior:

```text
E1: S0 PASS / S1 PASS / S2 PASS
E2: S0 FAIL / S1 FAIL / S2 PASS
E3: tool SUCCESS / oracle FAIL
E4: controlled failure / no automatic continuation to CHECK
```

These observations are implementation evidence only. They do not yet establish the architectural claims under the formal RB-B protocol.

## 4. Remaining limitations

The control gate does not yet prove:

- that the observer is independently correct in a broader sense;
- that S2 is generally adaptive beyond this O1 task;
- that the runtime distinction survives an actual LLM implementation;
- that recovery is universally desirable;
- that the A0–A5 taxonomy should change;
- that the current anatomy is complete.

The oracle itself remains a component that requires validation; independence does not imply infallibility.

## 5. Gate decision

### Controls

| Control | Status |
|---|---|
| Observer reads external state independently | PASS — control test |
| Experiment-specific E2 knowledge removed from provider | PASS — structural test |
| Mutation precedes affected observation | PASS — control test |
| Evidence layers remain distinct | PASS — inspected/tested structure |
| Final success comes from O1 oracle | PASS — existing + regression test |
| E4 policy is explicit and fail-closed | PASS — control test |

### Gate

**RB-B-HARNESS-CONTROL-01: PASS**

This PASS authorizes progression to the formal E1–E4 execution stage. It does **not** validate RB-B, S2, or the agent anatomy.

## 6. Next block

Proceed to controlled execution of E1 first, inspect the resulting traces, then determine independently whether E2 can be opened.

```text
RB-B-HARNESS-CONTROL-01  PASS
        ↓
E1 CONTROLLED BASELINE
        ↓
TRACE / CONFONDER INSPECTION
        ↓
E2 GATE
```

`01-AGENT-ANATOMY.md`, `02-EXPERIMENTAL-AGENT-BOUNDARY.md`, and `03-RB-B-EXPERIMENT-PROTOCOL-E1-E4.md` remain unchanged.
