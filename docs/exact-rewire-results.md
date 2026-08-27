# Exact one-for-one rewiring threshold — result

Date: 2026-08-27

## Frozen model

The preregistered finite game used:

- initial castle: five-node K_{2,3};
- source 0, target 4;
- three independent length-2 source-target routes;
- O3p timing: crows move first, then the adversary rewires for the next round;
- up to b genuine one-for-one rewires per round;
- fixed edge count 6;
- connected post-rewire graph;
- lambda_t(source,target) >= lambda_min;
- full-information centralized controller;
- horizon H=6;
- exact adversary enumeration, not sampled seeds.

The workflow completed successfully in GitHub Actions run 33046240653.

## Exact K* result

K* is the minimum number of agents that can force target reach within H=6.

| b | lambda_min=1 | lambda_min=2 | lambda_min=3 | cut sufficiency b+1 |
|---:|---:|---:|---:|---:|
| 1 | 2 | 2 | 2 | 2 |
| 2 | 3 | 3 | 2 | 3 |

All cells resolved within k <= 4.

## Preregistered decision

The preregistered rewiring-penalty signal required:

K* > b+1

in at least one cell.

That never occurred.

Therefore:

**No rewiring penalty was observed on this exact finite instance.**

The experiment is closed without expanding the horizon, graph family, k-range, or timing class.

## What the b=2, lambda_min=3 cell means

Here K*=2 while b+1=3.

This does not contradict the bounded-cut reachability lemma. The lemma says b+1 agents are sufficient in the fixed-footprint cut model; it does not say b+1 are necessary in every other model.

The exact rewire game is O3p:
1. agents move on the current graph;
2. reaching the target succeeds immediately;
3. only then does the adversary edit the next graph.

Also, lambda_min=3 with only six edges on five vertices strongly restricts the adversary's legal next graphs.

So the rewire adversary can be weaker than a current-round cut adversary despite having richer topology edits.

## Validation landmarks

All tests passed before the threshold result:

1. static K_{2,3}: one crow forces reach in two rounds with b=0;
2. transient fixed-footprint cuts: b+1 assigned edge-disjoint paths guarantee arrival, with the exact scheduler respecting the sum-of-path-lengths upper bound;
3. every enumerated rewire successor preserves edge count, connectivity, and lambda_min;
4. a compact single-label temporal graph reproduces the known vertex-Menger violation class: maximum temporal vertex-disjoint packing 1, minimum temporal vertex separator 2.

The temporal landmark is a warning against importing static vertex-connectivity intuition wholesale. It is not claimed as an edge-Menger counterexample for this rewire game.

## Scientific status

This experiment does **not** establish a new threshold theorem.

It establishes an exact negative result for one deliberately small model:

- the hoped-for K* > b+1 separation did not appear;
- b+1 remained sufficient in every tested cell;
- in one highly constrained cell fewer agents sufficed.

The broader question of K* on larger rewiring games remains mathematically open unless prior literature subsumes it, but the repository's stop rule applies: this instance is not expanded merely to search for a positive result.

## Related Phase-4 screen

The preceding known-arsenal 10-seed screen also found 0 fortified cells out of 81 hostile graph/adversary/budget/agent cells: at least one mature baseline achieved P(reach)=1.0 in every screened cell.

That screen was heuristic/adversary-specific; this exact finite-game experiment is minimax. Together they say that the castle configurations tested so far are not demonstrating a hard unexplained regime.
