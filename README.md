# Infinity Castle Research

A falsification-first experimental harness for **navigation/search on graphs whose topology is rewritten online by a bounded, reactive adversary**.

The project started from a simple question inspired by the *Infinity Castle* thought experiment:

> Given the same search/redundancy budget, can local adaptive policies allocate that redundancy more efficiently than conventional strategies when an adversary observes the search and rewires the topology in response?

This repository does **not** assume that Physarum/slime-mold dynamics are superior. The biological angle survives only if it beats both strong conventional baselines and a mechanism-matched generic reinforcement control.

## v0 game model

At round `t`:

1. Agents observe the current graph `G_t`.
2. A policy selects one legal move per agent.
3. Moves are executed; traffic on each traversed edge is recorded.
4. If any agent reaches the target, the run succeeds.
5. The adversary observes realized traffic/positions and performs at most `b` **rewires** to construct `G_{t+1}`.

A rewire removes one edge and inserts one non-edge. v0 keeps the graph simple, connected, and edge-count preserving.

This is intentionally **not** the same parameter as the fixed-footprint / missing-edge bounds used in much temporal-graph exploration literature.

## Policies in v0

- `random`: random legal neighbor.
- `replan`: shortest-path replanning on the current graph.
- `disjoint`: spreads agents over distinct current shortest routes when available.
- `reinforcement`: simple non-biological edge reinforcement + decay.
- `physarum`: conductance dynamics driven by electrical flow from current agent mass to the target.

## Adversaries in v0

- `none`: no topology changes.
- `oblivious`: random connected rewiring, independent of current traffic.
- `traffic_aware`: preferentially removes highly used edges and chooses replacement edges that avoid gifting obvious shortcuts.
- `reactive_cut`: position-aware adversary that attacks edges on the agents’ current shortest-path frontier; stronger than traffic-aware but still does not inspect policy internals or future random bits.

## Primary measurements

For a fixed horizon `H`:

- `P_reach`: empirical probability that at least one agent reaches the target.
- `T_reach`: rounds to first success.
- `W`: total traversals performed by all agents.
- `K_max`: peak number of active agents.

The research target is a **Pareto frontier**, not one cherry-picked scalar.

## Falsification gates

The biological hypothesis is *not* supported merely because Physarum beats random walk.

It must clear, on held-out instances/seeds:

1. random walk,
2. shortest-path replanning,
3. disjoint-path redundancy,
4. generic reinforcement with the same observation and memory class.

If generic reinforcement reproduces the Physarum frontier, the Physarum-specific hypothesis is dead and the result is instead about adaptive reinforcement.

See [`docs/preregistration.md`](docs/preregistration.md).

## Quick start

```bash
python -m pip install -e .[dev]
pytest
python experiments/run_sweep.py --seeds 30 --horizon 80 --out results/smoke.csv
```

## Status

`v0.1` is an instrument-validation stage. Phase 1 hardens baselines, adds route concentration/entropy metrics, and tests analytic sanity checks against layered/parallel-path graphs before any application claim.
