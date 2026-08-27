# Pheromone consensus experiment — closed gate

## Original question

Does shared evaporating memory plus a consensus/contrarian population split improve the success/work frontier of a fixed-size crow cohort under reactive topology changes?

## Frozen first gate

- agents: 8
- horizon: 70
- graph families: grid6, ladder12, connected ER(36, 0.12)
- adversaries: traffic-aware and reactive-cut
- budgets: b in {1,2}
- seeds: 30
- identical adversary RNG stream for all policies within a paired cell
- no hyperparameter search before the gate.

Controls included:
- shortest replanning;
- true edge-disjoint routing;
- entropy-regularized replanning;
- the same adaptive consensus/contrarian logic with pheromone memory disabled;
- pure pheromone consensus;
- fixed 25% contrarians.

## Gate

Proceed to parameter tuning only if:
- adaptive pheromone beats no-memory adaptive control in at least 2 hostile cells;
- adaptive pheromone beats pure pheromone consensus in at least 2 hostile cells;
- at least one hostile cell satisfies both.

A cell win required either:
- reach probability +0.10; or
- reach probability within 0.02 and at least 10% lower mean work.

## Result

- memory wins: 0
- contrarian wins: 5
- joint wins: 0

**Gate failed. No tuning is permitted.**

## Post-result methodological correction

The analytic epsilon* is valid only for its explicitly stated one-junction objective. The full castle is sequential and adversarial, and the policy's softmax confidence is not calibrated consensus correctness.

No trajectory-level optimality claim is made for epsilon*.

Any reopening requires a new preregistration and strong adversarial-learning baselines (EXP3/EXP4-style and, where feasible, adversarial-MDP methods).
