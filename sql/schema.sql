PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sessions (
 session_id TEXT PRIMARY KEY, user_id TEXT NOT NULL, agent_id TEXT NOT NULL,
 started_at TEXT NOT NULL, ended_at TEXT NOT NULL, prompt_version TEXT NOT NULL,
 task_type TEXT NOT NULL, route TEXT NOT NULL,
 technical_success INTEGER NOT NULL CHECK(technical_success IN (0,1)),
 user_outcome TEXT NOT NULL CHECK(user_outcome IN ('completed','abandoned','follow_up')),
 memory_used INTEGER NOT NULL CHECK(memory_used IN (0,1)),
 resolution_ms INTEGER NOT NULL CHECK(resolution_ms>=0)
);
CREATE TABLE IF NOT EXISTS events (
 event_id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(session_id),
 sequence INTEGER NOT NULL CHECK(sequence>0), timestamp TEXT NOT NULL,
 event_type TEXT NOT NULL CHECK(event_type IN ('user_input','routing','memory_read','memory_write','api_call','retry','final_output','user_action')),
 status TEXT NOT NULL, duration_ms INTEGER NOT NULL CHECK(duration_ms>=0),
 tool TEXT, endpoint TEXT, call_id TEXT, attempt INTEGER, error_type TEXT,
 state_before INTEGER, state_after INTEGER,
 UNIQUE(session_id,sequence),
 CHECK(event_type!='api_call' OR (tool IS NOT NULL AND call_id IS NOT NULL AND attempt IN (1,2) AND status IN ('ok','error'))),
 CHECK((status='error' AND event_type='api_call' AND error_type IS NOT NULL) OR event_type!='api_call' OR status='ok')
);
CREATE INDEX IF NOT EXISTS events_session ON events(session_id,sequence);
CREATE INDEX IF NOT EXISTS events_tool ON events(event_type,tool);
CREATE VIEW IF NOT EXISTS call_outcomes AS
 SELECT session_id,call_id,tool,COUNT(*) attempts,
 MAX(CASE WHEN status='ok' THEN 1 ELSE 0 END) succeeded,
 MAX(CASE WHEN attempt=1 AND status='error' THEN 1 ELSE 0 END) initially_failed
 FROM events WHERE event_type='api_call' GROUP BY session_id,call_id,tool;
