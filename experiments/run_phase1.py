from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from infinity_castle.adversaries import NoAdversary, ReactiveCutAdversary, TrafficAwareAdversary
from infinity_castle.analytics import trace_metrics
from infinity_castle.graphs import grid_graph, ladder_graph, parallel_corridors
from infinity_castle.model import CastleConfig
from infinity_castle.policies import (
    EdgeDisjointPathPolicy,
    ElectricalFlowPolicy,
    EntropyRegularizedPolicy,
    GenericReinforcementPolicy,
    PhysarumPolicy,
    RandomWalkPolicy,
    ReplanShortestPathPolicy,
)
from infinity_castle.simulator import run_episode

POLICIES = {
    "random": RandomWalkPolicy,
    "replan": ReplanShortestPathPolicy,
    "edge_disjoint": EdgeDisjointPathPolicy,
    "entropy_replan": EntropyRegularizedPolicy,
    "electrical": ElectricalFlowPolicy,
    "reinforcement": GenericReinforcementPolicy,
    "physarum": PhysarumPolicy,
}

ADVERSARIES = {
    "none": NoAdversary,
    "traffic_aware": TrafficAwareAdversary,
    "reactive_cut": ReactiveCutAdversary,
}


def graphs():
    return {
        "grid6": grid_graph(6),
        "ladder12": ladder_graph(12),
        "corridors4x6": parallel_corridors(4, 6),
        "corridors8x6": parallel_corridors(8, 6),
    }


def run(seeds: int, horizon: int):
    rows = []
    for seed in range(seeds):
        for gname, (g, s, t) in graphs().items():
            for aname, afactory in ADVERSARIES.items():
                for k in (2, 4, 8):
                    budgets = (0,) if aname == "none" else (1, 2)
                    for b in budgets:
                        for pname, pfactory in POLICIES.items():
                            cfg = CastleConfig(horizon=horizon, agents=k, adversary_budget=b)
                            r = run_episode(
                                g, s, t, pfactory(), afactory(), cfg,
                                seed=seed * 100003 + k * 101 + b * 17,
                                keep_trace=True,
                            )
                            m = trace_metrics(r.traces, attack_budget=max(1, b))
                            rows.append({
                                "seed": seed, "graph": gname, "policy": pname,
                                "adversary": aname, "agents": k, "budget": b,
                                "success": int(r.success), "reach_time": r.reach_time,
                                "work": r.work, **m,
                            })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--horizon", type=int, default=60)
    ap.add_argument("--out", type=Path, default=Path("results/phase1.csv"))
    args = ap.parse_args()
    df = run(args.seeds, args.horizon)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    summary = df.groupby(["graph", "policy", "adversary", "agents", "budget"], dropna=False).agg(
        p_reach=("success", "mean"),
        mean_work=("work", "mean"),
        mean_reach_time=("reach_time", "mean"),
        mean_support=("mean_effective_support", "mean"),
        mean_hhi=("mean_hhi", "mean"),
        mean_top_b_mass=("mean_top_b_mass", "mean"),
        runs=("success", "size"),
    ).reset_index()
    summary.to_csv(args.out.with_name(args.out.stem + "_summary.csv"), index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
