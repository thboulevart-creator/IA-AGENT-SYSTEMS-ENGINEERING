# Autonomous Adversarial Execution Rules

## Status

These rules govern autonomous execution of protocol-driven validation work in this repository.

## Operating mandate

When the user explicitly delegates autonomy to conduct a validation protocol through its final verdict, execution must continue through the complete protocol and stop only at one of:

- `PASS` — all required evidence exists and all adversarial falsifiers are excluded.
- `FAIL` — a required invariant is violated or a falsifying condition is demonstrated.
- `BLOCKED` — the required proof cannot be executed or completed with the available evidence/capabilities, and no legitimate path remains to complete it.

Autonomy is execution authority, not permission to improvise beyond the protocol.

## Non-negotiable safeguards

1. Never convert missing evidence, non-executable checks, or uncertainty into `PASS`.
2. Distinguish explicitly between:
   - current violation;
   - architectural exposure;
   - absence of evidence / blocked proof.
3. Use adversarial testing: actively construct and attempt to break apparent proofs before accepting them.
4. Preserve causal and temporal ordering required by the protocol; do not infer causality from correlation or final success alone.
5. Treat scripted/controller-specific evidence as limited to what that controller can actually establish; do not generalize it to real LLM behavior without a valid experiment.
6. Re-check negative controls, leakage paths, seeds, budgets, initial-state equivalence, mutation effectiveness, observation independence, trace integrity, and final oracle validity whenever required by the protocol.
7. If a falsifier is found, verdict is `FAIL`; do not patch around it and silently continue as if the original proof remained valid.
8. If a required test cannot be executed, verdict remains `BLOCKED` until a legitimate executable path is established.
9. Do not claim a protocol is validated merely because the implementation passes its own internal tests.
10. Preserve protected-branch isolation at all times.

## Branch and repository locks

- `main` is protected during the active validation protocol: no direct modification, no direct commit.
- `rb-b-harness-restore` is protected: do not modify.
- `rb-b-control-01` is protected: do not modify.
- Experimental implementation work must be isolated on a dedicated branch derived from the validated E2 base.
- The E2 base is `main` at commit `e89ac8aee33503c5473dab83d6e0a3653634ce96` unless a later protocol step explicitly revalidates and changes the base.
- Do not silently rebase or mix work from protected/legacy harness branches into E2.

## Execution discipline

The autonomous agent must:

1. Freeze and verify the current base before implementation.
2. Complete conceptual/adversarial analysis before changing the harness.
3. Design the smallest implementation that can execute the falsification matrix without weakening the protocol.
4. Implement only on the isolated working branch.
5. Run unit, falsification, and formal protocol tests in the required order.
6. Audit evidence independently of the mechanism that produced it wherever the protocol requires independence.
7. Re-break the apparent solution after a successful result to test robustness.
8. Issue the final verdict only after the full evidence chain has been audited.

## E2-specific discipline

For E2, the proof must establish a causal chain of the form:

`controlled external-state difference -> observation difference -> first subsequent decision/action difference -> action addresses the changed condition -> objective resolves`

The experiment must exclude pre-planning, condition leakage, seed differences, incomparable initial state/configuration, ineffective mutation, tool-claim substitution for external observation, instrumentation artifacts, and unexplained first divergence.

A normal and perturbed run must be paired on the same scenario/seed and equivalent initial conditions. The current S2 implementation is a scripted deterministic controller; any final claim must be scoped accordingly unless an actual LLM/controller experiment is separately executed.

## No premature completion

The agent must not stop merely because:

- the code compiles;
- smoke tests pass;
- the perturbed path reaches `PASS`;
- the trace looks plausible;
- a single run demonstrates the expected behavior;
- a controller is capable of repairing after a failure.

Completion requires the protocol's required evidence and adversarial falsification criteria.
