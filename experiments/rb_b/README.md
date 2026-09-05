# RB-B experimental harness

Minimal, local, deterministic harness for the E1–E4 protocol in `docs/03-RB-B-EXPERIMENT-PROTOCOL-E1-E4.md`.

## Scope

This is an **experimental laboratory**, not Agent #1 and not a production framework.

It implements:

- O1 verified artifact transformation;
- S0 deterministic workflow;
- S1 one-shot plan execution;
- S2 observation-driven closed loop;
- independent byte-exact oracle;
- deterministic E2 external corruption;
- E3 false-success injection;
- E4 unavailable/timeout/malformed/execution-error faults;
- structured JSONL traces;
- deterministic decision-provider abstraction.

`ScriptedDecisionProvider` is deliberately **not an LLM**. It is a controlled stand-in used to test the runtime architecture without making an external model/API a prerequisite. Therefore these runs cannot establish claims about LLM quality.

## Run

From the repository root:

```text
python -m experiments.rb_b.harness --experiment E1 --variant S0 --runs 20
python -m experiments.rb_b.harness --experiment E1 --variant S1 --runs 20
python -m experiments.rb_b.harness --experiment E1 --variant S2 --runs 20

python -m experiments.rb_b.harness --experiment E2 --variant S2 --runs 20
python -m experiments.rb_b.harness --experiment E3 --variant S0 --runs 20
python -m experiments.rb_b.harness --experiment E4-D --variant S0 --runs 20
```

The default output is `experiments/rb_b/results.jsonl`.

## Trace rule

The final outcome is established by the independent oracle, not by model/provider prose or tool-reported success. Workspace hashes are captured after tool execution and in the final state.

No result from this harness should be promoted to an architectural invariant until the protocol's evidence and confounder rules have been applied.
