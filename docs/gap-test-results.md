# Asymmetric gap-test result

Date: 2026-08-27

Workflow: 30 seeds, 4 agents, asymmetric corridor families, horizons of 45 rounds, with no adversary and reactive-cut budgets b in {1,2}.

Primary comparison: Physarum-inspired transient conductance adaptation vs fixed electrical-flow routing.

## Validation first

The corrected suite contains 13 passing tests, including:

- canonical equal-corridor symmetry preservation;
- canonical unequal-corridor shortest-path convergence;
- true edge-disjoint routing on a four-corridor graph;
- verification that the 5x5 corner-to-corner grid has edge connectivity 2.

## Paired Physarum vs electrical result

Across all nine graph/adversary/budget cells:

- mean success delta = 0.0;
- Physarum reachability wins = 0;
- electrical reachability wins = 0;
- all 30 paired seeds tied in every cell.

Work deltas (Physarum minus electrical):

| graph | adversary | b | mean work delta |
|---|---|---:|---:|
| u_3_4_6_9 | none | 0 | 0.0 |
| u_3_4_6_9 | reactive_cut | 1 | 0.0 |
| u_3_4_6_9 | reactive_cut | 2 | 0.0 |
| u_3_5_7_9 | none | 0 | 0.0 |
| u_3_5_7_9 | reactive_cut | 1 | +1.2 |
| u_3_5_7_9 | reactive_cut | 2 | +1.8667 |
| u_4_6_7_10 | none | 0 | 0.0 |
| u_4_6_7_10 | reactive_cut | 1 | +0.8 |
| u_4_6_7_10 | reactive_cut | 2 | +2.4 |

Positive means Physarum used more work.

## Strong baseline result

True edge-disjoint routing reached the target in 100% of runs for every asymmetric corridor cell tested and generally used less work than the adaptive policies under reactive cuts.

This does not prove edge-disjoint routing is globally optimal; these graph families were designed around parallel corridor structure. It does show that the earlier weak "disjoint" implementation was not an adequate conventional baseline.

## Conclusion

The preregistered Physarum-specific hypothesis fails on the tested asymmetric model.

We therefore close that line instead of replacing it with a route-entropy or top-b-mass novelty claim.

The artifact remains valuable for:
- reproducing the negative result;
- testing future ideas against strong controls;
- demonstrating how symmetry and weak baselines can create misleading early signals.
