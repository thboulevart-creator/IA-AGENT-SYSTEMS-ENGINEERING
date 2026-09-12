# Q-E2 — Final Adversarial Verdict

**Verdict: PASS**

## Scope

E2 validates the controlled causal property implemented by the current RB-B S2 controller: a controlled external-state perturbation changes the observed state, causes a different subsequent runtime action, and that action resolves the perturbed objective.

This is **not** a claim of general LLM adaptive behavior. The tested controller is `ScriptedDecisionProvider`.

## Experimental evidence

- Base: `main @ e89ac8aee33503c5473dab83d6e0a3653634ce96`.
- Working branch: `e2-autonomous-adversarial`.
- Formal dataset: 20 paired normal/perturbed runs for each of S0, S1 and S2.
- Total formal E2 executions: 120.
- Pairing: same scenario ID, same seed, same objective version and same initial workspace state.
- Perturbation: deterministic byte corruption after `WRITE_ARTIFACT` tool execution and before the following external observation.
- Normal S2: `READ -> WRITE -> CHECK(PASS) -> terminate`.
- Perturbed S2: `READ -> WRITE -> CHECK(FAIL) -> REPAIR -> CHECK(PASS)`.
- Formal E2 causal audit: PASS.
- Formal E1 baseline audit: PASS.
- Unit + adversarial re-break suite: PASS, 13 tests.
- CI run: GitHub Actions run `33973945681`, all steps successful.
- Formal E2 evidence artifact: `rb-b-formal-e2`, digest `sha256:483cb25a02d28fc6a24af2b3f7851233595d3b488e51fcfe9bd1e57cae4745d1`.

## Adversarial attacks successfully excluded

The final implementation/audit explicitly checks against:

1. pre-planned repair masquerading as adaptation;
2. experiment-condition leakage into the provider;
3. unequal seed/pair conditions;
4. mutation ineffectiveness;
5. invalid mutation placement;
6. tool claim substituted for external state;
7. trace-only causal inference;
8. unexplained first action divergence;
9. repair without the causal FAIL observation;
10. false final PASS/FAIL through independent final-state hashing;
11. tampered causal observation evidence;
12. missing mutation evidence;
13. unequal pair seeds;
14. preplanned repair traces.

## Important residual exposure

`tools.py` and the oracle share the repository's canonical transformation implementation. The formal E2 audit independently computes the expected transformation for its causal evidence, so this shared-code exposure does not invalidate the observed S2 causal divergence/resolution result. However, it remains an architectural exposure and E2 must not be interpreted as proof of complete verifier implementation independence.

## Branch integrity

At final audit:

- `main` remained at `e89ac8aee33503c5473dab83d6e0a3653634ce96`.
- `rb-b-harness-restore` remained at `da578f8acb7cba4f8562ea666d1727c76adc2fb7`.
- `rb-b-control-01` remained at `f16f3a90d5c37ffa78ea80e4fa427c92e107eab0`.
- E2 work remained isolated on `e2-autonomous-adversarial`.
- The validation branch was not merged into `main`.

## Final conclusion

**PASS — E2 is valid within the declared scope: the tested S2 closed-loop controller demonstrates observation-conditioned runtime adaptation to a controlled external perturbation, with paired formal evidence and adversarial falsification tests.**

No claim is made here that an arbitrary LLM would exhibit the same behavior without a separate LLM-level experiment.
