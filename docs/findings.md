# Reproducible demo findings

Source: default generator, seed 42. These findings describe **synthetic data** only.

| Measure | Result |
|---|---:|
| Sessions | 1,200 |
| Events | 9,412 |
| API attempts | 3,055 |
| Technical session success | 97.08% |
| User completion | 84.33% |
| Initially failed logical calls | 263 |
| Calls recovered by retry | 227 |
| Retry recovery | 86.31% |
| Technically successful sessions without completion | 153 |

## 1. Reliability and completion answer different questions

The gap between technical success and user completion is intentional. 153 sessions completed every required logical call but did not end with a completed user action. Reporting technical success as task completion would overstate the simulated product outcome.

## 2. The order provider warrants investigation

Order API attempts have a 14.77% error rate, above the other tools in this dataset. The generator injects higher failure probability and latency on 14–16 October. Filter the error dashboard to those dates and the order task; inspect an affected trace to see failures and retries. Source-code knowledge establishes the cause in the demo; production attribution would require independent incident evidence.

## 3. Retries can recover calls while still adding latency

227 of 263 initially failed calls recover on the second attempt. This describes recovery in the simulated retry policy. It does not establish how many users would have completed without retries, or whether another retry policy would be better.

## 4. Prompt comparisons need controls

The newer release starts halfway through the observation period. Its baseline failure probability is deliberately lower, and both versions encounter the provider incident. Aggregate cohort differences combine these assumptions with task mix and timing. Restrict to overlapping dates and inspect within-task rates before forming a hypothesis; use real controlled experimentation for causal conclusions.

## Recommended next work

Instrument a real toy agent; map events to the contract; connect an independent completion event; retain the original failure attempts; add safeguards for late or incomplete traces. Do not advertise the demo findings as business improvements.
