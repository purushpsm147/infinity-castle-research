# Falsification protocol

## Research question

Does a Physarum-inspired **transient conductance adaptation** improve adversarial navigation over a fixed electrical-flow control on asymmetric graphs under the same information and resource budgets?

This is intentionally narrower than the earlier Phase 1 framing.

## Validation prerequisites

Before an adversarial result is interpretable:

1. canonical fixed-source Physarum must preserve symmetry on equal corridors;
2. canonical fixed-source Physarum must concentrate onto a unique shortest path on unequal corridors;
3. the conventional redundancy control must use actual edge-disjoint paths;
4. graph cut size / edge connectivity must be reported alongside k and b.

## Primary hypothesis

On at least one predeclared asymmetric graph family and bounded reactive-rewiring regime, adaptive conductance produces a reproducible Pareto improvement over fixed electrical routing in:
- reach probability, and
- work conditional on comparable reach probability.

The comparison is paired by seed.

## Controls

- shortest-path replanning;
- true edge-disjoint routing;
- generic reinforcement;
- fixed electrical-flow routing.

## Kill gate

Close the Physarum-specific line if, across the predeclared asymmetric sweep:
- Physarum does not improve reach probability over fixed electrical flow by a practically meaningful margin, or
- any apparent reach gain is paid for by a clearly dominated work frontier, or
- the effect does not survive held-out seeds / asymmetric graph variants.

Do **not** replace a null with a new claim about route entropy or top-b mass. Those quantities may explain behavior but belong to established robust-routing/interdiction territory.

## Evidence standard

The prior two-seed diagnostic is not evidence. Confirmatory reporting requires the frozen asymmetric sweep and held-out seeds.
