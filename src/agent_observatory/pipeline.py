"""Validate JSONL, load transactional SQLite tables, export a portable dashboard."""
import argparse
import json
import math
from pathlib import Path
import sqlite3
from datetime import datetime
from .generate import generate

ROOT = Path(__file__).resolve().parents[2]


def validate(sessions, events):
    if not sessions:
        raise ValueError('No sessions provided')
    ids = {s['session_id'] for s in sessions}
    if len(ids) != len(sessions):
        raise ValueError('Duplicate session IDs')
    seen, grouped = set(), {sid: [] for sid in ids}
    call_owners = {}
    for e in events:
        if e['event_id'] in seen:
            raise ValueError('Duplicate event IDs')
        seen.add(e['event_id'])
        if e['session_id'] not in ids:
            raise ValueError('Orphan event')
        if not isinstance(e['duration_ms'], (int, float)) or not math.isfinite(e['duration_ms']) or e['duration_ms'] < 0:
            raise ValueError('Invalid duration')
        if e['event_type']=='api_call':
            owner = (e['session_id'],e['tool'])
            if call_owners.setdefault(e['call_id'],owner) != owner:
                raise ValueError('Logical call ID reused across sessions or tools')
        grouped[e['session_id']].append(e)
    for s in sessions:
        rows = sorted(grouped[s['session_id']], key=lambda r:r['sequence'])
        if not rows or [r['sequence'] for r in rows] != list(range(1, len(rows)+1)):
            raise ValueError('Missing or duplicate sequence')
        if rows[0]['event_type'] != 'user_input' or rows[-1]['event_type'] != 'user_action':
            raise ValueError('Incomplete trace')
        times = [datetime.fromisoformat(r['timestamp']) for r in rows]
        if any(t.utcoffset() is None or t.utcoffset().total_seconds() != 0 for t in times):
            raise ValueError('Timestamps must be UTC with timezone')
        start, end = datetime.fromisoformat(s['started_at']), datetime.fromisoformat(s['ended_at'])
        if start.utcoffset() is None or end.utcoffset() is None or start.utcoffset().total_seconds() != 0 or end.utcoffset().total_seconds() != 0:
            raise ValueError('Session times must be UTC')
        if times != sorted(times) or times[0] != start or times[-1] > end:
            raise ValueError('Invalid trace ordering or bounds')
        if rows[-1]['status'] != s['user_outcome']:
            raise ValueError('User outcome disagrees with trace')
        if abs((end-start).total_seconds()*1000 - s['resolution_ms']) > 1:
            raise ValueError('Resolution duration disagrees with timestamps')
        finals = [r for r in rows if r['event_type']=='final_output']
        if len(finals)!=1 or int(finals[0]['status']=='ok') != s['technical_success']:
            raise ValueError('Final output disagrees with session')
        calls = {}
        for r in rows:
            if r['event_type']=='api_call':
                calls.setdefault(r['call_id'], []).append(r)
        for attempts in calls.values():
            if [r['attempt'] for r in attempts] not in ([1], [1,2]):
                raise ValueError('Invalid attempt sequence')
            if len(attempts)==2 and attempts[0]['status']!='error':
                raise ValueError('Cannot retry a successful call')
        if not calls or int(all(any(r['status']=='ok' for r in a) for a in calls.values())) != s['technical_success']:
            raise ValueError('Call outcomes disagree with session')
        if s['user_outcome']=='completed' and not s['technical_success']:
            raise ValueError('Demo contract requires technical success for completion')


def load(db, sessions, events):
    validate(sessions, events)
    db.executescript((ROOT/'sql/schema.sql').read_text())
    # Atomically replace both tables; never leave a partial import.
    with db:
        db.execute('DELETE FROM events')
        db.execute('DELETE FROM sessions')
        for table, rows in [('sessions',sessions),('events',events)]:
            keys = list(rows[0])
            expected = [r[1] for r in db.execute(f'PRAGMA table_info({table})')]
            if set(keys)!=set(expected) or any(set(r)!=set(keys) for r in rows):
                raise ValueError(f'Unexpected fields in {table}')
            db.executemany(f'INSERT INTO {table} ({",".join(keys)}) VALUES ({",".join("?" for _ in keys)})',
                           [[r[k] for k in keys] for r in rows])


def rows(db, query):
    db.row_factory = sqlite3.Row
    return [dict(r) for r in db.execute(query)]


def export(db, output, provenance=None):
    payload = dict(sessions=rows(db,'SELECT * FROM sessions ORDER BY started_at'),
                   events=rows(db,'SELECT * FROM events ORDER BY session_id,sequence'),
                   provenance=provenance or dict(kind='synthetic', seed=42))
    template = (ROOT/'dashboard/template.html').read_text()
    # Prevent embedded payloads from terminating the script element.
    encoded = json.dumps(payload,separators=(',',':'),allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(template.replace('__PAYLOAD__',encoded),encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sessions',type=int,default=1200)
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--input',type=Path,help='Directory containing sessions.jsonl and events.jsonl; must follow demo contract')
    args = p.parse_args()
    data = ROOT/'data'
    data.mkdir(exist_ok=True)
    if args.input:
        sessions, events = [[json.loads(line) for line in (args.input/f'{name}.jsonl').read_text().splitlines() if line.strip()]
                            for name in ['sessions','events']]
    else:
        sessions, events = generate(args.sessions,args.seed)
    validate(sessions,events)
    for name, records in [('sessions',sessions),('events',events)]:
        (data/f'{name}.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    with sqlite3.connect(data/'observatory.db') as db:
        load(db,sessions,events)
        export(db,ROOT/'dashboard/index.html', dict(kind='imported' if args.input else 'synthetic', seed=None if args.input else args.seed))
        report = dict(sessions=len(sessions),events=len(events),
            summary=rows(db,"SELECT ROUND(100.0*AVG(technical_success),2) technical_success_pct, ROUND(100.0*AVG(user_outcome='completed'),2) completion_pct FROM sessions")[0],
            tools=rows(db,"SELECT tool,COUNT(*) attempts,ROUND(100.0*AVG(status='error'),2) error_pct FROM events WHERE event_type='api_call' GROUP BY tool"))
    report['provenance'] = {'kind':'imported' if args.input else 'synthetic','seed':None if args.input else args.seed}
    (data/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
