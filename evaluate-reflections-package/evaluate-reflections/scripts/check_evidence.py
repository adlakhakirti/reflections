#!/usr/bin/env python3
"""Offline source-integrity checks. No model calls; semantic support is not scored."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def require(test, message):
    if not test:
        raise ValueError(message)


def evaluate(data):
    require(isinstance(data, dict) and data.get('schema_version') == 1, 'schema_version must be 1')
    require(isinstance(data.get('provenance'), str) and data['provenance'].strip(), 'provenance required')
    cases = data.get('cases')
    require(isinstance(cases, list) and cases, 'cases must be a nonempty array')
    results, ids = [], set()
    for case in cases:
        require(isinstance(case, dict), 'case must be an object')
        cid = case.get('id')
        require(isinstance(cid, str) and cid and cid not in ids, 'case IDs must be unique nonempty strings')
        ids.add(cid)
        sessions = case.get('sessions')
        require(isinstance(sessions, list), f'{cid}: sessions must be an array')
        lookup, session_ids = {}, set()
        for session in sessions:
            require(isinstance(session, dict), f'{cid}: session must be an object')
            sid = session.get('id')
            require(isinstance(sid, str) and sid and sid not in session_ids, f'{cid}: invalid/duplicate session ID')
            session_ids.add(sid)
            require(isinstance(session.get('passages'), list), f'{cid}: passages must be an array')
            for passage in session['passages']:
                require(isinstance(passage, dict), f'{cid}: passage must be an object')
                require(all(isinstance(passage.get(k), str) and passage[k] for k in ('id','speaker','text')), f'{cid}: passage fields required')
                key = (sid, passage['id'])
                require(key not in lookup, f'{cid}: duplicate passage ID')
                lookup[key] = passage
        ref = case.get('reflection')
        require(isinstance(ref, dict) and isinstance(ref.get('claim'), str), f'{cid}: reflection claim required')
        citations, declared = ref.get('citations'), ref.get('declared_session_count')
        require(isinstance(citations, list), f'{cid}: citations must be an array')
        require(type(declared) is int and declared >= 0, f'{cid}: count must be a nonnegative integer')
        issues, seen, cited_sessions, valid_sessions = [], set(), set(), set()
        for cite in citations:
            require(isinstance(cite, dict) and all(isinstance(cite.get(k), str) and cite[k] for k in ('session_id','passage_id','quote','speaker')), f'{cid}: citation fields required')
            sid, pid = cite['session_id'], cite['passage_id']
            cited_sessions.add(sid)
            key = (sid, pid)
            if key in seen:
                issues.append({'code':'DUPLICATE_CITATION','reference':f'{sid}/{pid}'})
            seen.add(key)
            source = lookup.get(key)
            if source is None:
                issues.append({'code':'MISSING_SOURCE','reference':f'{sid}/{pid}'})
                continue
            valid = True
            if cite['quote'] not in source['text']:
                issues.append({'code':'QUOTE_MISMATCH','reference':f'{sid}/{pid}'})
                valid = False
            if cite['speaker'] != source['speaker']:
                issues.append({'code':'SPEAKER_MISMATCH','reference':f'{sid}/{pid}'})
                valid = False
            if valid:
                valid_sessions.add(sid)
        if declared != len(cited_sessions):
            issues.append({'code':'SESSION_COUNT_MISMATCH','declared':declared,'distinct_cited':len(cited_sessions)})
        if ref['claim'].strip() and not citations:
            issues.append({'code':'UNSOURCED_CLAIM'})
        if not ref['claim'].strip() and (citations or declared):
            issues.append({'code':'INCONSISTENT_ABSTENTION'})
        results.append({'case_id':cid,'source_status':'FAIL' if issues else 'PASS','issues':issues,'distinct_cited_sessions':len(cited_sessions),'source_valid_sessions':len(valid_sessions),'interpretation_status':'NOT_TESTED','revision_status':'REVIEW_REQUIRED' if 'previous_claim' in case else 'NOT_TESTED'})
    return {'provenance':data['provenance'],'scope':'Source checks only. PASS does not establish interpretation quality. No product model was called.','results':results}


def render(report):
    lines=['# Source-integrity report','',report['scope'],'',f"Input provenance: {report['provenance']}",'',f"Input SHA-256: {report['input_sha256']}",'','| Case | Source checks | Findings | Interpretation |','|---|---|---|---|']
    for r in report['results']:
        name=r['case_id'].replace('|','\\|').replace('\n',' ')
        lines.append(f"| {name} | {r['source_status']} | {', '.join(x['code'] for x in r['issues']) or 'No source-integrity issue detected'} | NOT TESTED |")
    lines += ['', 'Review the complete sessions using references/rubric.md before making a product recommendation. Passing cases may still contain overreach, missing context, or inappropriate abstention.']
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        raw=args.input.read_bytes()
        report=evaluate(json.loads(raw))
        report['input_sha256']=hashlib.sha256(raw).hexdigest()
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'source-checks.json').write_text(json.dumps(report,indent=2)+'\n')
        (args.output/'source-checks.md').write_text(render(report))
        failed=sum(r['source_status']=='FAIL' for r in report['results'])
        print(f"{len(report['results'])} cases; {failed} failed source checks. Interpretation: NOT TESTED. Reports: {args.output}")
        return 1 if failed else 0
    except (ValueError,OSError,TypeError) as exc:
        print(f'Input/output error: {exc}',file=sys.stderr)
        return 2

if __name__=='__main__':
    sys.exit(main())
