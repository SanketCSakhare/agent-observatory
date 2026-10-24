# Explain this project in an interview

## 30-second description

“I built an AI agent observability project using Python, SQLite and a browser dashboard. It tracks the sequence of tool calls, failures, retries and memory events, then connects those to user completion. I used clearly labelled simulated data so I could reproduce a provider outage and test whether my metrics and traces exposed it correctly.”

## Why not just count errors?

“One logical tool call can fail once and then recover after a retry. I keep both attempts in the error rate, but measure recovery at logical-call level. I also measure user completion separately, because a successful API response does not prove the user finished their task.”

## What was the main data modelling decision?

“I separated sessions from events and used a logical call ID to group retries. That lets me measure session outcomes without giving long sessions extra weight. SQL constraints and validation checks reject broken traces before loading the data.”

## Did v1.1 improve performance?

“The simulator explicitly gives it a lower baseline failure probability. The dashboard can compare the resulting cohorts, but I would not call that a measured production improvement. In real data I would compare overlapping dates and task types, then use a controlled experiment for causal claims.”

## How did you validate it?

“I reconciled SQL metrics with the raw records and tested invalid imports, retry denominators, duplicate events, missing sequences and timestamp ordering. I also tested dashboard rendering and filter logic in a JavaScript harness. Full browser interaction and visual testing are still pending because the build environment could not install a browser.”

## What would you build next?

“I would instrument a real, low-risk agent and map its traces into the event contract. Then I would add independent product completion events, redact sensitive fields, and support incomplete sessions and concurrent spans before treating it as operational monitoring.”

## Claims to avoid

Do not claim production deployment, reduced costs, improved reliability, real customer impact, statistical significance or implemented OpenTelemetry support. The project demonstrates engineering and analytical reasoning with synthetic telemetry.
