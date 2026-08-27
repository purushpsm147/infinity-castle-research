# Phase 1 targeted diagnostic

These are **two-seed mechanism checks**, not confirmatory evidence.

Configuration: 4 agents, reactive-cut adversary, budget b=2, horizon 30.

## 4 parallel corridors

Physarum and fixed electrical-flow routing produced identical outcomes in both seeds:

- seed A: success, work 20, mean effective support ~1.755
- seed B: success, work 48, mean effective support ~1.934

This is evidence **against** attributing the result to conductance adaptation in this toy graph. Fixed electrical geometry was sufficient.

## 5x5 grid

Both seeds:

- shortest-path replanning failed;
- random walk failed;
- current disjoint-path baseline failed;
- entropy-regularized replanning succeeded;
- fixed electrical-flow routing succeeded;
- generic reinforcement succeeded;
- Physarum succeeded.

This sharply weakens the naive claim "Physarum wins." The stronger hypothesis is that a family of policies with dispersed or less predictable traffic can evade an adversary designed around current shortest-path structure.

## Interpretation

The next experiment should test whether success is statistically associated with low top-b traffic mass / higher effective support **after controlling for progress toward the target**.

If fixed electrical or entropy-regularized routing matches Physarum across held-out regimes, kill the Physarum-specific claim and retain the broader adversarial routing result.
