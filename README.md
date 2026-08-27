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
