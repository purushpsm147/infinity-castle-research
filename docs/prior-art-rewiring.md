# Prior-art note: adversarial rewiring

The project initially treated per-round connected rewiring as potentially less occupied than fixed-footprint temporal-graph models. A targeted literature check found direct prior art.

## Direct overlap

**Kawamura, Shiina, Aung, Ohsaki (IEEE COMPSAC 2024)**, "Robustness of Random Walk on a Graph against Adversary Attacks", DOI 10.1109/COMPSAC61105.2024.00146.

The paper studies target-node search and graph exploration while an adversary rewires a limited number of links, evaluating multiple random-walk policies under several attack strategies.

**Hirayama, Aung, Ohsaki (IEEE COMPSAC 2025)**, "Understanding and Mitigating Vulnerabilities of Random Walks against Adversarial Attacks", DOI 10.1109/COMPSAC65507.2025.00127.

The follow-up broadens link-deletion and link-addition attack strategies and again evaluates hitting time / cover time.

## Consequence for this repository

The following are not safe novelty claims:

- "bounded rewiring during navigation";
- "target search under adversarial link rewiring";
- "route concentration as an attack surface" in the broad sense.

A possible future contribution would need a much sharper distinction, such as a formal result, stronger multi-agent model, or domain-specific constraint not already covered by adjacent temporal-graph, random-walk, sabotage-game, or interdiction literature. No such gap is claimed here.
