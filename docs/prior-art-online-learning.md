# Prior-art checkpoint: consensus, contrarians, and online learning

The pheromone-consensus idea is not treated as a novelty claim.

## Closest algorithmic literature

### Adversarial bandits: EXP3 / EXP4

Auer, Cesa-Bianchi, Freund, and Schapire, "The Nonstochastic Multiarmed Bandit Problem", SIAM Journal on Computing 32(1), 48-77 (2002), DOI 10.1137/S0097539701398375.

EXP3 addresses exploration/exploitation when an adversary controls arm payoffs. The same paper also gives an expert-advice extension (EXP4 family), which is the natural baseline when multiple pheromone channels are interpreted as experts recommending actions.

### Sequential version: adversarial MDPs

The Infinity Castle is not literally a stateless bandit: a branch choice changes the next graph state. Relevant theory therefore includes online/adversarial Markov decision processes.

Examples:
- Neu, Antos, Gyorgy, Szepesvari, "Online Markov Decision Processes under Bandit Feedback", NeurIPS 2010.
- Jin, Jin, Luo, Sra, Yu, "Learning Adversarial Markov Decision Processes with Bandit Feedback and Unknown Transition", ICML 2020.

Any future claim about a trajectory-level exploration rule must compare against this literature, not only against epsilon-greedy-like controls.

### Thompson sampling

Thompson sampling is useful as a stochastic/Bayesian probability-matching baseline, but ordinary Thompson sampling does not by itself supply an adversarial guarantee. It should not be described as the canonical adversarial baseline.

Reference: Russo, Van Roy, Kazerouni, Osband, Wen, "A Tutorial on Thompson Sampling", Foundations and Trends in Machine Learning 11(1), 2018.

### Pheromone collapse prevention

MAX-MIN Ant System already constrains pheromone values to prevent runaway concentration/stagnation.

Reference: Stutzle and Hoos, "MAX-MIN Ant System", Future Generation Computer Systems 16(8), 889-914 (2000).

### Biological consensus / cross-inhibition

Honeybee swarms already provide a biological example of heterogeneous positive evidence plus inhibitory signaling between competing alternatives.

Reference: Seeley et al., "Stop Signals Provide Cross Inhibition in Collective Decision-Making by Honeybee Swarms", Science 335(6064), 108-111 (2012), DOI 10.1126/science.1210361.

## Consequence

"Adapt the exploration/contrarian fraction to consensus reliability under adversarial drift" is not sufficient as a novelty statement.

If this project is ever reopened, the minimum algorithmic baseline set includes:
- EXP3-style local adversarial exploration;
- EXP4-style expert aggregation for multiple signal channels;
- a trajectory-aware adversarial-MDP baseline where computationally feasible;
- edge-disjoint / robust routing;
- stochastic probability matching only as a secondary control.

A precise uncovered gap must be written before another optimization phase begins.
