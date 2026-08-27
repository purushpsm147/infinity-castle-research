from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from infinity_castle.adversaries import NoAdversary, ReactiveCutAdversary
from infinity_castle.analytics import trace_metrics
from infinity_castle.graphs import unequal_corridors
from infinity_castle.model import CastleConfig
from infinity_castle.policies import (
    EdgeDisjointPathPolicy,
    ElectricalFlowPolicy,
    GenericReinforcementPolicy,
    PhysarumPolicy,
    ReplanShortestPathPolicy,
)
from infinity_castle.simulator import run_episode


POLICIES = {
    "replan": ReplanShortestPathPolicy,
    "edge_disjoint": EdgeDisjointPathPolicy,
    "reinforcement": GenericReinforcementPolicy,
    "electrical": ElectricalFlowPolicy,
    "physarum": PhysarumPolicy,
}


def graph_cases():
    return {
        "u_3_5_7_9": unequal_corridors([3, 5, 7, 9])[:3],
        "u_3_4_6_9": unequal_corridors([3, 4, 6, 9])[:3],
        "u_4_6_7_10": unequal_corridors([4, 6, 7, 10])[:3],
    }


def run(seeds: int = 30, horizon: int = 45) -> pd.DataFrame:
    rows = []
    for seed in range(seeds):
        for gname, (g, source, target) in graph_cases().items():
            for adversary_name, adversary_factory, budgets in (
                ("none", NoAdversary, (0,)),
                ("reactive_cut", ReactiveCutAdversary, (1, 2)),
            ):
                for b in budgets:
                    for pname, pfactory in POLICIES.items():
                        policy = pfactory()
                        result = run_episode(
                            g,
                            source,
                            target,
                            policy,
                            adversary_factory(),
                            CastleConfig(horizon=horizon, agents=4, adversary_budget=b),
                            seed=seed * 100003 + b * 101,
                            keep_trace=True,
                        )
                        metrics = trace_metrics(result.traces, attack_budget=max(1, b))
                        rows.append({
                            "seed": seed,
                            "graph": gname,
                            "adversary": adversary_name,
                            "budget": b,
                            "policy": pname,
                            "success": int(result.success),
                            "reach_time": result.reach_time,
                            "work": result.work,
                            **metrics,
                        })
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["graph", "adversary", "budget", "policy"], dropna=False)
        .agg(
            p_reach=("success", "mean"),
            mean_reach_time=("reach_time", "mean"),
            mean_work=("work", "mean"),
            mean_support=("mean_effective_support", "mean"),
            mean_top_b_mass=("mean_top_b_mass", "mean"),
            runs=("success", "size"),
        )
        .reset_index()
    )


def paired_physarum_minus_electrical(df: pd.DataFrame) -> pd.DataFrame:
    paired = df[df["policy"].isin(["physarum", "electrical"])].pivot(
        index=["seed", "graph", "adversary", "budget"],
        columns="policy",
        values=["success", "work"],
    )
    paired.columns = ["_".join(x) for x in paired.columns]
    paired = paired.reset_index()
    paired["success_delta"] = paired["success_physarum"] - paired["success_electrical"]
    paired["work_delta"] = paired["work_physarum"] - paired["work_electrical"]
    return paired


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--horizon", type=int, default=45)
    ap.add_argument("--out", type=Path, default=Path("results/gap_test.csv"))
    args = ap.parse_args()

    df = run(args.seeds, args.horizon)
    summary = summarize(df)
    paired = paired_physarum_minus_electrical(df)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    summary.to_csv(args.out.with_name(args.out.stem + "_summary.csv"), index=False)
    paired.to_csv(args.out.with_name(args.out.stem + "_paired.csv"), index=False)

    print("=== SUMMARY ===")
    print(summary.to_string(index=False))
    print("\n=== PAIRED PHYSARUM - ELECTRICAL ===")
    print(
        paired.groupby(["graph", "adversary", "budget"])
        .agg(
            mean_success_delta=("success_delta", "mean"),
            physarum_wins=("success_delta", lambda x: int((x > 0).sum())),
            electrical_wins=("success_delta", lambda x: int((x < 0).sum())),
            ties=("success_delta", lambda x: int((x == 0).sum())),
            mean_work_delta=("work_delta", "mean"),
            runs=("success_delta", "size"),
        )
        .reset_index()
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
