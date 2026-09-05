# Agent Anatomy — V0

**Status:** DRAFT / LEARNING BASELINE  
**Purpose:** establish a falsifiable model of what makes a software/AI system agentic before implementing Agent #1.

> **Core rule:** we do not consider a capability acquired because an AI model describes it. A concept becomes part of the project knowledge only after it is understood, instantiated and tested against evidence.

---

## 1. Why this document exists

The project objective is not to build a sophisticated chatbot. It is to learn how to engineer reliable agents and eventually extract reusable architectural invariants from several agents.

Therefore the first task is to decompose an agent into observable components and relationships without prematurely treating this decomposition as truth.

This document is a **V0 model**, not a final architecture.

Every important claim is subject to challenge, experiment and revision.

---

## 2. Provisional definition of an agent

For this project, an agent is provisionally defined as:

> **A system that pursues an objective by maintaining or using state/context, selecting or generating actions, interacting with an environment through available capabilities/tools, observing the consequences, and deciding whether to continue, recover, verify or terminate.**

This definition deliberately emphasizes the **closed-loop behavior** rather than the presence of an LLM.

An LLM may be the reasoning component of an agent, but an LLM by itself is not automatically an agent.

---

## 3. Agent vs. model vs. workflow

### Model

A model transforms inputs into outputs according to its learned behavior and runtime configuration.

### Workflow

A workflow executes a predefined sequence of operations.

Example:

```text
Input → Step A → Step B → Step C → Output
```

### Agent

An agent has some degree of runtime decision-making over what to do next, based on an objective, state and observations.

A simplified distinction is:

```text
MODEL
  ↓
response

WORKFLOW
  ↓
predefined execution

AGENT
  ↓
objective
  ↓
state/context
  ↓
decision
  ↓
action
  ↓
observation
  ↓
new decision
```

This distinction remains provisional and must be tested against concrete systems.

---

## 4. Provisional anatomy

The first decomposition is:

```text
┌───────────────────────────────┐
│           OBJECTIVE           │
└──────────────┬────────────────┘
               ↓
┌───────────────────────────────┐
│       CONTEXT / STATE         │
└──────────────┬────────────────┘
               ↓
┌───────────────────────────────┐
│       REASONING / PLAN        │
└──────────────┬────────────────┘
               ↓
┌───────────────────────────────┐
│       ACTION SELECTION        │
└──────────────┬────────────────┘
               ↓
┌───────────────────────────────┐
│          TOOL / ACTION        │
└──────────────┬────────────────┘
               ↓
┌───────────────────────────────┐
│          OBSERVATION          │
└──────────────┬────────────────┘
               ↓
┌───────────────────────────────┐
│       DECISION / UPDATE       │
└──────────────┬────────────────┘
               ↓
       ┌───────┴────────┐
       ↓                ↓
   VERIFY            RECOVER
       ↓                ↓
       └───────┬────────┘
               ↓
      CONTINUE / TERMINATE
```

The components below describe the role each element may play. They do **not** yet assert that every agent must implement them as separate software modules.

---

## 5. Objective

The objective defines what the system is trying to accomplish.

Questions:

- Is the objective explicit?
- Is it measurable?
- What counts as success?
- What constraints apply?
- What actions are forbidden?
- When is the objective impossible?

A vague objective creates an ambiguous evaluation target.

For Agent #1, the objective must therefore be machine-testable as far as practical.

---

## 6. Context

Context is the information available to the agent at a given point in execution.

Potential context includes:

- user/task input;
- system instructions;
- tool descriptions;
- retrieved information;
- previous observations;
- relevant state;
- constraints;
- intermediate results.

A key research question is the distinction between **context** and **memory**.

We must not assume that every retained piece of information is memory in the architectural sense.

---

## 7. State

State represents information that describes the current execution situation.

Examples:

- current objective;
- completed actions;
- pending actions;
- tool results;
- errors;
- retries;
- validation status;
- termination status.

State is particularly important because an autonomous system needs a way to know where it is in an execution process.

We will test whether state is explicit, implicit, externalized, model-held, or distributed across several components.

---

## 8. Memory

Memory is provisionally treated as information retained beyond the immediate interaction context and made available for future decisions.

Possible forms include:

- short-lived execution state;
- conversation history;
- persistent records;
- retrieved knowledge;
- learned preferences;
- external databases.

**Important:** memory is not assumed to be mandatory for every agent. This is an empirical question.

---

## 9. Reasoning and planning

The system must determine what to do next.

This can range from:

- a single model decision;
- selecting one tool;
- producing a multi-step plan;
- replanning after observations;
- delegating work;
- evaluating competing actions.

We must distinguish:

**planned behavior** from **actual execution behavior**.

A plan written by a model is not proof that the plan was executed.

---

## 10. Tools and actions

Tools give the system capabilities beyond pure text generation.

Examples:

- search;
- code execution;
- databases;
- APIs;
- file operations;
- calculators;
- external services;
- communication systems.

A tool call creates an important boundary:

```text
MODEL DECISION
      ↓
  TOOL REQUEST
      ↓
EXECUTION LAYER
      ↓
 EXTERNAL EFFECT
      ↓
   OBSERVATION
```

The execution layer must not blindly assume that a requested action succeeded.

---

## 11. Observation

An agent needs information about the consequences of its actions.

An observation can be:

- successful output;
- failure;
- partial result;
- contradictory result;
- timeout;
- malformed response;
- unexpected external state.

Observation is therefore different from intention.

```text
INTENDED ACTION ≠ ACTUAL RESULT
```

This distinction will be central to reliability testing.

---

## 12. Decision loop

The provisional agent loop is:

```text
OBJECTIVE
   ↓
STATE / CONTEXT
   ↓
DECIDE
   ↓
ACT
   ↓
OBSERVE
   ↓
UPDATE STATE
   ↓
VERIFY
   ↓
┌───────────────┬───────────────┬───────────────┐
│ CONTINUE      │ RECOVER       │ TERMINATE     │
└───────────────┴───────────────┴───────────────┘
```

The loop is the most important element to test experimentally.

If a system cannot react meaningfully to observations, it may be better characterized as a workflow with model-generated steps rather than a genuinely adaptive agent.

This is a hypothesis, not yet a final classification rule.

---

## 13. Verification

Verification asks whether the system has sufficient evidence that its objective was actually achieved.

Possible mechanisms:

- deterministic checks;
- schema validation;
- tests;
- comparison against a source of truth;
- secondary model evaluation;
- human approval;
- external confirmation.

A model saying "done" is not itself proof of completion.

This principle will be an invariant candidate for later validation.

---

## 14. Recovery

Recovery handles situations in which the expected path fails.

Examples:

```text
Tool failure
   ↓
retry / alternate tool / revise action / escalate / stop
```

Recovery policy must eventually specify:

- what errors are retryable;
- maximum retries;
- when to change strategy;
- when to stop;
- when to ask a human;
- how failed actions affect state.

An autonomous system without controlled failure handling may simply turn errors into uncontrolled behavior.

---

## 15. Termination

Termination is a first-class architectural concern.

The agent must have conditions under which it stops.

Possible termination states:

- success;
- controlled failure;
- objective impossible;
- authorization denied;
- safety constraint reached;
- retry budget exhausted;
- human escalation;
- timeout.

A system that can continuously generate actions without a bounded termination policy is not considered reliable merely because it is autonomous.

---

## 16. Autonomy levels — V0 hypothesis

For experimentation we will use this provisional scale:

| Level | Description |
|---|---|
| A0 | Model responds only; no external action. |
| A1 | Model can select/use a tool in a single bounded interaction. |
| A2 | System can execute multiple steps toward an objective. |
| A3 | System can observe results and adapt/replan. |
| A4 | System can recover from defined failures and independently terminate/escalate under explicit policies. |
| A5 | System can operate a governed process over time with durable state, evaluation and controlled external effects. |

These levels are **classification hypotheses**, not accepted standards.

They will be revised if experiments reveal that the scale is ambiguous or incomplete.

---

## 17. Reliability dimensions

Every future agent should eventually be evaluated on at least:

| Dimension | Core question |
|---|---|
| Goal fidelity | Did it pursue the correct objective? |
| Execution correctness | Did actions occur as intended? |
| Observation integrity | Did it correctly interpret results? |
| Adaptation | Did it react appropriately to new information? |
| Verification | Did it establish that the result was actually correct? |
| Recovery | Did it handle failures within policy? |
| Termination | Did it stop at the right time? |
| Traceability | Can we reconstruct what happened? |
| Reproducibility | Can the behavior be tested again? |
| Control | Were permissions and constraints respected? |

---

## 18. Failure laboratory — mandatory future tests

Agent #1 must eventually be tested against deliberate failures.

Minimum scenarios:

1. correct task / successful tool;
2. incorrect tool result;
3. tool unavailable;
4. tool timeout;
5. malformed tool response;
6. contradictory information;
7. missing information;
8. impossible objective;
9. unauthorized action;
10. repeated failure;
11. misleading intermediate result;
12. false success condition;
13. unexpected external state;
14. excessive loop/retry behavior.

The purpose is not to make the agent look good.

The purpose is to expose its failure boundaries.

---

## 19. What we deliberately do NOT assume yet

We do not yet assume that:

- an agent requires an LLM;
- an agent requires persistent memory;
- an agent requires a predefined planner;
- every agent requires multi-agent orchestration;
- every agent requires vector databases/RAG;
- more tools necessarily mean more autonomy;
- more context necessarily means better performance;
- a longer prompt creates a better agent;
- a model's reasoning trace is equivalent to its actual internal reasoning;
- successful demonstrations prove reliability;
- a framework's label "agent" proves that the system is agentic.

These are research questions to be resolved by evidence.

---

## 20. Evidence hierarchy for this project

For architectural claims, we will progressively prefer:

```text
E0 — assertion / intuition
E1 — documentation / authoritative description
E2 — observed behavior / reproducible experiment
E3 — automated test / evaluation evidence
E4 — repeated validated behavior under controlled conditions
```

A higher level does not automatically invalidate a lower level; it means the claim has stronger operational support.

No hypothesis should silently become an invariant without evidence.

---

## 21. First implementation target

Agent #1 should be:

- small enough to understand completely;
- useful enough to expose real agent mechanics;
- equipped with at least one external capability/tool;
- observable;
- testable;
- deliberately breakable;
- bounded by explicit permissions and termination conditions;
- simple enough that every architectural component can be traced.

We should optimize for **learning density**, not feature count.

---

## 22. Research questions before Agent #1

1. What is the minimum architecture that qualifies as an agent?
2. Which components are mandatory versus optional?
3. Where exactly does autonomy emerge?
4. What is the role of the model versus the orchestration layer?
5. How is state represented and updated?
6. What distinguishes memory from state and context?
7. How should tools be selected and authorized?
8. How can an agent know that an action succeeded?
9. How should failure and recovery be represented?
10. What guarantees can be deterministic rather than model-dependent?
11. How should autonomy be measured?
12. What architectural properties are reusable across very different agents?
13. Which apparent "agent capabilities" are merely framework features?
14. What must be externalized from the model to make a system reliable?

These questions form the research backlog for the next blocks.

---

## 23. Decision rule for the next step

We do not move directly from this document to a complex implementation.

First:

```text
ANATOMY V0
   ↓
INDEPENDENT CHALLENGE
   ↓
CORRECTIONS / OPEN QUESTIONS
   ↓
VALIDATED BASELINE
   ↓
MINIMAL AGENT DESIGN
   ↓
IMPLEMENTATION
   ↓
FAILURE LAB
   ↓
EVALUATION
```

The next artifact should therefore be the **minimal Agent #1 design**, but only after this anatomy has been challenged and its major assumptions have been identified.

---

## 24. Status

**Current status: DRAFT / NOT VALIDATED.**

This document is a working model. It must not be treated as an architectural invariant until independently challenged and experimentally supported.
