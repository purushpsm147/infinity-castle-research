# Roadmap

## Phase 0 — instrument validation
- [x] bounded connected rewiring model
- [x] baseline policies and adversaries
- [x] CI workflow
- [x] invariant tests

## Phase 1 — falsify the Physarum-specific claim
- [x] identify equal-corridor symmetry problem
- [x] validate canonical static Physarum on equal corridors
- [x] validate convergence on unequal [3,5,7] corridors
- [x] replace weak "disjoint" control with actual edge-disjoint routing
- [x] run asymmetric 30-seed paired Physarum-vs-electrical sweep
- [x] apply kill gate

### Verdict
Closed. No reachability advantage was observed; when work differed, transient Physarum was generally equal or worse than fixed electrical flow.

## Prior-art checkpoint
- [x] bounded link rewiring during target search/exploration exists in IEEE COMPSAC 2024
- [x] broader random-walk adversarial rewiring follow-up exists in COMPSAC 2025
- [x] robust/interdiction objectives are mature literature

## Future work policy

No Phase 2 is scheduled.

Before adding another algorithm or application:
1. state a precise question;
2. identify the nearest primary literature;
3. explain exactly what is not covered;
4. define a falsifiable experiment before implementation.

If that review does not expose a genuine gap, do not extend the project.


## Pheromone consensus branch — closed gate
- [x] add shared progress/failure/volatility memory
- [x] add consensus and fixed/adaptive contrarian variants
- [x] separate policy/adversary RNG streams
- [x] pair policies on identical adversary RNG streams
- [x] run frozen 30-seed gate
- [x] audit EXP3/EXP4/adversarial-MDP prior art
- [x] apply stop rule

### Verdict
Shared pheromone memory produced 0 preregistered wins over the matched no-memory adaptive control. Adaptive exploration/contrarian behavior helped pure consensus in some hostile cells, but the combined mechanism did not pass the gate.

No parameter optimization is scheduled. Any reopening must start with strong adversarial-learning baselines and a new preregistration.


## Feasibility frontier — exact bounded rewiring
- [x] retire the unproven Castle Trilemma
- [x] formalize the fixed-footprint b+1 reachability floor
- [x] freeze O3p one-for-one rewiring semantics
- [x] enforce lambda_min, connectivity, and fixed edge count
- [x] add exact backward-induction minimax solver
- [x] validate static, transient-cut, rewire-invariant, and temporal-Menger landmarks
- [x] preregister K*(b, lambda_min; H=6) before solving
- [x] run exact finite game in Actions
- [x] apply the preregistered stop rule

### Result

K*:
- b=1: 2 for lambda_min in {1,2,3}
- b=2: 3 for lambda_min in {1,2}, 2 for lambda_min=3

No cell had K* > b+1. The proposed rewiring penalty did not appear on the frozen instance.

No graph/horizon/timing expansion is scheduled to rescue the hypothesis. A future extension requires a fresh literature-grounded reason independent of this result.


## Moving-gateway theorem — validated
- [x] state exact candidate theorem K*_infty(G_{n,d})=n-d
- [x] prove lower relocation invariant for k<=n-d-1
- [x] prove upper two-round win for k=n-d
- [x] freeze five regression instances before execution
- [x] mechanically verify both sides at every threshold
- [x] independently smoke-test the smallest case with the generic exact solver
- [x] park the validation workflow after success

### Result

All five frozen regressions passed.

The theorem establishes that, under the stated O3p replacement semantics, instantaneous lambda_min and edit budget b alone do not yield an n-independent redundancy bound. At d=b the exact threshold is n-b.

### Publication status

Potential theorem contribution, not yet a novelty claim. Before paper drafting:
1. audit primary literature for an equivalent multi-agent replacement-game threshold;
2. position explicitly against dynamic-network relocation lower bounds, Gotoh-style exploration thresholds, Nemesis, interdiction, and temporal reachability;
3. investigate a persistence condition that restores a bounded redundancy guarantee.

Do not add another heuristic policy.
