# Metric dictionary

All date filters use the **session start date in UTC**, inclusively. Events from a selected session remain attached even if they cross midnight. Excluded sessions do not contribute to event metrics. Empty denominators display an em dash. Latency percentiles use linear interpolation at `(n−1) × q`.

| Metric | Grain | Definition |
|---|---|---|
| Sessions | Session | Count of selected session IDs |
| Technical success | Session | Sessions in which every logical call eventually succeeds / sessions |
| User completion | Session | Sessions with explicit `completed` user action / sessions |
| Abandonment | Session | Sessions labelled `abandoned` / sessions |
| Follow-up | Session | Sessions labelled `follow_up` / sessions |
| API attempts | API event | Count of API call events including retries |
| API error rate | API event | Failed API attempts / all API attempts |
| Retry attempt share | API event | Attempts numbered above 1 / all API attempts |
| Calls needing retry | Logical call | Calls with a failed first attempt |
| Retry recovery | Logical call | Initially failed calls with a later success / initially failed calls |
| Logical tool call success | Logical call | Calls with any successful attempt / logical calls; available from SQL view |
| Mean / P50 / P95 API latency | API event | Duration per attempt, including failed attempts; not session time |
| Mean session duration | Session | Mean elapsed time across all selected sessions |
| Time to resolution | Completed session | Mean elapsed time among completed sessions only |
| Memory sessions | Session | Sessions with memory read / selected sessions |
| Memory reads / writes | Memory event | Counts of explicit read / write events |
| Route success | Session / route | Technical success among sessions in the same full route |

## Analytical guardrails

- Do not average session success over an event-joined table: long sessions would get extra weight.
- Do not remove recovered failures from API error rate. A retry is another attempt, not an erasure.
- Do not divide retry recoveries by all successful calls. The eligible population is initially failed calls.
- Do not describe prompt or memory differences as causal effects. Version timing and task mix differ; the simulator also encodes its own assumptions.
- Do not call memory state counters RAM usage, hallucination quality, or memory correctness.
- No active prompt version is inferred: release labels in historical telemetry are not a deployment registry.
- Cohorts are sessions, not independent users. Repeated user IDs are present; no confidence intervals or statistical significance claims are made.
