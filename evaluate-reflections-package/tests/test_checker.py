import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'evaluate-reflections'
spec=importlib.util.spec_from_file_location('checker',SKILL/'scripts/check_evidence.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA=json.loads((SKILL/'references/demo-input.json').read_text())
class Checks(unittest.TestCase):
 def test_source_failures_and_semantic_boundary(self):
  r={x['case_id']:x for x in m.evaluate(DATA)['results']}
  expected={'missing-passage':'MISSING_SOURCE','fabricated-quote':'QUOTE_MISMATCH','wrong-speaker':'SPEAKER_MISMATCH','inflated-count':'SESSION_COUNT_MISMATCH','duplicate-citation':'DUPLICATE_CITATION','unsupported-claim':'UNSOURCED_CLAIM'}
  for cid,code in expected.items():
   with self.subTest(cid=cid):self.assertIn(code,[x['code'] for x in r[cid]['issues']])
  for cid in ['requested-advice','thin-history','changed-behavior']:
   self.assertEqual(r[cid]['source_status'],'PASS');self.assertEqual(r[cid]['interpretation_status'],'NOT_TESTED')
 def test_duplicate_identifiers_rejected(self):
  for kind in ['case','session','passage']:
   d=copy.deepcopy(DATA)
   if kind=='case':d['cases'].append(d['cases'][0])
   elif kind=='session':d['cases'][0]['sessions'].append(d['cases'][0]['sessions'][0])
   else:d['cases'][0]['sessions'][0]['passages'].append(d['cases'][0]['sessions'][0]['passages'][0])
   with self.subTest(kind=kind), self.assertRaises(ValueError):m.evaluate(d)
 def test_bad_counts_rejected(self):
  for count in [True,-1,1.5,'3']:
   d=copy.deepcopy(DATA);d['cases'][0]['reflection']['declared_session_count']=count
   with self.subTest(count=count),self.assertRaises(ValueError):m.evaluate(d)
 def test_abstention(self):
  d=copy.deepcopy(DATA);d['cases'][0]['reflection']['claim']=''
  self.assertIn('INCONSISTENT_ABSTENTION',[x['code'] for x in m.evaluate(d)['results'][0]['issues']])
 def test_cli_and_overwrite_protection(self):
  with tempfile.TemporaryDirectory() as td:
   inp=Path(td)/'input.json';inp.write_text(json.dumps(DATA));before=inp.read_bytes()
   cmd=[sys.executable,str(SKILL/'scripts/check_evidence.py'),'--input',str(inp),'--output',str(Path(td)/'out')]
   self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,1)
   self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,2)
   self.assertEqual(inp.read_bytes(),before)
   self.assertEqual(len(json.loads((Path(td)/'out/source-checks.json').read_text())['results']),12)
 def test_valid_input_exit_zero(self):
  with tempfile.TemporaryDirectory() as td:
   d=copy.deepcopy(DATA);d['cases']=[d['cases'][8]]
   inp=Path(td)/'input.json';inp.write_text(json.dumps(d))
   self.assertEqual(subprocess.run([sys.executable,str(SKILL/'scripts/check_evidence.py'),'--input',str(inp),'--output',str(Path(td)/'out')],capture_output=True).returncode,0)
if __name__=='__main__':unittest.main()
