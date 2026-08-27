# Theorem B — Synchronous Gateway-Dwell Characterization

## Scope and relation to Theorem A

This theorem studies a **weaker adversary** than the Moving-Gateway Threshold
Theorem (Theorem A).

Theorem A allows post-move one-for-one rewiring anywhere in the graph. Theorem B
freezes the core graph and allows only the target gateway edges to relocate at
synchronized epoch boundaries.

Therefore Theorem B does **not** subsume Theorem A. They coincide on the
clique-core family at tau=0 because Theorem A's lower-bound adversary never
needed to edit the clique core.

The more general model in which every edge may be rewired but newly created
edges receive tau-round persistence is deliberately parked as **Theorem C**.

## Frozen model

Let F=(V,E) be a fixed connected simple undirected core graph with source s in V.
The target t is external to F.

Parameters:

- d >= 1: number of target gateway edges in each epoch;
- tau >= 0: spatial pursuit radius induced by gateway persistence;
- b >= d: per-boundary replacement budget.

At the start of every synchronized epoch:

1. the adversary observes all agent positions;
2. she chooses exactly d gateway vertices S subseteq V;
3. the epoch graph is F plus edges {vt : v in S};
4. the resulting graph must satisfy lambda(s,t) >= d;
5. the gateway set S remains unchanged for exactly tau+1 agent moves.

Agents:

- have full visibility of F and the current gateway edges;
- know when a fresh epoch begins;
- move at most one edge per agent move;
- may wait and may co-locate;
- win immediately when any agent reaches t.

At the epoch boundary the adversary may atomically replace the old d gateway
edges by the next d gateway edges. Intermediate delete-before-add states are not
part of the game. Constraints are checked on the resulting epoch graph.

The admissible gateway family must be nonempty.

## Admissible gateway family

Define

A_d(F,s) = {
    S subseteq V(F) :
    |S|=d and lambda_{F+tS}(s,t) >= d
}.

This absorbs the lambda-floor directly into the legal adversary action set.
On sparse cores, not every d-subset need be admissible.

## Distance-transversal quantity

For nonempty vertex sets P,S subseteq V(F), define

dist_F(P,S) = min_{p in P, v in S} dist_F(p,v).

Define

rho_tau(F,A_d) =
    min {|P| :
         for every S in A_d(F,s),
         dist_F(P,S) <= tau }.

This is a distance transversal / covering quantity over the admissible gateway
family. It is not introduced as a new graph invariant.

For d=1 on a connected core, A_1 consists of every singleton vertex and rho_tau
is exactly the standard distance-tau domination number gamma_tau(F).

## Theorem B

**Synchronous Gateway-Dwell Theorem.**

Under the frozen model above,

    K*_infty = rho_tau(F,A_d(F,s)).

Here K*_infty is the minimum number of persistent centrally coordinated agents
that can force eventual reachability of t.

### Lower bound

Take k < rho_tau agents. At the beginning of any fresh epoch let P be the set of
distinct occupied core vertices. Co-location implies |P| <= k.

By the definition of rho_tau, there exists an admissible gateway set S such that

    dist_F(P,S) > tau.

Distances are integral, hence every agent is at distance at least tau+1 from
every gateway.

Reaching a gateway therefore requires at least tau+1 moves, followed by one
additional move along the gateway edge to t. Arrival needs at least tau+2 moves.

The gateway set survives only tau+1 agent moves.

Thus nobody reaches t during this epoch. At the next fresh epoch the adversary
observes the new positions and repeats the same argument. She can prevent
arrival forever.

Therefore

    K*_infty >= rho_tau.

### Upper bound

Let P* be a minimum distance transversal with

    |P*| = rho_tau.

Because F is fixed and connected, the agents can first reposition so that one
agent occupies every vertex of P*. They may then wait for a fresh observable
epoch boundary.

For any legal gateway set S in A_d,

    dist_F(P*,S) <= tau.

Hence some agent is at distance at most tau from some gateway. That agent reaches
the gateway in at most tau moves and traverses the final gateway edge to t on
the next move.

Arrival occurs within tau+1 moves, before the gateway set is allowed to change.

Therefore

    K*_infty <= rho_tau.

Combining both inequalities proves the theorem.

## d-edge-connected core corollary

If F is d-edge-connected, then every d-subset S of V(F) is admissible.

For any proper s-side cut X of F, at least d core edges cross the cut. For the
cut containing all of F, exactly d target edges cross. Thus for every d-set S,

    lambda_{F+tS}(s,t) = d.

In this case the theorem becomes

    K*_infty =
      min {|P| : |V(F) \ N_tau[P]| <= d-1}.

Equivalently, the agents need only distance-tau dominate all but at most d-1
core vertices.

## Special graph families

### Connected core, d=1

    K*_infty = gamma_tau(F),

the ordinary distance-tau domination number.

### Clique K_m

For tau=0,

    K*_infty = m-d+1.

Taking m=n-1 recovers Theorem A's clique threshold n-d.

For tau>=1,

    K*_infty = 1.

Thus on the clique, one move of genuine gateway persistence collapses the
threshold from n-d to one.

### Path P_m, d=1

    K*_infty = ceil(m/(2 tau+1)).

Therefore any fixed tau still permits K*=Theta(m).

### Cycle C_m, d=1

    K*_infty = ceil(m/(2 tau+1)).

### Cycle C_m, d=2

Because C_m is 2-edge-connected, one vertex may remain outside N_tau[P].
Choosing that uncovered vertex breaks the remaining m-1 vertices into a path,
and each radius-tau center covers at most 2 tau+1 consecutive vertices.
Therefore

    K*_infty = ceil((m-1)/(2 tau+1)).

## Complexity corollary

Consider the decision problem:

    given the frozen gateway-dwell instance and k, is K*_infty <= k?

This problem is NP-complete already in the restricted case d=1, tau=1.

By Theorem B,

    K*_infty = gamma(F)

in that case. Therefore the decision question is exactly DOMINATING SET on the
connected core F.

Membership in NP follows by supplying a candidate vertex set P of size <=k and
checking in polynomial time that every core vertex lies within distance one.

No broader NP-completeness claim for every fixed d,tau is made here.

## Relation to domination games

For d=1, the static parameter is classical distance domination. This should be
positioned explicitly against two neighboring game families:

1. **Eternal distance-k domination** (Cox, Meger & Messinger; subsequent tree
   work by Clow et al.): guards must respond to an infinite sequence of attacks
   while continuously maintaining a valid defensive configuration. The eternal
   value may exceed the static distance-domination number because a response can
   degrade the future formation.

2. **The domination game** (Brešar, Klavžar & Rall): Dominator and Staller
   alternately choose vertices while constructing a dominating set. Its move
   structure and objective differ from the present reachability game.

Theorem B is one-shot: once an agent reaches t, the game ends. The intercepting
agent never has to restore the covering formation. That is why the game value
can equal a static covering quantity rather than an eternal one.

## What persistence does and does not fix

The theorem does **not** say that any fixed amount of persistence yields an
n-independent bound.

It says that redundancy is exactly governed by the coverability of the stable
geometry at radius tau.

For paths and cycles, fixed tau leaves K*=Theta(n). For bounded-radius or
bounded distance-covering-number families, the required number of agents can be
bounded independently of n.

The relevant design variable is therefore not tau alone but persistence relative
to the spatial covering scale of the stable core.

## Parked extensions — Theorem C territory

The following are deliberately excluded from this result:

- globally rewritable cores where every new edge receives a tau-round lifetime;
- b < d, where a full gateway set cannot be relocated in one boundary;
- staggered per-gateway expiration rather than synchronized epochs;
- repeated delivery / repeated targets, where formation degradation may matter.

No implementation or conjecture for these variants belongs in the Theorem B
validation phase.
