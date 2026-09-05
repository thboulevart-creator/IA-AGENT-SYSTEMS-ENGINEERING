# ADVERSARIAL-COUNTER-EXPERTISE-PROTOCOL

**Version:** V0.1  
**Status:** METHODOLOGY / DRAFT FOR VALIDATION

## 1. Purpose

This protocol establishes independent adversarial counter-expertise as a mandatory methodological step for important architectural work in this project.

Its purpose is to reduce confirmation bias, expose hidden assumptions, identify architectural errors early, and force disagreements between AI analyses to be resolved by evidence rather than authority or model consensus.

## 2. Role of Grok

Grok is used as an **independent counter-expert** for important project blocks.

Grok is not a validation authority. ChatGPT is not a validation authority either.

Agreement between ChatGPT and Grok is not evidence by itself.

The role of counter-expertise is to challenge the current V0, identify weaknesses, propose alternative interpretations, and surface claims that require empirical or documentary verification.

## 3. Mandatory cycle

For each important architectural block:

```text
V0 CONSTRUCTION
      ↓
INDEPENDENT COUNTER-EXPERTISE
      ↓
DISAGREEMENTS / OBJECTIONS
      ↓
CLAIM CLASSIFICATION
      ↓
EVIDENCE / EXPERIMENT / TEST
      ↓
CORRECTION
      ↓
REGRESSION / VALIDATION
      ↓
VERSIONED BASELINE
      ↓
NEXT BLOCK
```

The project should not advance a foundational block merely because the first analysis appears coherent.

## 4. Required counter-expertise behavior

The counter-expert should actively search for:

- incorrect assumptions;
- missing components;
- category errors;
- unjustified architectural abstractions;
- false autonomy claims;
- hidden dependencies;
- failure modes;
- ambiguous definitions;
- unsupported claims;
- unnecessary complexity;
- contradictions with documented behavior;
- cases where the proposed architecture works only on the happy path;
- alternative architectures that materially change the conclusion.

The counter-expert should prefer criticism over confirmation when evidence warrants it.

## 5. Disagreement handling

When ChatGPT and Grok disagree, the project must not resolve the disagreement by majority vote or perceived model quality.

Instead:

```text
DISAGREEMENT
    ↓
WHAT EXACTLY IS THE CLAIM?
    ↓
WHAT EVIDENCE SUPPORTS EACH POSITION?
    ↓
CAN THE CLAIM BE EXPERIMENTALLY TESTED?
    ↓
TEST / PRIMARY DOCUMENTATION
    ↓
RESULT
    ↓
UPDATE KNOWLEDGE STATUS
```

If the issue cannot currently be resolved, it remains explicitly marked **UNKNOWN**, **HYPOTHESIS**, or **BLOCKED**, as appropriate.

## 6. Evidence rule

AI consensus is never sufficient to promote a hypothesis into an invariant.

The project's evidence hierarchy remains authoritative:

- **E0** — assumption / intuition;
- **E1** — authoritative documentation;
- **E2** — controlled reproducible observation;
- **E3** — automated test / evaluation evidence;
- **E4** — repeated validated behavior under controlled or real operating conditions.

Counter-expertise increases scrutiny; it does not replace evidence.

## 7. Separation of responsibilities

The process distinguishes three roles:

### Builder

Constructs the current architecture or hypothesis.

### Counter-expert

Attempts to falsify, weaken, or find omissions in the current architecture.

### Evidence / validation layer

Determines what can actually be established from documentation, experiments, tests, or operational evidence.

One model may perform more than one role during a project cycle, but the roles must remain conceptually distinct.

## 8. Required output of a counter-expertise pass

For important blocks, the counter-expertise should return at minimum:

1. overall assessment;
2. strongest parts of the current proposal;
3. suspected errors;
4. missing elements;
5. unsupported assumptions;
6. disagreements with explicit reasoning;
7. claims requiring evidence;
8. proposed experiments or tests;
9. severity / architectural impact;
10. recommendation: accept, revise, investigate, or reject.

## 9. No automatic authority transfer

A counter-expert must not become an architectural authority merely because it identifies an error.

Every objection itself is a claim and must be evaluated according to the project's evidence rules.

## 10. Scope

This protocol is mandatory for foundational architecture, definitions, interfaces, agent lifecycle models, reliability models, autonomy classifications, factory abstractions, and other decisions whose later reversal could create substantial technical debt.

Minor implementation choices may use a lighter review process when their architectural impact is demonstrably low.

## 11. Relation to project invariants

This protocol reinforces the project's existing principles:

- **Evidence over consensus**
- **No hidden assumptions**
- **No false autonomy**
- **No false PASS**
- **Failure must remain visible**
- **Reproducibility**
- **Traceability**
- **Least necessary complexity**
- **Prove before generalizing**
- **Generalize only after repetition**

It does not override them.

## 12. Status

This protocol is itself a methodological V0 and must be reviewed after several real cycles.

Its effectiveness must eventually be evaluated empirically: whether independent counter-expertise actually detects errors that would otherwise have survived, and whether the process improves architectural quality without introducing disproportionate overhead.
