# Q-LLM-01 — General LLM Adaptive Behavior

**Status:** PROTOCOL LOCKED / EXECUTION GATED  
**Scope:** real-LLM causal adaptation in the RB-B closed loop

## 1. Research question

Can a real LLM, operating through the RB-B runtime loop, change a subsequent action because of an externally induced state difference that was not available to the model before observation, and use that changed action to resolve the perturbed objective?

This block must not be interpreted as proof of arbitrary or universal LLM generality. The final verdict applies only to the declared model, configuration, task family, and experimental domain.

## 2. Required causal chain

A PASS requires evidence for the complete chain:

```text
same initial state
      -> controlled external perturbation
      -> different externally observable state
      -> LLM receives the changed observation
      -> first relevant post-observation decision differs
      -> difference is attributable to the observation
      -> adapted action is executed
      -> independent verifier confirms objective resolution
```

The causal observation is the first observation after the perturbation that contains the externally changed state. The causal decision is the first LLM action decision that is made after receiving that observation.

## 3. Paired design

For every scenario, run a normal and perturbed member of a pair.

The pair must share:

- model identity/version;
- system instructions;
- task/objective;
- tool definitions;
- tool authorization policy;
- initial workspace state;
- initial context visible to the model;
- sampling/inference configuration;
- scenario identifier;
- execution budget;
- runtime version;
- observation schema.

The only intended experimental difference is the controlled external perturbation, introduced after the designated write action and before the causal observation.

## 4. Information barrier

Before the causal observation, the model must not receive:

- experiment condition labels;
- mutation identifiers;
- scenario metadata that encodes the condition;
- hidden harness state;
- perturbation instructions;
- expected repair action;
- post-perturbation ground truth.

The audit must statically and dynamically verify the information barrier where feasible.

## 5. Controls

### S0 — no adaptation opportunity

A fixed non-adaptive controller provides a negative control. It must not be able to use the changed observation to select a different runtime action.

### S1 — preplanned control

A controller may contain a prewritten conditional repair path. If it produces the same repair sequence without requiring a post-perturbation LLM decision, this does not count as LLM adaptation.

### S2 — real LLM controller

The LLM receives observations through the runtime and selects the next action. The provider must not be given experiment-condition information.

## 6. Minimum execution target

Minimum: **20 paired normal/perturbed runs** for the real-LLM S2 condition for the declared scenario family, with additional repetitions when stochasticity prevents reliable causal discrimination.

A single successful demonstration is insufficient.

## 7. Mandatory adversarial attacks

The audit must attempt to falsify the conclusion through at least:

1. pre-planning;
2. experiment-condition leakage;
3. hidden metadata leakage;
4. prompt leakage;
5. framework/tool leakage;
6. seed or sampling mismatch;
7. context mismatch;
8. budget/call-count mismatch;
9. mutation ineffectiveness;
10. invalid mutation placement;
11. tool-claim substitution for external state;
12. observation tampering;
13. trace-only inference;
14. unexplained first action divergence;
15. repair without causal observation;
16. opportunistic/systematic repair;
17. false final PASS;
18. false final FAIL;
19. benchmark/task artifact;
20. removal/ablation of the causal observation;
21. alternative explanation for action divergence;
22. scope overclaim beyond tested model/task family.

Critical attacks are 1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 14, 15, 20 and 21.

## 8. Counterfactual requirement

At least one controlled ablation must remove or neutralize the causal observation while preserving the rest of the pair. The audit must verify that the claimed observation-conditioned adaptation does not survive unchanged through a hidden alternate information channel.

## 9. Independent verification

Final objective resolution must be checked from external state, not from the LLM's claim and not solely from tool-return text.

Where the tool implementation and verifier share transformation logic, the audit must independently derive expected state for the causal evidence and record the residual architectural exposure.

## 10. Verdict rules

- **PASS:** all critical causal requirements are evidenced, adversarial attacks are excluded, and the declared scope is not exceeded.
- **FAIL:** a falsifier demonstrates that the claimed adaptation is not causal, the information barrier is violated, or the objective resolution evidence is invalid.
- **BLOCKED:** required execution/evidence cannot be obtained or a critical condition cannot be discriminated.

Missing evidence is never PASS.

## 11. Scope boundary

A PASS means:

> The declared real LLM, under the declared runtime, configuration, task family, and observation interface, demonstrated observation-conditioned causal adaptation under the paired perturbation protocol.

It does **not** mean:

> all LLMs adapt generally in all environments.

Generality must be established by additional model, task, and environment coverage in later blocks.

## 12. Execution gate

No final PASS may be issued until the repository contains executable evidence from an actual LLM inference runtime. A scripted controller, manually authored response, or conceptual simulation is not sufficient.
