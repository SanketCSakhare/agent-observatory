-- Attempt grain: errors before retries are still counted.
SELECT tool, COUNT(*) AS attempts,
       ROUND(100.0*SUM(status='error')/COUNT(*),2) AS error_pct,
       ROUND(AVG(duration_ms),1) AS mean_latency_ms
FROM events WHERE event_type='api_call' GROUP BY tool ORDER BY error_pct DESC;

-- Logical call grain: recovery denominator is initially failed calls.
SELECT SUM(initially_failed) AS initially_failed,
       SUM(initially_failed*succeeded) AS recovered,
       ROUND(100.0*SUM(initially_failed*succeeded)/NULLIF(SUM(initially_failed),0),2) AS recovery_pct
FROM call_outcomes;

-- Session grain. Never join sessions to raw events before averaging outcomes.
SELECT prompt_version,task_type,COUNT(*) AS sessions,
       ROUND(100.0*AVG(technical_success),2) AS technical_success_pct,
       ROUND(100.0*AVG(user_outcome='completed'),2) AS completion_pct
FROM sessions GROUP BY prompt_version,task_type;

-- Inspect the injected incident by UTC date and tool.
SELECT substr(timestamp,1,10) AS day,tool,COUNT(*) AS attempts,
       ROUND(100.0*AVG(status='error'),2) AS error_pct
FROM events WHERE event_type='api_call' GROUP BY day,tool ORDER BY day,tool;
