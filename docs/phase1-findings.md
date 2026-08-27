# Phase 1 findings — corrected status

The original two-seed table was a **diagnostic only** and must not be treated as evidence.

## Retracted interpretation

The statement that equality between Physarum and fixed electrical flow on equal corridors was evidence that conductance adaptation was inert is retracted. Equal parallel corridors are a symmetry-dominated test for the canonical fixed-source dynamics.

## Validation added

The branch now tests two known properties before evaluating adversarial navigation:

1. Equal [4,4,4] corridors with uniform conductance preserve symmetry under canonical static Physarum dynamics.
2. Unequal [3,5,7] corridors converge strongly to the unique shortest corridor.

This reproduces the known static shortest-path behavior.

## Disjoint baseline audit

The old "disjoint" implementation was not truly edge-disjoint and has been superseded by EdgeDisjointPathPolicy.

The earlier 5x5 grid cell (k=4, b=2) is also structurally hostile to disjoint routing: corner-to-corner edge connectivity is only 2. Thus an adversary budget of 2 matches the maximum number of edge-disjoint escape routes at the source.

## What remains worth testing

Only the asymmetric adversarial comparison is treated as a possible research gap:

- fixed electrical-flow routing;
- transient Physarum conductance adaptation;
- true edge-disjoint routing;
- shortest replanning;
- generic reinforcement.

Primary comparison: **Physarum vs fixed electrical, paired by seed.**

If the adaptive policy does not produce a reproducible held-out improvement on asymmetric graphs, the Physarum-specific hypothesis is closed.

Top-b mass / entropy remain diagnostics, not novelty claims.
