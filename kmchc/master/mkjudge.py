# -*- coding: utf-8 -*-
"""mkjudge — ★순회 결과(JSON)를 판정 일감으로 옮긴다★

  쓰임:  python3 mkjudge.py <일감이름> <문항당개수> <순회결과.json> [<순회결과.json> …]
  보기:  python3 mkjudge.py t16c 3 verify_out_a.json verify_out_b.json

  ★왜 세우는가★ — 순회 한 판이 범위 셋 × (solver·defender·factchecker) 를 돌려 지적 열~서른을
  낸다. 그것을 손으로 옮겨 적으면 ★한 판에 이백 줄★ 이고, 옮기다 빠뜨리면 그 지적은 사라진다.
  실제로 이 마디에서 지적을 손으로 옮기는 데 든 품이 조치하는 품보다 컸다.
  ▸ 순회 결과의 꼴은 정해져 있다: {범위: {solver:{answers,blocking}, defender:[…], fact:{errors,warnings}}}
    그래서 ★기계로 옮긴다★. 문면은 ★은행에서 새로 뽑는다★(낡은 검증 파일을 따라가지 않도록).

  나가는 것
    · judge_<이름>_<n>.json — 판정 에이전트가 읽는 일감(item + findings)
    · 화면에 args JSON — Workflow 에 그대로 넘긴다
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
S = '/tmp/claude-0/-home-user-exam/5f2ecfac-9847-5091-89ed-a121f3b6410f/scratchpad/'
ID = re.compile(r'M\d{5}')


def load_bank():
    d = json.load(io.open(os.path.join(HERE, 'master_bank.json'), encoding='utf-8'))
    pool = d['items'] if isinstance(d, dict) else d
    return {x['id']: x for x in pool}


def collect(paths):
    """순회 결과 여러 판을 문항별 지적 목록으로 모은다."""
    F = {}

    def add(mid, kind, option, text):
        F.setdefault(mid, []).append({'kind': kind, 'option': option, 'text': text})

    for p in paths:
        r = json.load(io.open(p if os.path.isabs(p) else S + p, encoding='utf-8'))
        r = r.get('result', r)
        for rng, blk in r.items():
            for b in (blk.get('solver') or {}).get('blocking', []):
                m = ID.search(b)
                if m:
                    add(m.group(0), 'solver차단', None, b)
            for d in blk.get('defender', []):
                sev = d.get('severity') or ''
                add(d['id'], 'defender', d.get('option'),
                    (d.get('defense') or '') + (' [심각도 %s]' % sev if sev else ''))
            fact = blk.get('fact') or {}
            for e in fact.get('errors', []):
                add(e['id'], 'fact✗', None,
                    '문장: %s / 틀린 까닭: %s / 권고: %s'
                    % (e.get('sentence', ''), e.get('wrong', ''), e.get('fix', '')))
            for w in fact.get('warnings', []):
                add(w['id'], 'fact△', None,
                    '문장: %s / 지적: %s' % (w.get('sentence', ''), w.get('note', '')))
    return F


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return
    tag, per, paths = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
    by = load_bank()
    F = collect(paths)
    rows = []
    for mid in sorted(F):
        x = by.get(mid)
        if x is None:
            print('  ⚠ 은행에 없는 id — %s' % mid)
            continue
        rows.append({'item': {'id': mid, 'answer': x['answer'] + 1, 'stem': x['stem'],
                              'choices': x['choices'], 'calc': x.get('calc_check', ''),
                              'proof': x.get('answer_proof', ''),
                              'solution': x.get('solution', '')},
                     'findings': F[mid]})
    jobs = []
    for i in range(0, len(rows), per):
        ch = rows[i:i + per]
        f = S + 'judge_%s_%d.json' % (tag, i // per)
        json.dump(ch, io.open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        jobs.append({'file': f, 'ids': [r['item']['id'] for r in ch]})
    args = {'judge': jobs, 'calc': []}
    json.dump(args, io.open(S + 'args_%s.json' % tag, 'w', encoding='utf-8'), ensure_ascii=False)
    kinds = {}
    for v in F.values():
        for f in v:
            kinds[f['kind']] = kinds.get(f['kind'], 0) + 1
    print('문항 %d · 지적 %d (%s) · 일감 %d'
          % (len(rows), sum(kinds.values()),
             ' '.join('%s%d' % (k, v) for k, v in sorted(kinds.items())), len(jobs)))
    print(json.dumps(args, ensure_ascii=False))


if __name__ == '__main__':
    main()
