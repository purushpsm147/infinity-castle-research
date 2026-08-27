# Moving-gateway theorem — validation result

Date: 2026-08-27

## Statement under validation

For the clique-core family G_{n,d} under O3p one-for-one rewiring with b>=d and instantaneous lambda(s,t)>=d:

    K*_infty(G_{n,d}) = n-d.

The proof has two parts:

- lower: for k<=n-d-1, an adversary can keep all d target gateways on unoccupied core vertices forever using at most d swaps per round;
- upper: with k=n-d, the controller occupies n-d distinct core vertices in round 1, leaving only d-1 free vertices, so any legal next graph with lambda(s,t)>=d must expose at least one occupied gateway; that crow reaches t in round 2.

## Mechanical regression results

GitHub Actions run: 33050050082

All repository tests passed: 40 passed.

All five frozen theorem regressions passed:

| n | d | b | predicted K* | lower moves exhaustively checked | legal upper rewires checked |
|---:|---:|---:|---:|---:|---:|
| 4 | 1 | 1 | 3 | 81 | 9 |
| 5 | 1 | 1 | 4 | 2,560 | 22 |
| 5 | 2 | 2 | 3 | 288 | 45 |
| 6 | 1 | 1 | 5 | 109,375 | 45 |
| 6 | 2 | 2 | 4 | 12,500 | 235 |

For every case:

- the inductive loss certificate at k=n-d-1 was verified;
- the exhaustive win certificate at k=n-d was verified.

Independent semantic smoke test on G_{4,1}:

- k=2 does not force reach through H=8 in the generic exact solver;
- k=3 forces reach by H=2.

## Interpretation

The code agrees with the two-sided proof semantics on all frozen cases.

This changes the status of the earlier K_{2,3} null without invalidating it. The old |E|=6 instance did not contain enough dense core structure for the moving-gateway family that realizes the linear threshold. The new result is a mechanism/proof result, not a post-hoc rescue of the earlier finite sweep.

When d=b,

    K*_infty = n-b

and therefore

    K*_infty - (b+1) = n-2b-1.

For fixed b, the separation grows without bound with n. Thus instantaneous lambda_min together with per-round edit budget b is insufficient, by itself, to upper-bound the sure-reachability redundancy requirement in this model.

## Novelty status

The theorem is now mathematically and mechanically validated **under the repository model**.

It is still only a **candidate publication contribution** until a dedicated literature audit excludes an equivalent theorem.

The novelty claim must remain narrow:

> exact multi-agent sure-reachability threshold under connectivity-preserving one-for-one post-move edge replacement, plus the resulting unbounded separation showing that snapshot edge connectivity alone does not bound required agent redundancy.

Do not claim novelty for adversarial graph reachability, moving-edge lower bounds, dynamic exploration, or the relocation trick itself.

## Next research question

Do not assume protecting target-incident edges restores b+1. The relocation mechanism may recurse into the approaches to fixed gateways.

The next paper-shaped question is to identify a temporal persistence/stability condition under which a bound independent of n is restored.
