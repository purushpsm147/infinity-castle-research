# Critique audit: what changed and what did not

This note records corrections made after reviewing the first Phase 1 diagnostic.

## 1. Equal-corridor Physarum ablation

**Genuine gap:** yes.

For canonical fixed-source/fixed-sink Physarum dynamics with uniform initial conductances, equal-length parallel corridors are symmetric. Equal flow produces equal conductance updates, so the symmetry is preserved. Exact equality against fixed electrical flow on that benchmark is therefore not informative about whether adaptation matters.

The repository now contains:
- a canonical static Physarum step;
- a symmetry unit test on [4,4,4] corridors;
- a convergence test on unequal [3,5,7] corridors.

The unequal test verifies that the implementation reproduces the established shortest-path concentration behavior before the moving-agent variant is trusted.

Reference: Bonifaci, Mehlhorn, Varma, "Physarum Can Compute Shortest Paths", J. Theoretical Biology 309 (2012), DOI 10.1016/j.jtbi.2012.06.017.

### Important model distinction

The navigation policy in the adversarial simulator is not exactly the canonical theorem setting. Its injection points move with the agents, the graph may be rewired, and the episode stops on first arrival. Therefore the static convergence theorem is a validation target for the conductance mechanism, not a theorem about the full navigation game.

For clarity, claims in this repo should call it a **Physarum-inspired transient conductance policy** unless discussing the canonical static helper.

## 2. Disjoint-path failure

**Implementation gap:** yes. **Interpretation that the grid result disproves dispersion:** no.

The old baseline only selected distinct first hops from shortest-simple paths; it did not guarantee edge-disjoint paths. A new EdgeDisjointPathPolicy uses actual edge-disjoint paths.

However, the 5x5 corner-to-corner grid has source-target edge connectivity 2. Under the diagnostic k=4, b=2 setting, at most two edge-disjoint routes can leave the corner, so an attacker with budget 2 already matches that cut size. Failure of a true disjoint-path policy is therefore not surprising in that cell.

## 3. Top-b traffic mass / robust routing pivot

**Novelty gap:** no.

Top-b traffic mass remains useful as an explanatory metric, but optimizing progress against bounded interdiction belongs to mature network-interdiction / robust-routing / Stackelberg-security territory. The project will not claim novelty for a C_b-penalized routing objective.

A recent survey: Ausiello et al., "Interdiction in network maximum flow and related problems: A survey", Computer Science Review 60 (2026), DOI 10.1016/j.cosrev.2025.100867.

## 4. Surviving research question

The narrow unresolved test is:

> On asymmetric graphs, under adaptive topology rewiring, does transient Physarum-style conductance adaptation improve the success/work frontier over fixed electrical-flow routing under matched information and resources?

The asymmetric gap test pairs Physarum and fixed-electrical outcomes by seed. If no reproducible advantage appears, the Physarum-specific line should be closed rather than replaced by another nearby novelty claim.
