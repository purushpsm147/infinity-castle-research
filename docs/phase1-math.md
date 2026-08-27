# Phase 1 mathematical sanity model

The first useful correction to the informal ratio `rho = k/b` is that **agents are not the same thing as independently threatened routes**.

Consider `m` equal, internally edge-disjoint corridors. Let `k` agents independently choose a corridor uniformly. If `R` is the number of distinct occupied corridors, then

```
E[R] = m (1 - (1 - 1/m)^k).
```

The number of agents can grow without bound while useful route support saturates at `m`.

For a post-choice attacker able to neutralize `b` whole route frontiers, the one-step survival event is `R > b`. Exactly,

```
P(R=r) = (m)_r S(k,r) / m^k,
P_survive = sum_{r=b+1}^{min(k,m)} P(R=r),
```

where `S(k,r)` is a Stirling number of the second kind.

Wolfram-checked examples:

| m | k | b | P(R>b) |
|---:|---:|---:|---:|
| 4 | 2 | 1 | 0.75 |
| 4 | 4 | 2 | 0.65625 |
| 4 | 8 | 2 | 0.9766845703 |
| 8 | 4 | 2 | 0.90234375 |
| 8 | 8 | 2 | 0.9995756149 |

This is not a theorem for arbitrary rewired graphs. It is an analytic **sanity benchmark**. It predicts that the useful control variable should involve route support / cut diversity, not raw `k/b`.

## Mechanism metrics

For realized per-round traffic shares `p_e`, Phase 1 records:

- Shannon entropy: `H = -sum p_e log p_e`
- effective support: `exp(H)`
- Herfindahl concentration: `sum p_e^2`
- top-b traffic mass: sum of the `b` largest shares.

The last metric is directly adversarial: if an attacker can hit `b` edges after observing traffic, high top-b mass means a larger fraction of the policy's realized activity is coverable.

## Current hypothesis

The early result may be better explained by:

> success under reactive cuts increases when the policy keeps attackable traffic mass diffuse while still making directional progress.

Physarum is only one possible implementation. Fixed electrical flow and entropy-regularized replanning are explicit controls for this claim.
