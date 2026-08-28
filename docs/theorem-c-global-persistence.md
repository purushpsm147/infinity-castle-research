# Theorem C — global per-edge persistence foothold

## Status

This note validates only the **proved foothold** used in the manuscript. It is
not a general solution of globally rewritable persistent-edge reachability.

The full class is denoted C_tau:

- O3p timing: agents move and success is checked before the adversary edits;
- one-for-one replacement budget b;
- fixed edge count, simplicity, connectivity, and lambda(s,t) floor;
- the adversary may rewire anywhere;
- every inserted edge receives a persistence lock tau.

An edge inserted after a round is guaranteed to exist for the next agent move.
When tau=0 it may be deleted in the post-move edit immediately following that
move. Therefore C_0 is exactly the repository's base O3p replacement semantics.

## Mechanical boundary check: C_0 = Theorem A's base model

For frozen G_{n,1} instances with n in {3,4,5,6}, the harness compares the
complete set of legal first rewire successors under C_0 with
ExactRewireGame.rewire_successors. The edge-state successor sets must agree
exactly.

This is a semantics regression, not a new mathematical theorem.

## Proved positive-persistence proposition

For the clique-core family G_{n,1}, with b=d=1 and tau>=1,

    K*_H(G_{n,1}; C_tau) = K*_infty(G_{n,1}; C_tau) = 1

for every H>=3.

The proof strategy is:

1. the one agent moves from the source to the current target gateway g;
2. if g-t remains, the agent crosses on the next move;
3. if g-t is replaced, connectedness forces a new target edge u-t;
4. because the only deletion in that branch was g-t, the clique edge g-u remains;
5. the agent moves g->u;
6. the newly inserted u-t edge is still locked during the following post-move
   adversary phase, so the agent crosses on move 3 before another edit.

The mechanical certificate exhaustively enumerates every legal first successor
and, in every gateway-relocation branch, every legal second successor. It checks
that the replacement target edge remains locked through the critical chase move.

Frozen cases:

- n in {3,4,5,6,7};
- tau in {1,2,3};
- b=d=lambda_min=1.

An independent exact finite-game smoke test on G_{4,1} also checks:

- C_0, k=1, H=2: lose;
- C_0, k=3, H=2: win;
- C_1, k=1, H=2: lose;
- C_1, k=1, H=3: win.

## What is deliberately not tested

No d=2 or b=2 sweep is included.

The general C_tau game for b,d>=2 remains an open problem in the manuscript.
The repository artifact exists to guard model semantics and the proved
b=d=1 proposition, not to generate a post-hoc extension.
