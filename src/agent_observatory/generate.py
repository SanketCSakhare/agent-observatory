"""Synthetic support-agent telemetry. No real users, APIs or model calls."""
from datetime import datetime, timedelta, timezone
import random


def generate(n=1200, seed=42):
    if n < 1:
        raise ValueError('sessions must be positive')
    rng = random.Random(seed)
    sessions, events = [], []
    for i in range(n):
        day = i % 30
        start = datetime(2026, 9, 24, tzinfo=timezone.utc) + timedelta(days=day, seconds=rng.randrange(86400))
        version = rng.choice(['v1.0', 'v1.1']) if day >= 14 else 'v1.0'
        task = rng.choice(['knowledge_search', 'order_status', 'account_update'])
        route = {'knowledge_search': ['search', 'llm'], 'order_status': ['orders_api', 'llm'], 'account_update': ['identity_api', 'profile_api', 'llm']}[task]
        sid = f'session-{i+1:05d}'
        t = start
        seq = 0
        def emit(kind, status='ok', duration_ms=0, **extra):
            nonlocal t, seq
            seq += 1
            row = dict(event_id=f'{sid}:{seq:02d}', session_id=sid, sequence=seq,
                       timestamp=t.isoformat(), event_type=kind, status=status,
                       duration_ms=duration_ms, tool=None, endpoint=None, call_id=None,
                       attempt=None, error_type=None, state_before=None, state_after=None)
            row.update(extra)
            events.append(row)
            t += timedelta(milliseconds=duration_ms + 30)
        emit('user_input')
        emit('routing')
        memory = rng.random() < .55
        if memory:
            emit('memory_read', duration_ms=rng.randrange(15, 100), state_before=1, state_after=1)
        reliable = True
        # Injected incident: order provider degrades on days 20–22, both versions.
        incident = 20 <= day <= 22
        for j, tool in enumerate(route):
            call_id = f'{sid}/call-{j+1}'
            base = .06 if version == 'v1.1' else .10
            fail_rate = .43 if incident and tool == 'orders_api' else base
            ok = False
            for attempt in (1, 2):
                latency = int(rng.lognormvariate(6.1 if tool != 'llm' else 6.8, .5))
                if incident and tool == 'orders_api':
                    latency *= 3
                ok = rng.random() >= fail_rate
                emit('api_call', 'ok' if ok else 'error', latency,
                     tool=tool, endpoint=f'/demo/{tool}', call_id=call_id, attempt=attempt,
                     error_type=None if ok else rng.choice(['timeout', 'rate_limit', 'upstream_5xx']))
                if ok:
                    break
                if attempt == 1:
                    emit('retry', tool=tool, call_id=call_id)
            reliable = reliable and ok
        if memory and reliable:
            emit('memory_write', duration_ms=35, state_before=1, state_after=2)
        emit('final_output', 'ok' if reliable else 'error', 120)
        # User completion is deliberately different from technical success.
        completed = reliable and rng.random() < (.89 if task != 'account_update' else .78)
        outcome = 'completed' if completed else ('abandoned' if rng.random() < .65 else 'follow_up')
        emit('user_action', status=outcome)
        sessions.append(dict(session_id=sid, user_id=f'user-{rng.randrange(1,401):04d}',
            agent_id='support-agent', started_at=start.isoformat(), ended_at=t.isoformat(),
            prompt_version=version, task_type=task, route=' → '.join(route),
            technical_success=int(reliable), user_outcome=outcome, memory_used=int(memory),
            resolution_ms=round((t-start).total_seconds()*1000)))
    return sessions, events
