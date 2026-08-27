# Infinity Castle Research

A falsification-first experimental harness for **navigation/search on graphs whose topology is rewritten online by a bounded, reactive adversary**.

The project started from a simple question inspired by the *Infinity Castle* thought experiment:

> Given the same search/redundancy budget, can local adaptive policies allocate that redundancy more efficiently than conventional strategies when an adversary observes the search and rewires the topology in response?

## Current verdict

The **Physarum-specific hypothesis is closed for the tested model**.

After correcting the original equal-corridor symmetry flaw, validating canonical Physarum shortest-path convergence on unequal corridors, and replacing the weak "disjoint" control with a true edge-disjoint-path baseline, a 30-seed asymmetric sweep found:

- no reach-probability advantage for transient Physarum adaptation over fixed electrical-flow routing in any paired cell;
- 0 Physarum wins and 0 electrical wins on reachability across all paired cells (all reach outcomes tied);
- where work differed, Physarum was generally equal or worse;
- true edge-disjoint routing was often the strongest baseline on the corridor families.

See [docs/gap-test-results.md](docs/gap-test-results.md).

This repository remains useful as a benchmark/negative-result artifact, but it does **not** claim a novel Physarum algorithm or a novel bounded-rewiring model.

## Game model

At round t:

1. Agents observe the current graph G_t.
2. A policy selects one legal move per agent.
3. Moves are executed; traffic is recorded.
4. If any agent reaches the target, the run succeeds.
5. The adversary observes realized traffic/positions and performs at most b connected rewires to construct G_{t+1}.

A rewire removes one edge and inserts one non-edge while preserving simplicity, connectivity, and edge count.

## Policies

- random walk
- shortest-path replanning
- legacy diverse-first-hop baseline
- true edge-disjoint-path routing
- generic reinforcement
- entropy-regularized replanning
- fixed electrical-flow routing
- Physarum-inspired transient conductance adaptation

The canonical fixed-source/fixed-sink Physarum helper is kept separately for validation.

## Important prior art

Limited link rewiring during target-node search and graph exploration is already studied in the random-walk literature (IEEE COMPSAC 2024, with a broader 2025 follow-up). Network interdiction / robust routing is also a mature field. Accordingly:

- top-b traffic mass and entropy are diagnostics, not novelty claims;
- the rewiring model itself is not presented as new;
- any future research extension requires a fresh literature review before implementation.

## Reproduce

```bash
python -m pip install -e .[dev]
pytest
python experiments/run_gap_test.py --seeds 30 --horizon 45 --out results/gap_test.csv
```

## Pheromone / consensus experiment

A second preregistered experiment tested shared evaporating pheromone memory plus consensus/contrarian population splitting.

The first frozen gate **failed**:
- 12 hostile cells;
- shared-memory wins over the matched no-memory control: 0;
- adaptive-contrarian wins over pure consensus: 5;
- cells showing both benefits: 0.

The current interpretation is that avoiding consensus collapse helped, while the added pheromone memory did not justify parameter tuning. See [docs/pheromone-result.md](docs/pheromone-result.md).

The broad mechanism also overlaps heavily with adversarial bandits/expert advice and adversarial MDPs; see [docs/prior-art-online-learning.md](docs/prior-art-online-learning.md).

## Research discipline

A null is allowed to stay null. Neither the Physarum line nor the current pheromone-memory line is open for parameter tuning. Any new phase must first identify the nearest primary literature, state a precise uncovered question, and preregister a held-out evaluation.


## Feasibility frontier / exact rewiring threshold

The project then stopped inventing new policies and tested a narrow resource-threshold question with exact minimax backward induction.

For a five-node K_{2,3} castle under O3p one-for-one rewiring, H=6:

| b | lambda_min=1 | lambda_min=2 | lambda_min=3 |
|---:|---:|---:|---:|
| 1 | K*=2 | K*=2 | K*=2 |
| 2 | K*=3 | K*=3 | K*=2 |

The preregistered signal K* > b+1 never occurred. The exact finite experiment therefore found **no rewiring penalty above the bounded-cut sufficiency floor**. In the strongest-connectivity cell, two agents sufficed even for b=2, emphasizing that b+1 is sufficient in the cut model, not a universal lower bound.

See [docs/exact-rewire-results.md](docs/exact-rewire-results.md) and [docs/exact-rewire-preregistration.md](docs/exact-rewire-preregistration.md).

The earlier known-arsenal screen likewise found 0/81 provisionally fortified hostile cells. No novel threshold or new navigation algorithm is currently claimed.


## Moving-gateway threshold theorem

A later theorem-first phase identified a graph family that the earlier six-edge exact experiment structurally could not realize.

For the clique-core family G_{n,d} under O3p one-for-one rewiring, with b>=d and every snapshot constrained by lambda(s,t)>=d, the proved threshold is

[
K^*_{\infty}(G_{n,d}) = n-d.
]

When d=b,

[
K^*_{\infty}-(b+1)=n-2b-1,
]

so the gap above the fixed-footprint cut sufficiency value grows unboundedly with n.

This means **snapshot connectivity and per-round edit budget alone do not bound the number of persistent agents needed for sure reachability** in this model.

Five frozen semantics regressions all passed in GitHub Actions, including exhaustive verification of 109,375 controller moves for the (n,d,b)=(6,1,1) lower certificate. The smallest case independently agrees with the generic exact solver.

See [docs/moving-gateway-theorem.md](docs/moving-gateway-theorem.md) and [docs/moving-gateway-results.md](docs/moving-gateway-results.md).

Novelty status remains cautious: the theorem is validated under the model, but an equivalent-result literature audit is still required before a publication claim.
