# ARCHITECTURAL-GOVERNANCE-RULES

**Version:** V0.2  
**Status:** ACTIVE / GOVERNANCE  
**Scope:** Permanent methodological rules for architectural and experimental work

## 1. Purpose

This document is the canonical operational registry for permanent methodological rules discovered during the project.

A rule belongs here when it materially affects how architecture is designed, audited, tested, qualified, or interpreted. The objective is to prevent important lessons from remaining implicit in conversation or being lost after a local implementation is changed.

This registry is complementary to the more specific project protocols. Specific protocols remain authoritative for their domain; this document records the cross-cutting rules that govern the reasoning process itself.

## 2. Mandatory evidence discipline

### GOV-EVID-001 — Observation is not interpretation

A raw technical observation must not be treated as proof of the presumed cause.

Required sequence:

```text
RAW OBSERVATION
    ↓
POSSIBLE INTERPRETATIONS
    ↓
COMPETING HYPOTHESES
    ↓
DISCRIMINATING TEST / DOCUMENTATION
    ↓
VERDICT
```

An error message, log line, timeout, unexpected output, or other symptom is evidence of an observation, not automatically evidence of the hypothesized root cause.

### GOV-EVID-002 — Correction is not validation

A corrective change that removes a symptom does not by itself prove that the original causal diagnosis was correct, nor that the resulting system is qualified.

A fix requires independent validation against the relevant invariant and regression evidence.

### GOV-EVID-003 — AI agreement is not evidence

Agreement between ChatGPT, Grok, Claude, or any other model is not sufficient to establish a technical claim, invariant, or PASS verdict.

Model outputs are hypotheses, critiques, or reasoning inputs unless independently supported by the project's evidence hierarchy.

### GOV-EVID-004 — No false PASS

A PASS may only be issued when the required acceptance condition is supported by the defined evidence.

If evidence is insufficient, contradictory, unavailable, or the test cannot execute, the status must remain FAIL, BLOCKED, UNKNOWN, or an explicitly qualified non-PASS state as appropriate.

### GOV-EVID-005 — Preserve uncertainty

Unresolved uncertainty must remain explicit. The project must not convert uncertainty into confidence merely to enable progression.

## 3. Invariant discipline

### GOV-INV-001 — Invariants must be falsifiable

A proposed invariant must have a meaningful way to attempt to falsify it.

For each invariant, the project should define:

- the property;
- the failure condition;
- the observable evidence;
- the test or experiment capable of exposing the failure;
- the current evidence level;
- the status: HYPOTHESIS / TO-PROVE / VALIDATED / INVALIDATED / BLOCKED.

### GOV-INV-002 — Local fixes must be generalized carefully

A defect discovered in one implementation must not automatically become a universal architectural rule.

Before promotion, determine whether the lesson is:

- implementation-specific;
- component-specific;
- project-wide;
- or a general engineering invariant.

Generalization requires evidence and repeated applicability where appropriate.

### GOV-INV-003 — Qualification is stronger than successful execution

"The system ran successfully" is not equivalent to "the system is qualified."

Qualification requires evidence that relevant failure modes, boundary conditions, and acceptance properties have been exercised at the required level.

## 4. Independent validation and oracle discipline

### GOV-ORACLE-001 — Avoid common-mode validation failure

The system under test and its test oracle should not depend on the same unverified assumption when that assumption determines correctness.

Where practical, validation should use an independent representation, independent calculation, authoritative documentation, or a separately constructed reference.

### GOV-ORACLE-002 — Test harnesses are themselves auditable

A passing test harness is not automatically trustworthy. The harness must be reviewed for hidden assumptions, circular logic, accidental coupling to implementation details, and weak oracles.

### GOV-ORACLE-003 — Failure injection is required for critical rejection properties

If a critical invariant concerns rejection of malformed, incomplete, corrupted, ambiguous, or otherwise invalid input, controlled failure injection should be used to demonstrate that the invalid state is actually rejected and cannot be silently promoted.

### GOV-ORACLE-004 — Independent oracle/reference for critical qualification claims

For critical correctness claims, the qualification harness should, where practical, derive expected outcomes from an independent oracle or reference representation rather than reproducing the implementation's own logic.

If independent validation is impossible, the limitation must be explicit and the claim must not be presented as stronger than the available evidence permits.

## 5. Status and progression discipline

### GOV-STATUS-001 — Evidence status follows evidence, not intention

A planned test, a proposed fix, an expected behavior, or a command intended to demonstrate a property does not count as evidence that the property holds.

### GOV-STATUS-002 — BLOCKED remains BLOCKED

A test that cannot execute because of missing prerequisites, unavailable infrastructure, unavailable data, or another blocking condition must not be represented as PASS.

### GOV-STATUS-003 — Real-data gates come after synthetic adversarial qualification

For high-cost or high-consequence real acquisitions, the project should first establish the relevant safety properties using controlled fixtures, failure injection, recovery tests, and deterministic checks before committing to the full real-data gate.

This does not eliminate the need for real-data validation; it reduces the risk of discovering basic architectural failures during the expensive run.

### GOV-STATUS-004 — Historical success is not current qualification evidence

A historical green test, prior successful run, or previously observed correct behavior does not constitute current qualification evidence when the relevant code, environment, dependencies, harness, or acceptance conditions have changed or cannot be reproduced in the current environment.

Current qualification requires executable, attributable evidence for the current baseline.

## 6. Automatic rule-promotion policy

### GOV-META-001 — Material methodological discoveries are persistent by default

When work in the project reveals a new methodological rule that materially affects architecture, evidence interpretation, testing, qualification, or safety, that rule must be recorded in the appropriate repository governance/protocol document rather than remaining only in conversation.

### GOV-META-002 — Correct repository and scope

Rules must be recorded at the narrowest appropriate scope:

1. project-wide methodological rules → this governance registry;
2. domain-specific rules → the relevant protocol/specification;
3. component-specific rules → the component's qualification/design document;
4. experimental findings → the experiment record and, when generalizable, promoted here.

### GOV-META-003 — Promotion metadata

A newly promoted rule should include, when practical:

- stable identifier;
- concise statement;
- rationale;
- triggering observation or discovery;
- applicability/scope;
- falsification or validation method;
- current status.

### GOV-META-004 — Conversation is not the source of truth

Important architectural rules are not considered durably adopted merely because they were stated or agreed upon in chat. Repository documentation is the durable source of truth.

## 7. Current permanent rules promoted from V3.3 qualification work

The following rules were promoted after the V3.3 downloader qualification work exposed methodological failure modes: interpreting a PowerShell error as confirmation of a previously suspected defect rather than first treating the error as an observation requiring interpretation; and recognizing that runtime qualification requires executable evidence and an independently trustworthy validation oracle.

- GOV-EVID-001 — Observation is not interpretation.
- GOV-EVID-002 — Correction is not validation.
- GOV-ORACLE-001 — Avoid common-mode validation failure.
- GOV-ORACLE-002 — Test harnesses are themselves auditable.
- GOV-ORACLE-003 — Failure injection is required for critical rejection properties.
- GOV-ORACLE-004 — Independent oracle/reference for critical qualification claims.
- GOV-STATUS-004 — Historical success is not current qualification evidence.
- GOV-META-001 through GOV-META-004 — Material methodological discoveries must be durably promoted to the appropriate repository scope.

## 8. Change control

This document is living governance. New rules may be added when supported by project evidence or a clearly documented methodological discovery.

A rule should not be removed or weakened solely because it makes an implementation or experiment inconvenient. Any relaxation should state the reason, scope, evidence, and consequences.
