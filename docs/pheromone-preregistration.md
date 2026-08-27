# Pheromone consensus experiment — preregistered gate

## Question

Does shared evaporating memory plus a confidence-dependent contrarian minority improve the success/work frontier of a fixed-size crow cohort under reactive topology changes?

This is an engineering experiment, **not a novelty claim**. Pheromone routing, stigmergy, exploration/exploitation mixtures, and adversarial routing all have substantial prior art.

## Freeze before results

First gate:

- agents: 8
- horizon: 70
- graph families: 6x6 grid, ladder-12, connected ER(36, 0.12)
- adversaries: none, traffic-aware, reactive-cut
- hostile budgets: b in {1,2}
- seeds: 30
- policy/adversary random streams are separated.

Pheromone defaults are frozen in PheromoneConsensusPolicy. No hyperparameter search is allowed before the gate result.

## Memory channels

1. progress: decayed reinforcement on traversals that reduce current graph distance;
2. failure: non-progress moves and extra penalty when a recently used edge is rewired away;
3. volatility: decayed rewiring activity around incident vertices;
4. corroborating evidence: decayed observation count retained for instrumentation.

The current shortest-distance term is available to conventional baselines too; pheromones add temporal history, not hidden target information.

## Policies

- replan
- true edge-disjoint
- entropy-regularized replan
- adaptive consensus with memory disabled
- pheromone consensus, no contrarians
- pheromone + fixed 25% contrarians
- pheromone + adaptive contrarian fraction

## Adaptive contrarian rule

At a junction with d exits, n co-located crows, and estimated consensus reliability p,

epsilon* = A(d-1)/(d-1+A)

where

A = ((1-p)/(p(d-1)))^(1/(n-1)).

This is the closed-form optimum for the toy objective P(at least one crow chooses the correct branch), assuming contrarians choose uniformly among non-consensus branches.

In the full castle p is a model confidence (softmax top probability), so epsilon* is a heuristic transfer, not a theorem.

## Gate

A hostile cell counts as a win over a control if either:

- reach probability improves by at least 0.10; or
- reach probability is within 0.02 and mean work improves by at least 10%.

Proceed to parameter tuning only if:

- adaptive pheromone beats the no-memory adaptive control in at least 2 hostile cells;
- adaptive pheromone beats pure pheromone consensus in at least 2 hostile cells;
- at least 1 hostile cell satisfies both.

If the gate fails, do not optimize crow count, evaporation, weights, or consensus temperature.
