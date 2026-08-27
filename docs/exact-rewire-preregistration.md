# Exact one-for-one rewiring threshold — preregistration

## Question

For the exact bounded rewiring model, where does the minimum guaranteed-agent threshold sit relative to the fixed-footprint cut floor b+1?

The primary quantity is

K*(b, lambda_min; H=6, O3p),

the minimum number of centrally coordinated agents that can **force** target reach within H=6 against **every** legal adversary response in the finite game.

This is deliberately a finite-instance measurement, not a claimed universal theorem.

## Frozen castle

Initial graph: K_{2,3} on five vertices.

- source s = 0
- target t = 4
- middle vertices = {1,2,3}
- edges = {(s,i),(i,t): i in {1,2,3}}
- |E| = 6
- initial lambda(s,t) = 3
- initial shortest-path distance = 2

The instance is intentionally small enough for exact backward induction while still beginning with three genuinely edge-disjoint s-t routes.

## Frozen timing: O3p

For each round:

1. controller observes current graph and all crow positions;
2. controller chooses all moves jointly;
3. moves execute on the current graph;
4. reaching target terminates successfully;
5. adversary observes the realized positions;
6. adversary performs up to b one-for-one rewires for the next round.

This does **not** test the stronger O3i action-intercept adversary.

## Adversary envelope

- undirected simple graph
- fixed five-node vertex set
- fixed target
- up to b one-for-one rewires per round
- edge count remains exactly 6
- graph remains connected
- lambda_t(s,t) >= lambda_min after every rewire
- zero edits are allowed
- additions must be genuine pre-edit nonedges
- adversary is otherwise minimax: every legal successor graph is enumerated

Sweep:

- b in {1,2}
- lambda_min in {1,2,3}
- k in {1,2,3,4}
- H = 6

No parameter is changed after seeing results.

## Controller power

The controller is intentionally strong:

- knows the target;
- sees the full current graph;
- centrally coordinates all crows;
- may randomize in principle, but because this is a finite perfect-information reachability game with deterministic transitions after action choices, the exact solver asks whether a pure action can force the winning set;
- agents may wait.

If this controller cannot force reach, weaker routing heuristics cannot claim a worst-case guarantee in the same finite model.

## Validation before K*

1. Static sanity: with b=0, one crow must force reach on K_{2,3} within 2 rounds.
2. Bounded-cut floor: exhaustive transient-cut scheduling must reproduce that b+1 crows on b+1 fixed edge-disjoint paths guarantee arrival and respect the sum-of-path-lengths upper bound.
3. Rewire invariants: every enumerated successor preserves edge count, connectedness, and lambda_min.
4. Temporal landmark: the temporal analyzer reproduces a compact known-class vertex-Menger violation (max temporal vertex-disjoint packing 1, minimum temporal vertex separator 2). This is a validation warning about temporal/static connectivity, not a direct edge-Menger theorem for our model.

## Decision rule

For each (b, lambda_min) cell:

- K* is the smallest k <= 4 that is exactly winnable within H=6.
- If no such k exists, report K* as censored (>4 for this horizon).

Interpretation is frozen:

- **Rewiring penalty:** if K* > b+1 in at least one resolved cell, bounded rewiring has separated from the fixed-footprint cut floor on this instance.
- **No separation:** if every resolved K* <= b+1, this toy instance gives no evidence that the exact rewiring variant needs more agents than the cut floor.
- **Censored:** K* > 4 at H=6 is not a universal impossibility theorem; it says only that the guarantee is outside the preregistered resource/horizon box.

No new algorithm, hyperparameter tuning, larger horizon, or new graph family is introduced to rescue either outcome.

## Prior-art guardrail

The result is not claimed as novel merely because it is exact. It sits next to:

- dynamic graph exploration thresholds;
- temporal connectivity / temporal Menger theory;
- network interdiction and robust routing;
- limited link-rewiring attacks on random walks.

A contribution claim requires a separate literature review showing that this exact resource threshold is not already implied by a known model.
