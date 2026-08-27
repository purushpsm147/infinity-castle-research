from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from infinity_castle.exact_game import (
    ExactRewireGame,
    moving_gateway_castle,
    verify_moving_gateway_threshold,
)

CASES = [
    (4, 1, 1),
    (5, 1, 1),
    (5, 2, 2),
    (6, 1, 1),
    (6, 2, 2),
]


def main():
    out = Path("results/moving_gateway_theorem.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    all_pass = True

    for n, d, b in CASES:
        cert = verify_moving_gateway_threshold(n, d, budget=b)
        predicted = n - d
        passed = (
            cert.agents == predicted
            and cert.lower_invariant_verified
            and cert.upper_force_verified
        )
        all_pass = all_pass and passed
        rows.append({
            "n": n,
            "d": d,
            "budget": b,
            "predicted_k_star": predicted,
            "lower_k": predicted - 1,
            "lower_invariant_verified": cert.lower_invariant_verified,
            "upper_k": predicted,
            "upper_force_verified": cert.upper_force_verified,
            "lower_cases_checked": cert.lower_cases_checked,
            "lower_moves_checked": cert.lower_moves_checked,
            "upper_rewires_checked": cert.upper_rewires_checked,
            "passed": passed,
        })

    g, s, t = moving_gateway_castle(4, 1)
    exact = ExactRewireGame(g, s, t, budget=1, lambda_min=1)
    smoke_loss = not exact.solve(agents=2, horizon=8).winnable
    smoke_win = exact.solve(agents=3, horizon=2).winnable
    all_pass = all_pass and smoke_loss and smoke_win

    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)
    summary = {
        "candidate_theorem": "K*_infty(G_{n,d}) = n-d for b>=d under O3p moving-gateway rewiring",
        "tested_cases": len(CASES),
        "all_certificates_pass": bool(all_pass),
        "independent_smallest_case": {
            "n": 4,
            "d": 1,
            "b": 1,
            "k2_loses_through_H8": smoke_loss,
            "k3_wins_by_H2": smoke_win,
        },
        "novelty_status": "candidate contribution only; equivalence still needs literature audit",
    }
    out.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n")
    print(df.to_string(index=False))
    print(json.dumps(summary, indent=2))

    if not all_pass:
        raise SystemExit("Validation failed; stop and reconcile model/proof.")


if __name__ == "__main__":
    main()
