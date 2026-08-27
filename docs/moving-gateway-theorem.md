# Moving-gateway threshold theorem — validation note

## Candidate theorem

Let G_{n,d} have n vertices. The n-1 non-target vertices form a clique C. The target t is adjacent to exactly d vertices of C. The source s is a non-neighbor of t. Assume

- 1 <= d <= n-2;
- k persistent, centrally coordinated agents start at s;
- O3p timing: agents move, success is checked, then the adversary edits;
- the adversary may perform at most b one-for-one edge replacements per round;
- b >= d;
- every resulting graph is simple and connected, preserves edge count, and satisfies lambda(s,t) >= d.

Then the candidate exact threshold is

    K*_infty(G_{n,d}) = n-d.

The upper strategy wins by round 2. The lower adversary invariant prevents arrival forever for every k <= n-d-1.

## Lower certificate

Suppose k <= n-d-1. At the end of every agent move, at most k core vertices are occupied, so at least

    (n-1)-k >= d

core vertices are free.

The adversary selects d free core vertices U as the next target neighborhood. Starting from the previous d-element target neighborhood S, replacing edges t-v for v in S\U with t-w for w in U\S uses at most d <= b swaps.

The clique core remains unchanged. Hence deg(t)=d and there are d edge-disjoint s-t paths: one through each gateway (with the direct s-t edge used if s itself is a gateway). Therefore lambda(s,t)=d.

No agent begins the next round adjacent to t, restoring the invariant indefinitely.

## Upper certificate

Set k=n-d. In the first round the controller occupies n-d distinct core vertices (one agent may wait at s; the others move within the clique).

Only d-1 core vertices remain unoccupied. Any legal adversary successor must satisfy

    lambda(s,t) >= d,

hence deg(t) >= d. Since there are only d-1 unoccupied core vertices, at least one target neighbor is occupied. On the next round that agent moves to t before another O3p edit occurs.

Thus K*_infty <= n-d, matching the lower bound.

## Corollary at d=b

When d=b,

    K*_infty = n-b

and the gap above the fixed-footprint cut sufficiency value b+1 is

    n-2b-1.

For fixed b this gap is unbounded as n grows. Therefore no universal sure-reachability agent bound depending only on b and the instantaneous lambda_min can hold for this model.

## Frozen mechanical validation

Exactly five cases are used as semantics regressions:

| n | d | b | predicted K* |
|---:|---:|---:|---:|
| 4 | 1 | 1 | 3 |
| 5 | 1 | 1 | 4 |
| 5 | 2 | 2 | 3 |
| 6 | 1 | 1 | 5 |
| 6 | 2 | 2 | 4 |

For every case the harness must verify both:

1. loss certificate at k=n-d-1;
2. win certificate at k=n-d.

The smallest case is also checked independently with the generic exact finite-game solver.

If any case fails, the theorem/model semantics must be reconciled before any further work.

## Novelty position

Do not claim novelty merely because the theorem is exact.

Nearest neighboring ideas include:

- adversarial dynamic-network lower bounds that relocate missing/usable edges;
- multi-agent exploration thresholds in evolving graphs;
- post-move adversarial reachability games such as Nemesis (single agent, cumulative deletion, no connectivity floor);
- network interdiction and temporal-graph reachability.

The candidate contribution is narrower:

> an exact multi-agent sure-reachability threshold under connectivity-preserving one-for-one replacement with a fixed instantaneous edge-connectivity floor, together with an unbounded separation showing snapshot connectivity alone does not bound required agent redundancy.

A publication claim requires a dedicated primary-literature audit for an equivalent theorem.

## Next question, only after validation

Target-edge protection is not assumed to restore the b+1 threshold. The relocation mechanism may recurse into approaches to stable gateways.

The paper-shaped follow-up is to identify a persistence condition (for example gateway/path stability over a time window) that restores a bounded redundancy guarantee. No such theorem is claimed here.
