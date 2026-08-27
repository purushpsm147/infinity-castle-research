# Falsification protocol

## Research question

Given equal search-resource and information budgets, does local adaptive flow allocation produce a better held-out success/work frontier than conventional redundancy policies under bounded reactive topology rewiring?

## Claims separated in advance

### H1 — redundancy
Multiple agents outperform one agent in some bounded-rewiring regimes. Not expected to be novel by itself.

### H2 — dispersion / adaptive allocation
A policy that avoids concentrating attackable traffic can outperform deterministic shortest-path concentration under a reactive adversary.

### H3 — Physarum-specific adaptation
Adaptive Physarum conductances outperform both:
1. fixed electrical-flow routing with the same current-flow geometry, and
2. non-biological entropy/reinforcement controls,
under the same observation/resource class.

H3 is the only claim that supports a Physarum-specific mechanism story.

## Phase 1 mechanism test

Primary explanatory variables:
- effective traffic support exp(H);
- Herfindahl concentration;
- top-b traffic mass;
- target progress / hitting time;
- work.

The mechanism hypothesis survives only if lower adversarial coverability predicts reachability without merely reflecting aimless random spreading.

## Kill gates

- If Physarum ~= fixed electrical flow, kill the adaptive-conductance claim.
- If Physarum ~= entropy-regularized or generic reinforcement, kill the biological-specific claim.
- If dispersion helps only against the shortest-frontier adversary but disappears against policy-agnostic or predictive adversaries, classify the result as adversary-specific.
- If robust conventional multipath dominates the adaptive policies, keep the simulator as an educational result and stop the biological thread.
- Any confirmatory claim requires unseen graph/adversary seeds and frozen hyperparameters.
