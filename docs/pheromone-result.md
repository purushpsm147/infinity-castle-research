# Pheromone-consensus gate result

Date: 2026-08-27

## Verdict

**FAIL — do not tune.**

The first frozen experiment used:
- 8 active crows;
- 30 seeds;
- grid, ladder, and connected Erdos-Renyi graph families;
- traffic-aware and reactive-cut adversaries with b in {1,2};
- separate policy/adversary random streams;
- identical adversary random streams across policies within each paired cell.

The gate was frozen before the result:
- shared memory must beat the same adaptive consensus/contrarian mechanism with memory disabled in at least 2 hostile cells;
- adaptive contrarians must beat pure pheromone consensus in at least 2 hostile cells;
- at least 1 hostile cell must satisfy both.

Observed:

- hostile cells: 12
- memory wins: **0**
- contrarian wins: **5**
- joint wins: **0**

Therefore the gate failed.

## What the result actually says

The strongest signal is **not** that pheromone memory improved navigation.

The adaptive policy with pheromone memory and the otherwise matched no-memory control were extremely similar. In several cells the no-memory control used slightly less work.

Examples:

### Grid 6x6, reactive-cut, b=2

- adaptive no-memory: P(reach)=1.00, mean work=132.27
- pheromone adaptive: P(reach)=1.00, mean work=129.60
- pure pheromone consensus: P(reach)=0.10, mean work=541.07

### Ladder-12, reactive-cut, b=2

- adaptive no-memory: P(reach)=1.00, mean work=163.47
- pheromone adaptive: P(reach)=1.00, mean work=165.33
- pure pheromone consensus: P(reach)=0.00, mean work=560.00

### ER-36, reactive-cut, b=2

- adaptive no-memory: P(reach)=1.00, mean work=51.73
- pheromone adaptive: P(reach)=1.00, mean work=51.20
- pure pheromone consensus: P(reach)=0.10, mean work=533.33

So the useful component in this configuration was largely **maintaining exploration / avoiding consensus collapse**, not the shared pheromone memory.

## Important limitation discovered after preregistration

The closed-form contrarian fraction used in the toy model maximizes a one-junction objective:

P(at least one crow takes the correct branch).

That objective:
- gives zero marginal value to additional followers once one succeeds;
- ignores multi-step trajectory cost;
- ignores common-cause failure when the demon attacks a shared route.

Also, the policy's softmax top probability is not a calibrated probability that the consensus branch is truly correct. Therefore the closed-form epsilon* must be treated only as a toy heuristic, not as a castle-optimal rule.

These limitations make the negative result no stronger than "this implementation did not justify tuning." They do **not** rescue the mechanism.

## Stop rule

No optimization of:
- crow count;
- pheromone decay;
- pheromone weights;
- consensus temperature;
- contrarian fraction

is performed after this result.

If the idea is reopened later, adversarial-bandit / expert-advice / adversarial-MDP baselines are mandatory first. See prior-art-online-learning.md.
