from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from infinity_castle.exact_game import moving_gateway_castle
from infinity_castle.global_persistence import (
    PersistentRewireGame,
    c0_matches_base_successors,
    verify_global_persistence_clique_foothold,
)


def main() -> None:
    rows = []
    for n in (3, 4, 5, 6, 7):
        g, s, t = moving_gateway_castle(n, 1)
        c0_ok = c0_matches_base_successors(
            g,
            s,
            t,
            budget=1,
            lambda_min=1,
        )
        for tau in (1, 2, 3):
            cert = verify_global_persistence_clique_foothold(n, tau)
            rows.append({
                "n": n,
                "d": 1,
                "b": 1,
                "tau": tau,
                "predicted_k_star": 1,
                "horizon_bound": 3,
                "c0_matches_base": c0_ok,
                "first_successors_checked": cert.first_successors_checked,
                "relocated_gateway_cases": cert.relocated_gateway_cases,
                "second_successors_checked": cert.second_successors_checked,
                "certificate_verified": cert.certificate_verified,
            })

    g, s, t = moving_gateway_castle(4, 1)
    c0 = PersistentRewireGame(g, s, t, budget=1, lambda_min=1, tau=0)
    c1 = PersistentRewireGame(g, s, t, budget=1, lambda_min=1, tau=1)
    smoke = {
        "G_4_1_C0_k1_H2": c0.solve(agents=1, horizon=2).winnable,
        "G_4_1_C0_k3_H2": c0.solve(agents=3, horizon=2).winnable,
        "G_4_1_C1_k1_H2": c1.solve(agents=1, horizon=2).winnable,
        "G_4_1_C1_k1_H3": c1.solve(agents=1, horizon=3).winnable,
    }

    if any(not row["c0_matches_base"] for row in rows):
        raise SystemExit("C0/base semantic equivalence failed")
    if any(not row["certificate_verified"] for row in rows):
        raise SystemExit("Theorem C clique certificate failed")

    expected_smoke = {
        "G_4_1_C0_k1_H2": False,
        "G_4_1_C0_k3_H2": True,
        "G_4_1_C1_k1_H2": False,
        "G_4_1_C1_k1_H3": True,
    }
    if smoke != expected_smoke:
        raise SystemExit(f"exact smoke mismatch: {smoke!r}")

    out = Path("results")
    out.mkdir(exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "theorem_c_global_persistence.csv", index=False)

    payload = {
        "frozen_cases": rows,
        "exact_smoke": smoke,
        "verdict": "all frozen semantic certificates passed",
    }
    (out / "theorem_c_global_persistence.json").write_text(
        json.dumps(payload, indent=2)
    )

    print(df.to_string(index=False))
    print(json.dumps(smoke, indent=2))


if __name__ == "__main__":
    main()
