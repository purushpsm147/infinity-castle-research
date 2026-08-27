# Theorem B — validation result

Date: 2026-08-27

## Frozen theorem

In the synchronous gateway-dwell model,

    K*_infty = rho_tau(F, A_d(F,s)),

where:

- F is a fixed connected core graph;
- A_d(F,s) is the family of d-gateway sets whose augmentation preserves lambda(s,t)>=d;
- gateways persist for exactly tau+1 agent moves;
- epochs are synchronized and observable;
- full gateway relocation is atomic and allowed only at epoch boundaries;
- b>=d;
- agents may wait and co-locate.

Theorem B uses a weaker adversary than Theorem A because the core F is fixed.

## CI validation

GitHub Actions run: 33059383800

Repository test suite:

    70 passed

Frozen theorem cases:

    20 / 20 passed

Each case checked both:

- lower side: k=rho_tau-1 has an admissible gateway set farther than tau;
- upper side: a rho_tau-vertex witness lies within distance tau of every admissible gateway set.

## Frozen results

| case | d | tau | predicted K* | computed rho | lower verified | upper verified |
|---|---:|---:|---:|---:|:---:|:---:|
| clique_4 | 1 | 0 | 4 | 4 | yes | yes |
| clique_5 | 2 | 0 | 4 | 4 | yes | yes |
| clique_6 | 3 | 0 | 4 | 4 | yes | yes |
| clique_6 | 1 | 1 | 1 | 1 | yes | yes |
| clique_7 | 3 | 1 | 1 | 1 | yes | yes |
| path_5 | 1 | 1 | 2 | 2 | yes | yes |
| path_8 | 1 | 2 | 2 | 2 | yes | yes |
| path_10 | 1 | 1 | 4 | 4 | yes | yes |
| path_12 | 1 | 2 | 3 | 3 | yes | yes |
| cycle_6_d1 | 1 | 1 | 2 | 2 | yes | yes |
| cycle_9_d1 | 1 | 1 | 3 | 3 | yes | yes |
| cycle_12_d1 | 1 | 2 | 3 | 3 | yes | yes |
| cycle_5_d2 | 2 | 1 | 2 | 2 | yes | yes |
| cycle_8_d2 | 2 | 1 | 3 | 3 | yes | yes |
| cycle_10_d2 | 2 | 2 | 2 | 2 | yes | yes |
| cycle_12_d2 | 2 | 2 | 3 | 3 | yes | yes |
| grid_2x2 | 1 | 1 | 2 | 2 | yes | yes |
| grid_2x3 | 1 | 1 | 2 | 2 | yes | yes |
| grid_3x3 | 1 | 1 | 3 | 3 | yes | yes |
| grid_4x4 | 1 | 1 | 4 | 4 | yes | yes |

The largest lower-side grid check enumerated 560 candidate supports.

## Closed-form corollaries supported

For connected F and d=1:

    K*_infty = gamma_tau(F).

For d-edge-connected F:

    K*_infty =
      min {|P| : |V(F) \ N_tau[P]| <= d-1}.

For a path P_m with d=1:

    K*_infty = ceil(m/(2 tau+1)).

For a cycle C_m with d=1:

    K*_infty = ceil(m/(2 tau+1)).

For a cycle C_m with d=2:

    K*_infty = ceil((m-1)/(2 tau+1)).

For a clique K_m:

    tau=0  => K*_infty = m-d+1,
    tau>=1 => K*_infty = 1.

Thus persistence does not by itself imply an n-independent bound; it turns the
dynamic reachability requirement into a covering requirement at spatial scale tau.

## Complexity corollary

The decision problem "is K*_infty <= k?" is NP-complete already for d=1,
tau=1, because Theorem B makes it exactly DOMINATING SET on a connected core.

No stronger all-(d,tau) complexity claim is recorded here.

## Scientific interpretation

Theorem A and Theorem B now give a clean boundary story:

- without persistence in the unrestricted moving-gateway clique construction,
  K*_infty=n-d;
- with a stable core and synchronized gateway dwell,
  K*_infty equals the appropriate distance-transversal/static covering number.

Theorem B does **not** prove that global per-edge persistence fixes unrestricted
rewiring. That stronger model remains parked as Theorem C.

## Artifact

Workflow artifact ID: 9641036438
