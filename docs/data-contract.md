# Data contract and provenance

## Source

Default source: `generate.py`, pseudorandom seed 42, 1,200 closed sessions beginning 24 September–23 October 2026 UTC. No personally identifiable real data is used. IDs, routes, endpoints and outcomes are fictitious. `llm` events are simulated tool calls, not model requests.

The simulator assigns one of three tasks per session. It routes each task to a fixed chain, permits one retry after a failed call, optionally reads memory, and writes a state version after technical success. It does not stop the route on a failed call. User outcomes are assigned after final output. All these are modelling choices, not facts about real agents.

## Session fields (one record per session)

| Field | Type | Meaning |
|---|---|---|
| session_id | string, unique | Primary key |
| user_id | string | Synthetic pseudonymous repeat user |
| agent_id | string | Agent label |
| started_at / ended_at | UTC ISO 8601 string | Trace bounds |
| prompt_version | string | Historical version label |
| task_type | string | knowledge_search, order_status, account_update |
| route | string | Ordered tool chain |
| technical_success | integer 0/1 | All logical calls eventually succeeded |
| user_outcome | enum | completed, abandoned, follow_up |
| memory_used | integer 0/1 | Memory-read session marker |
| resolution_ms | non-negative integer | Session elapsed time, all outcomes |

## Event fields (one record per event)

| Field | Type | Meaning |
|---|---|---|
| event_id | string, unique | Primary key |
| session_id | string | Foreign key to session |
| sequence | integer > 0 | Contiguous order within session |
| timestamp | UTC ISO 8601 string | Event start |
| event_type | enum | user_input, routing, memory_read, api_call, retry, memory_write, final_output, user_action |
| status | string | ok/error, or user outcome for user_action |
| duration_ms | non-negative number | Event duration |
| tool / endpoint | nullable string | Tool and synthetic endpoint for API events |
| call_id | nullable string | Globally unique logical call identifier for API/retry events |
| attempt | nullable integer | 1 or 2 for API events |
| error_type | nullable string | timeout, rate_limit, upstream_5xx for failed API events |
| state_before / state_after | nullable integer | Memory version before and after operation |

All fields must be present, including explicit nulls. No arbitrary input/output text is collected. This minimises accidental secret or prompt leakage.

## Loader checks

The loader validates IDs, foreign references, contiguous sequences, non-negative finite durations, timezone-aware UTC timestamps, ordering and session bounds, resolution-time reconciliation, final-output/user-outcome reconciliation, logical-call attempt order and technical-success reconciliation. SQLite additionally enforces enums, boolean domains, uniqueness, foreign keys and API required fields. Inserts are transactional: invalid imports roll back the database replacement.

Not every semantic property is enforced: route text and memory marker/counter consistency still rely on source instrumentation. This is explicitly a small closed-session demo contract. No late arrivals, partial traces or asynchronous span joins are supported.

## Import and privacy

Put `sessions.jsonl` and `events.jsonl` in a separate directory. One JSON object per line, UTF-8. Use `--input` as documented in the README. Provenance changes to `imported`; it does not certify external truthfulness. Remove identifiers, prompts, tokens, headers and secrets before importing. The complete telemetry is embedded in the HTML, so access to a shared dashboard exposes its underlying data.

The build replaces its generated outputs. Keep external source data outside `data/`. SQLite is generated locally and omitted from version control; JSONL files and the portable demo are included.
