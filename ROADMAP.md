# Roadmap

## Phase 0 — instrument validation
- [x] bounded connected rewiring model
- [x] random / replan / disjoint / reinforcement / Physarum policies
- [x] oblivious / traffic-aware / reactive-cut adversaries
- [x] no-adversary shortest-path control
- [x] CI workflow

## Phase 1 — mechanism and baseline hardening
- [x] parallel-corridor analytic benchmark
- [x] route entropy / effective support / HHI / top-b mass
- [x] fixed electrical-flow control
- [x] entropy-regularized replanning control
- [x] analytic occupancy survival sanity checks
- [ ] robust min-cost / multipath baseline
- [ ] risk-sensitive replanner with attack history
- [ ] improve disjoint-path policy under changing topologies
- [ ] scale runtime and cache repeated linear solves

## Phase 2 — adversary taxonomy
- [x] no adversary
- [x] oblivious rewiring
- [x] traffic-aware post-position rewiring
- [x] reactive shortest-frontier attack
- [ ] public-history predictive adversary
- [ ] policy-agnostic centrality/min-cut adversary
- [ ] pre-edit timing model
- [ ] action-intercept timing model

## Phase 3 — confirm mechanism
- [ ] regress success against top-b traffic mass + progress
- [ ] conductance ablations
- [ ] match compute/memory budgets
- [ ] held-out graph families
- [ ] bootstrap confidence intervals

## Phase 4 — application transfer, only if mechanism survives
- [ ] contested RF / traffic-aware jamming
- [ ] P2P eclipse / peer-view manipulation
- [ ] censorship relay blocking
- [ ] moving-target-defense dual game
