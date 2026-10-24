import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from agent_observatory.generate import generate
from agent_observatory.pipeline import load, validate, export, ROOT

class ObservatoryTests(unittest.TestCase):
    def setUp(self):
        self.s,self.e=generate(80,42)
        self.db=sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        load(self.db,self.s,self.e)

    def test_reproducibility(self):
        self.assertEqual(generate(80,42),(self.s,self.e))
        self.assertNotEqual(generate(80,43),(self.s,self.e))

    def test_sql_session_metrics_match_source(self):
        result=self.db.execute("SELECT COUNT(*),SUM(technical_success),SUM(user_outcome='completed') FROM sessions").fetchone()
        self.assertEqual(result,(80,sum(s['technical_success'] for s in self.s),sum(s['user_outcome']=='completed' for s in self.s)))

    def test_call_recovery_denominator(self):
        calls={}
        for e in self.e:
            if e['event_type']=='api_call': calls.setdefault(e['call_id'],[]).append(e)
        failed=[a for a in calls.values() if a[0]['status']=='error']
        recovered=[a for a in failed if any(e['status']=='ok' for e in a)]
        counts=self.db.execute('SELECT COUNT(*),SUM(initially_failed),SUM(initially_failed*succeeded) FROM call_outcomes').fetchone()
        self.assertEqual(counts,(len(calls),len(failed),len(recovered)))
        self.assertGreater(len(failed),0)

    def test_duplicate_event_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate event'):validate(self.s,self.e+[self.e[0]])

    def test_orphan_rejected(self):
        bad=copy.deepcopy(self.e);bad[0]['session_id']='missing'
        with self.assertRaisesRegex(ValueError,'Orphan'): validate(self.s,bad)

    def test_sequence_gap_rejected(self):
        with self.assertRaisesRegex(ValueError,'sequence'): validate(self.s,self.e[1:])

    def test_negative_latency_rejected(self):
        bad=copy.deepcopy(self.e);bad[0]['duration_ms']=-1
        with self.assertRaisesRegex(ValueError,'duration'): validate(self.s,bad)

    def test_outcome_mismatch_rejected(self):
        bad=copy.deepcopy(self.s);bad[0]['user_outcome']='bad'
        with self.assertRaises(ValueError): validate(bad,self.e)

    def test_time_order_rejected(self):
        bad=copy.deepcopy(self.e);bad[1]['timestamp']='2020-01-01T00:00:00+00:00'
        with self.assertRaisesRegex(ValueError,'ordering'): validate(self.s,bad)

    def test_attempt_sequence_rejected(self):
        bad=copy.deepcopy(self.e)
        next(e for e in bad if e['event_type']=='api_call')['attempt']=2
        with self.assertRaisesRegex(ValueError,'attempt'):validate(self.s,bad)

    def test_transaction_rolls_back_invalid_schema(self):
        bad=copy.deepcopy(self.s);bad[0]['unexpected']='x'
        with self.assertRaises(ValueError):load(self.db,bad,self.e)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM sessions').fetchone()[0],80)

    def test_export_escapes_script_payload(self):
        bad=copy.deepcopy(self.s);bad[0]['user_id']='</script><script>alert(1)</script>'
        load(self.db,bad,self.e)
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'index.html';export(self.db,out)
            text=out.read_text()
            self.assertNotIn('</script><script>alert(1)',text)
            payload=text.split('<script id="telemetry" type="application/json">')[1].split('</script>')[0]
            self.assertEqual(len(json.loads(payload)['sessions']),80)

    def test_cross_session_call_id_rejected(self):
        bad=copy.deepcopy(self.e)
        api=[e for e in bad if e['event_type']=='api_call']
        other=next(e for e in api if e['session_id']!=api[0]['session_id'])
        other['call_id']=api[0]['call_id']
        with self.assertRaisesRegex(ValueError,'reused'):validate(self.s,bad)

    def test_all_sql_queries_execute(self):
        for query in (ROOT/'sql/metrics.sql').read_text().split(';'):
            if query.strip():self.db.execute(query).fetchall()

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):generate(0)
        with self.assertRaises(ValueError):validate([],[])

if __name__=='__main__':unittest.main()
