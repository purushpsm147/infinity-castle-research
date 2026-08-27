from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from infinity_castle.adversaries import NoAdversary, ReactiveCutAdversary, TrafficAwareAdversary
from infinity_castle.analytics import trace_metrics
from infinity_castle.graphs import connected_erdos_renyi, grid_graph, ladder_graph
from infinity_castle.model import CastleConfig
from infinity_castle.policies import (
    AdaptiveConsensusNoMemoryPolicy,
    EdgeDisjointPathPolicy,
    EntropyRegularizedPolicy,
    PheromoneConsensusPolicy,
    PheromoneFixedContrarianPolicy,
    PheromonePureConsensusPolicy,
    ReplanShortestPathPolicy,
)
from infinity_castle.simulator import run_episode


POLICIES = {
    "replan": ReplanShortestPathPolicy,
    "edge_disjoint": EdgeDisjointPathPolicy,
    "entropy_replan": EntropyRegularizedPolicy,
    "adaptive_no_memory": AdaptiveConsensusNoMemoryPolicy,
    "pheromone_consensus": PheromonePureConsensusPolicy,
    "pheromone_fixed25": lambda: PheromoneFixedContrarianPolicy(0.25),
    "pheromone_adaptive": PheromoneConsensusPolicy,
}

ADVERSARIES = {
    "none": NoAdversary,
    "traffic_aware": TrafficAwareAdversary,
    "reactive_cut": ReactiveCutAdversary,
}


def graph_cases(seed: int):
    return {
        "grid6": grid_graph(6),
        "ladder12": ladder_graph(12),
        "er36": connected_erdos_renyi(36, 0.12, seed),
    }


def run(seeds: int = 30, horizon: int = 70, agents: int = 8) -> pd.DataFrame:
    rows = []
    for seed in range(seeds):
        for graph_name, (graph, source, target) in graph_cases(seed).items():
            for adversary_name, adversary_factory in ADVERSARIES.items():
                budgets = (0,) if adversary_name == "none" else (1, 2)
                for budget in budgets:
                    for policy_index, (policy_name, policy_factory) in enumerate(POLICIES.items()):
                        cfg = CastleConfig(
                            horizon=horizon,
                            agents=agents,
                            adversary_budget=budget,
                        )
                        result = run_episode(
                            graph,
                            source,
                            target,
                            policy_factory(),
                            adversary_factory(),
                            cfg,
                            seed=seed * 100003 + budget * 101 + policy_index * 17,
                            keep_trace=True,
                            separate_rngs=True,
                        )
                        metrics = trace_metrics(result.traces, attack_budget=max(1, budget))
                        rows.append(
                            {
                                "seed": seed,
                                "graph": graph_name,
                                "adversary": adversary_name,
                                "budget": budget,
                                "agents": agents,
                                "policy": policy_name,
                                "success": int(result.success),
                                "reach_time": result.reach_time,
                                "work": result.work,
                                **metrics,
                            }
                        )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["graph", "adversary", "budget", "agents", "policy"], dropna=False)
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


def _wins(candidate, baseline) -> bool:
    if candidate.p_reach >= baseline.p_reach + 0.10:
        return True
    if abs(candidate.p_reach - baseline.p_reach) <= 0.02:
        return candidate.mean_work <= 0.90 * baseline.mean_work
    return False


def gate(summary: pd.DataFrame) -> dict[str, int | bool]:
    hostile = summary[summary["adversary"] != "none"]
    memory_wins = 0
    contrarian_wins = 0
    joint_wins = 0
    cells = 0

    keys = ["graph", "adversary", "budget", "agents"]
    for _, cell in hostile.groupby(keys):
        by_policy = {row.policy: row for row in cell.itertuples()}
        needed = {"pheromone_adaptive", "adaptive_no_memory", "pheromone_consensus"}
        if not needed.issubset(by_policy):
            continue
        cells += 1
        memory = _wins(by_policy["pheromone_adaptive"], by_policy["adaptive_no_memory"])
        contra = _wins(by_policy["pheromone_adaptive"], by_policy["pheromone_consensus"])
        memory_wins += int(memory)
        contrarian_wins += int(contra)
        joint_wins += int(memory and contra)

    passed = memory_wins >= 2 and contrarian_wins >= 2 and joint_wins >= 1
    return {
        "cells": cells,
        "memory_wins": memory_wins,
        "contrarian_wins": contrarian_wins,
        "joint_wins": joint_wins,
        "passed": passed,
    }


def paired_deltas(df: pd.DataFrame, candidate: str, baseline: str) -> pd.DataFrame:
    sub = df[df["policy"].isin([candidate, baseline])].pivot(
        index=["seed", "graph", "adversary", "budget", "agents"],
        columns="policy",
        values=["success", "work"],
    )
    sub.columns = ["_".join(x) for x in sub.columns]
    sub = sub.reset_index()
    sub["success_delta"] = sub[f"success_{candidate}"] - sub[f"success_{baseline}"]
    sub["work_delta"] = sub[f"work_{candidate}"] - sub[f"work_{baseline}"]
    sub["comparison"] = f"{candidate}-vs-{baseline}"
    return sub


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--horizon", type=int, default=70)
    ap.add_argument("--agents", type=int, default=8)
    ap.add_argument("--out", type=Path, default=Path("results/pheromone_gate.csv"))
    args = ap.parse_args()

    df = run(args.seeds, args.horizon, args.agents)
    summary = summarize(df)
    paired = pd.concat(
        [
            paired_deltas(df, "pheromone_adaptive", "adaptive_no_memory"),
            paired_deltas(df, "pheromone_adaptive", "pheromone_consensus"),
            paired_deltas(df, "pheromone_adaptive", "edge_disjoint"),
        ],
        ignore_index=True,
    )
    verdict = gate(summary)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    summary.to_csv(args.out.with_name(args.out.stem + "_summary.csv"), index=False)
    paired.to_csv(args.out.with_name(args.out.stem + "_paired.csv"), index=False)

    print("=== SUMMARY ===")
    print(summary.to_string(index=False))
    print("\n=== GATE ===")
    print(verdict)
    print("\nRESULT:", "PASS - proceed to parameter tuning" if verdict["passed"] else "FAIL - do not tune")


if __name__ == "__main__":
    main()
