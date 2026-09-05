# RB-M8 — RULE-PROMOTION-GATE

**Status:** COMPLETED / PROMOTION DECISIONS RECORDED / NO FOUNDATION MODIFICATION
**Parent:** `RB-M7 — FOUNDATION-CONTRADICTION-MAPPING`
**Purpose:** classify cross-domain mined rules before they can influence the RB-B protocol or be treated as project invariants.

> **Core rule:** a mined rule is not promoted because it is elegant, repeated across repositories, or endorsed by AI models. It is promoted only to the narrowest status justified by existing project evidence and explicit scope.

---

## 1. Decision vocabulary

Each candidate is assigned one of:

- **EXISTING** — already represented in the current foundations; no new rule is imported.
- **PROMOTE-TO-METHODOLOGY** — safe as an explicit methodological control because it restates an existing project principle without claiming empirical validation.
- **PROMOTE-TO-EXPERIMENTAL-CONTROL** — may constrain an experiment, but does not become an architectural invariant.
- **REQUIRES-EXPERIMENT** — materially stronger than the current evidence and must be tested before adoption.
- **DEFER** — potentially useful, but outside the current RB-B question or requires a later architectural context.
- **REJECT-AS-GENERAL-RULE** — source-specific, over-broad, or contradicted by the current foundations/counterexamples.

No candidate is promoted directly to **INVARIANT VALIDATED** by this gate.

---

## 2. Existing foundations remain authoritative for this stage

`01-AGENT-ANATOMY.md` remains a draft learning baseline. It already distinguishes objective, state/context, action selection, execution, observation, decision, verification and recovery, while explicitly requiring challenge and evidence before treating the anatomy as invariant.

`02-EXPERIMENTAL-AGENT-BOUNDARY.md` explicitly requires the RB-B experiment to test competing explanations rather than define S2 as the winner. It also distinguishes proposed action, authorized action, executed action, observed result and verified result, and states that missing evidence must not become PASS.

`03-RB-B-EXPERIMENT-PROTOCOL-E1-E4.md` operationalizes the same controls and explicitly requires independent oracle verification, controlled perturbation, preservation of competing explanations and PASS/FAIL/BLOCKED classification.

Therefore mining is additive only where it exposes a genuine gap. It must not silently overwrite these foundations.

---

## 3. Candidate classification matrix

| # | Candidate rule | Classification | RB-B impact | Decision reason |
|---|---|---|---|---|
| 1 | Producer ≠ semantic authority | EXISTING + METHODOLOGY | Indirect | Already implied by separation of tools, execution layer, observation and verification. Useful governance rule, but not a new RB-B invariant. |
| 2 | Evidence ≠ decision | EXISTING | Direct | Already central to observation → decision distinction and C1/C2. |
| 3 | AI ≠ authority | EXISTING + METHODOLOGY | Direct | Already encoded by evidence-over-consensus and model prose being supplementary evidence. |
| 4 | UNKNOWN ≠ PASS | EXISTING + METHODOLOGY | Direct | Explicitly present in Anatomy/Boundary/Protocol and project no-false-PASS rule. |
| 5 | Provenance ≠ independent proof | PROMOTE-TO-EXPERIMENTAL-CONTROL | **Critical** | RB-M7 exposed that instrumentation provenance does not establish observer independence. Must become a harness design control, not an invariant yet. |
| 6 | Actual lineage only | PROMOTE-TO-EXPERIMENTAL-CONTROL | Indirect | Useful to prevent the trace/oracle from inventing causal ancestry, but full lineage architecture is outside RB-B. |
| 7 | Technical success ≠ external success ≠ objective success ≠ verified success | PROMOTE-TO-EXPERIMENTAL-CONTROL | **Critical** | Directly sharpens E3 and trace semantics. Current protocol already separates reported vs verified success; the layered distinction should be explicit in harness design. |
| 8 | No silent fallback as success | EXISTING + METHODOLOGY | Direct for E4 | Already required by no-false-PASS and explicit failure classification. E4 still needs a concrete predeclared policy. |
| 9 | Transformation may invalidate inherited validation | DEFER | None | Relevant to provenance/data lineage but not necessary for O1/E1-E4. Importing it now would add complexity without testing value. |
| 10 | World truth ≠ agent knowledge | PROMOTE-TO-EXPERIMENTAL-CONTROL | **Direct** | Useful for E2: the externally mutated workspace is reality; the agent's prior state is knowledge, not truth. This can be tested without adopting a full temporal model. |
| 11 | Full dependency chain matters | DEFER | None for RB-B | Important for future provenance/temporal experiments, but O1 has a deliberately small dependency graph. |
| 12 | Contradiction history persists | DEFER | None | Governance capability outside current boundary experiment. |
| 13 | Challenge ≠ modification | EXISTING + METHODOLOGY | Indirect | Compatible with adversarial protocol; does not alter RB-B execution mechanics. |
| 14 | Frozen ≠ incontestable | EXISTING + METHODOLOGY | Indirect | Already embedded in the project's challenge methodology. No RB-B change required. |
| 15 | Criticality follows impact | PROMOTE-TO-METHODOLOGY | Process | Compatible with project governance and useful for deciding audit depth, but not an empirical agent invariant. |
| 16 | Uncertainty escalates until evidence supports de-escalation | PROMOTE-TO-METHODOLOGY | Direct | Compatible with BLOCKED/UNKNOWN handling and prevents optimistic interpretation. |
| 17 | Orchestrator ≠ domain authority | PROMOTE-TO-EXPERIMENTAL-CONTROL | **Direct** | RB-M7 identified ambiguity around “harness as source of truth.” The harness coordinates; the oracle determines the tested property; environment is the external state. These roles must not be conflated. |
| 18 | External failure ≠ business success | EXISTING + METHODOLOGY | Direct | General form already exists as execution failure vs objective outcome separation in RB-B. |
| 19 | Negative information preserved | PROMOTE-TO-METHODOLOGY | Experimental record | Supports preservation of FAIL/BLOCKED and unsuccessful recovery attempts; does not yet create a new agent invariant. |
| 20 | Context conditioning | DEFER | None | Important for cross-domain learning, but not needed for the narrow O1 boundary experiment. |

---

## 4. Rules that are genuinely new for RB-B

After removing rules already present in the foundations, only four controls materially sharpen the current experiment:

### R-B8.1 — Observer independence is a property, not a provenance label

A trace saying that it was generated “independently” is insufficient. Independence must be established from architecture and data flow.

For RB-B, the observer must not merely repeat runner/tool claims. Where practical it must inspect the external workspace/state through its own observation path.

**Status:** EXPERIMENTAL CONTROL, not validated invariant.

### R-B8.2 — Separate external state from system knowledge

The workspace/environment is the state being acted upon. The observation is the information delivered to the decision system about that state. A prior system state or tool report is not automatically equivalent to current external reality.

**Status:** EXPERIMENTAL CONTROL.

### R-B8.3 — Separate four success layers

RB-B records must distinguish:

```text
ACTION REQUESTED
    ↓
ACTION EXECUTED
    ↓
EXTERNAL STATE / SIDE EFFECT
    ↓
OBJECTIVE PROPERTY VERIFIED
```

Tool/model claims may be recorded as claims, but must not collapse these layers.

**Status:** EXPERIMENTAL CONTROL.

### R-B8.4 — Harness is coordinator, not truth authority

The harness controls the experimental scenario and records the run. It must not be treated as the source of truth merely because it orchestrates the experiment.

For O1:

```text
ENVIRONMENT = actual external state
OBSERVER = independently observes state
ORACLE = determines whether O1's property is satisfied
HARNESS = coordinates experiment and records evidence
SYSTEM = acts/decides
```

The oracle itself remains subject to validation; “independent” does not mean infallible.

**Status:** EXPERIMENTAL CONTROL.

---

## 5. Rules explicitly NOT promoted now

The following are intentionally deferred despite being valuable in the source systems:

- full bitemporal validity/knowledge model;
- dependency-chain admissibility framework;
- contradiction registry as a runtime component;
- upward-challenge machinery inside the agent loop;
- learning lifecycle/status model;
- contextual generalization rules from the content domain;
- transformation lineage as a general domain invariant;
- production governance abstractions.

Reason: these would expand the RB-B experiment beyond its narrow research question and create new variables before the current harness is controlled.

---

## 6. Important non-promotion: “tool result is never truth” is rejected

A mined rule must **not** be generalized into:

> “A tool result can never be a source of truth.”

That statement is too strong.

A tool may legitimately be designated as an authoritative source for a specific property by an explicit contract.

The correct RB-B formulation is narrower:

> **A tool/model result is not authoritative for final objective success by default; authority must be explicitly designated by the experiment contract.**

For O1, final success authority is the independently implemented oracle over actual workspace state.

---

## 7. Promotion gate result

### Promoted for RB-B harness control

1. Observer independence must be architectural, not merely claimed.
2. External state and system knowledge must remain distinct.
3. Requested/executed/side-effect/verified-success layers must remain distinct.
4. Harness coordination must remain distinct from truth authority.

### Not promoted as invariants

All four remain experimental controls until implementation and tests demonstrate that they are correctly enforced and useful.

### Foundation modification

**NONE.**

`01-AGENT-ANATOMY.md` remains unchanged.

`02-EXPERIMENTAL-AGENT-BOUNDARY.md` remains unchanged.

`03-RB-B-EXPERIMENT-PROTOCOL-E1-E4.md` remains unchanged at this gate.

The current implementation remains **FAIL** against the controls above and therefore RB-B remains **BLOCKED**.

---

## 8. Decision for next block

Proceed to:

> **RB-B-HARNESS-CONTROL-01**

Required implementation work:

1. decouple the observer from runner-generated claims;
2. remove scenario-specific E2 recovery logic from the decision provider;
3. make the environment mutation occur at a formally defined point;
4. enforce the sequence:

```text
PROPOSE
→ AUTHORIZE
→ EXECUTE
→ EXTERNAL MUTATION (when scenario requires)
→ OBSERVE
→ NEXT DECISION
```

5. record requested/executed/external-state/observation/verification separately;
6. define E4 retry/termination policy before execution;
7. add anti-bias tests proving E2 is not won by construction;
8. do not execute E1–E4 until the control gate passes.

---

## 9. Final verdict

**RB-M8: PASS — promotion gate completed.**

This PASS means the classification gate itself is complete and produced bounded decisions. It does **not** mean RB-B is validated.

Current global state:

```text
RB-M8                    PASS
RB-B-HARNESS-CONTROL-01  NEXT
RB-B E1–E4               BLOCKED
RB-B validation          BLOCKED
ANATOMY V0               UNCHANGED
```
