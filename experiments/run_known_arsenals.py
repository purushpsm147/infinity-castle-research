"""Phase 4: attack the castle with mature algorithmic arsenals.

No bespoke candidate is privileged.  This experiment compares established ideas:
EXP3-style adversarial bandits, security-game/minimax dispersion, a robust-MDP
surrogate, shortest-path replanning, edge-disjoint routing and entropy routing.

Primary question: after importing these baselines, which castle regimes remain
hard?  A 'fortified' cell is one where every policy has P(reach) < 0.80.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from infinity_castle.adversaries import NoAdversary, ObliviousChurnAdversary, ReactiveCutAdversary, TrafficAwareAdversary
from infinity_castle.analytics import trace_metrics
from infinity_castle.graphs import connected_erdos_renyi, grid_graph, ladder_graph
from infinity_castle.known_arsenals import EXP3MinimaxHybridPolicy, EXP3RoutingPolicy, MinimaxTrafficPolicy, RobustMDPPolicy
from infinity_castle.model import CastleConfig
from infinity_castle.policies import EdgeDisjointPathPolicy, EntropyRegularizedPolicy, RandomWalkPolicy, ReplanShortestPathPolicy
from infinity_castle.simulator import run_episode

POLICIES = {
    "random": RandomWalkPolicy,
    "replan": ReplanShortestPathPolicy,
    "edge_disjoint": EdgeDisjointPathPolicy,
    "entropy": EntropyRegularizedPolicy,
    "exp3": EXP3RoutingPolicy,
    "minimax_traffic": MinimaxTrafficPolicy,
    "robust_mdp_surrogate": RobustMDPPolicy,
    "exp3_minimax": EXP3MinimaxHybridPolicy,
}
ADVERSARIES = {
    "none": NoAdversary,
    "oblivious": ObliviousChurnAdversary,
    "traffic_aware": TrafficAwareAdversary,
    "reactive_cut": ReactiveCutAdversary,
}


def graph_cases(seed):
    return {
        "grid6": grid_graph(6),
        "ladder12": ladder_graph(12),
        "er36": connected_erdos_renyi(36, 0.12, seed),
    }


def run(seeds=50, horizon=70, agents=(2, 4, 8)):
    rows = []
    for seed in range(seeds):
        for gi, (gname, (graph, source, target)) in enumerate(graph_cases(seed).items()):
            for ai, (aname, afactory) in enumerate(ADVERSARIES.items()):
                budgets = (0,) if aname == "none" else (1, 2, 3)
                for budget in budgets:
                    for k in agents:
                        cell_seed = seed*100003 + gi*1009 + ai*131 + budget*17 + k*7919
                        for pname, pfactory in POLICIES.items():
                            result = run_episode(
                                graph, source, target, pfactory(), afactory(),
                                CastleConfig(horizon=horizon, agents=k, adversary_budget=budget),
                                seed=cell_seed, keep_trace=True, separate_rngs=True,
                            )
                            m = trace_metrics(result.traces, attack_budget=budget)
                            rows.append({
                                "seed": seed, "graph": gname, "adversary": aname,
                                "budget": budget, "agents": k, "policy": pname,
                                "success": int(result.success), "reach_time": result.reach_time,
                                "work": result.work, **m,
                            })
    return pd.DataFrame(rows)


def summarize(df):
    return df.groupby(["graph","adversary","budget","agents","policy"], dropna=False).agg(
        p_reach=("success","mean"), mean_reach_time=("reach_time","mean"),
        mean_work=("work","mean"), mean_support=("mean_effective_support","mean"),
        mean_top_b_mass=("mean_top_b_mass","mean"), runs=("success","size"),
    ).reset_index()


def fortress_map(summary, threshold=0.80):
    hostile = summary[summary.adversary != "none"]
    keys = ["graph","adversary","budget","agents"]
    rows = []
    for key, cell in hostile.groupby(keys):
        best = cell.sort_values(["p_reach","mean_work"], ascending=[False, True]).iloc[0]
        rows.append(dict(zip(keys, key)) | {
            "best_policy": best.policy, "best_p_reach": best.p_reach,
            "best_mean_work": best.mean_work,
            "fortified": bool(best.p_reach < threshold),
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--horizon", type=int, default=70)
    ap.add_argument("--agents", type=int, nargs="+", default=[2,4,8])
    ap.add_argument("--threshold", type=float, default=0.80)
    ap.add_argument("--out", type=Path, default=Path("results/known_arsenals.csv"))
    args = ap.parse_args()
    df = run(args.seeds, args.horizon, tuple(args.agents))
    summary = summarize(df)
    fortress = fortress_map(summary, args.threshold)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    summary.to_csv(args.out.with_name(args.out.stem + "_summary.csv"), index=False)
    fortress.to_csv(args.out.with_name(args.out.stem + "_fortress.csv"), index=False)
    print("=== FORTRESS MAP ===")
    print(fortress.to_string(index=False))
    print("\nFortified cells:", int(fortress.fortified.sum()), "/", len(fortress))

if __name__ == "__main__":
    main()
