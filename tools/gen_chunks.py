#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""집필 에이전트에게 건네줄 **재료 묶음**을 저장소에서 다시 만들어 낸다.

왜 도구로 두나
--------------
동형문제·선지별 오답 해설·개념강의 배선을 집필할 때, 에이전트마다 열 문항 남짓씩
끊어 건넨다. 그 묶음은 answers/·exams.json·crops/ 에서 뽑아낸 것이라 언제든 다시
만들 수 있는데, 처음에는 그때그때 손으로 만들어 임시 폴더에 두었다.

컨테이너가 재시작되면 임시 폴더가 통째로 사라진다. **세 번 겪었다.** 그때마다
같은 코드를 다시 쳤고, 칠 때마다 조금씩 달라져서 「같은 재료로 다시 돌린다」는
말이 사실이 아니게 됐다. 만드는 법을 코드로 남겨 둔다.

    python3 tools/gen_chunks.py [--out <폴더>] [--only twin|mis|lec|crop]

만드는 것
    twinsrc/<시험>__<범위>.json   동형문제 집필용 — 원문 지문·선지·정답·개념·해설
    twinsrc/j0-haeseol.txt        j0 는 지문이 없어 해설 PDF 를 글로 뽑아 함께 둔다
    misrc/<시험>__m<n>.json       선지별 오답 해설용 — 아직 안 채운 문항만
    lecsrc/L<nn>.json             유형→강의 배선용 — 유형마다 단원·개념·문항 조각
    lecsrc/lectures.txt           강의 125편의 «파일이름<탭>제목»
    cropsrc/<시험>__c<n>.json     크롭에서 지문·선지를 옮길 때 — 정답·개념·해설만
"""
import collections
import glob
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(
    '/tmp/claude-0/-home-user-study64-report',
    '2113474c-4485-592e-912d-e7d09ec51ec8', 'scratchpad')
# 지금 집필 중인 회차. 여기 있는 것만 재료를 만든다.
ACTIVE = ['kch1u1', 'kch1to2', 'kch1to2-b', 'kch1to3', 'kch1to3-b',
          'chem2-1', 'kch2to3', 'kch2final', 'j0']
KEEP_TWIN = ('stem', 'choices', 'answer', 'concept', 'area',
             'explanation', 'misconception', 'learningPoint', 'sourceSolution')
KEEP_MIS = ('stem', 'choices', 'answer', 'acceptableAnswers',
            'concept', 'area', 'explanation', 'misconception')


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def dump(obj, p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8').write(
        json.dumps(obj, ensure_ascii=False, indent=1) + '\n')


def answers(eid):
    p = os.path.join(ROOT, 'answers', '%s.json' % eid)
    return (load(p).get('questions') or {}) if os.path.exists(p) else {}


def build_twin(out):
    ex = {e['id']: e for e in load(os.path.join(ROOT, 'exams.json'))}
    keys = []
    for eid in ACTIVE:
        items = sorted(answers(eid).items(), key=lambda kv: int(kv[0]))
        for i in range(0, len(items), 10):
            ch = items[i:i + 10]
            name = '%s__%02d-%02d' % (eid, int(ch[0][0]), int(ch[-1][0]))
            dump({'examId': eid, 'examTitle': ex[eid].get('title', ''),
                  'group': ex[eid].get('group', ''),
                  'questions': {k: {f: q[f] for f in KEEP_TWIN if q.get(f)}
                                for k, q in ch}},
                 os.path.join(out, 'twinsrc', name + '.json'))
            keys.append(name)
    # j0 는 답지에 지문이 없다. 해설 PDF 를 글로 뽑아 함께 둔다.
    pdf = os.path.join(ROOT, 'haeseol-j0.pdf')
    txt = os.path.join(out, 'twinsrc', 'j0-haeseol.txt')
    if os.path.exists(pdf):
        try:
            subprocess.run(['pdftotext', '-layout', pdf, txt], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            body = io.open(txt, encoding='utf-8').read()
            marks = [(m.start(), int(m.group(1)))
                     for m in re.finditer(r'^\s*문제\s+(\d+)\s*·', body, re.M)]
            for i, (pos, n) in enumerate(marks):
                end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
                dump_txt = os.path.join(out, 'twinsrc', 'j0q', '%02d.txt' % n)
                os.makedirs(os.path.dirname(dump_txt), exist_ok=True)
                io.open(dump_txt, 'w', encoding='utf-8').write(body[pos:end])
            for a in range(1, 61, 10):
                parts = []
                for n in range(a, a + 10):
                    q = os.path.join(out, 'twinsrc', 'j0q', '%02d.txt' % n)
                    if os.path.exists(q):
                        parts.append('\n\n===== 문항 %d =====\n' % n
                                     + io.open(q, encoding='utf-8').read())
                io.open(os.path.join(out, 'twinsrc', 'j0q',
                                     'blk-%02d-%02d.txt' % (a, a + 9)),
                        'w', encoding='utf-8').write(''.join(parts))
        except Exception as e:              # pdftotext 가 없을 수도 있다
            print('  (j0 해설 텍스트를 못 만들었다: %s)' % e)
    print('twinsrc %d덩어리' % len(keys))
    return keys


def build_mis(out):
    keys = []
    for eid in ACTIVE:
        items = [(k, q) for k, q in sorted(answers(eid).items(),
                                           key=lambda kv: int(kv[0]))
                 if q.get('choices') and not q.get('misconceptions')]
        for i in range(0, len(items), 15):
            ch = items[i:i + 15]
            name = '%s__m%d' % (eid, i // 15 + 1)
            dump({'examId': eid,
                  'questions': {k: {f: q[f] for f in KEEP_MIS if q.get(f)}
                                for k, q in ch}},
                 os.path.join(out, 'misrc', name + '.json'))
            keys.append(name)
    print('misrc %d덩어리 (아직 안 채운 문항만)' % len(keys))
    return keys


def build_lec(out):
    xs = load(os.path.join(ROOT, 'exams.json'))
    ans = {e['id']: answers(e['id']) for e in xs}
    info = collections.defaultdict(
        lambda: {'n': 0, 'areas': collections.Counter(),
                 'concepts': collections.Counter(), 'ex': []})
    for e in xs:
        A, T = e.get('area') or [], e.get('type') or []
        for i in range(e.get('nQ') or 0):
            t = (T[i] if i < len(T) else '') or ''
            a = (A[i] if i < len(A) else '') or ''
            if not t.strip():
                continue
            r = info[t.strip()]
            r['n'] += 1
            r['areas'][a.strip()] += 1
            q = (ans.get(e['id']) or {}).get(str(i + 1)) or {}
            if q.get('concept'):
                r['concepts'][q['concept']] += 1
            if len(r['ex']) < 2:
                sn = (q.get('stem') or '')[:180] or (q.get('explanation') or '')[:180]
                if sn:
                    r['ex'].append(sn)
    rows = [{'type': t, 'n': info[t]['n'],
             'areas': [a for a, _ in info[t]['areas'].most_common(4)],
             'concepts': [c for c, _ in info[t]['concepts'].most_common(3)],
             'ex': info[t]['ex']}
            for t in sorted(info, key=lambda x: (-info[x]['n'], x))]
    keys = []
    for i in range(0, len(rows), 45):
        k = 'L%02d' % (i // 45 + 1)
        dump(rows[i:i + 45], os.path.join(out, 'lecsrc', k + '.json'))
        keys.append(k)
    s = io.open(os.path.join(ROOT, 'final.html'), encoding='utf-8').read()
    m = re.search(r'const LECLIST=(\[.*?\]);\n', s, re.S)
    lst = json.loads(m.group(1))
    os.makedirs(os.path.join(out, 'lecsrc'), exist_ok=True)
    io.open(os.path.join(out, 'lecsrc', 'lectures.txt'), 'w', encoding='utf-8').write(
        '\n'.join('%s\t%s' % (a, b) for a, b in lst) + '\n')
    print('lecsrc %d덩어리 · 유형 %d종 · 강의 %d편' % (len(keys), len(rows), len(lst)))
    return keys


def build_crop(out):
    """크롭은 있는데 답지에 지문·선지가 없는 회차."""
    xs = {e['id']: e for e in load(os.path.join(ROOT, 'exams.json'))}
    keys = []
    for eid, e in sorted(xs.items()):
        n = e['nQ']
        d = os.path.join(ROOT, 'crops', eid)
        if not os.path.isdir(d):
            continue
        if not all(os.path.exists(os.path.join(d, '%d.png' % q))
                   for q in range(1, n + 1)):
            continue
        qs = answers(eid)
        if not qs or sum(1 for v in qs.values() if v.get('choices')) >= n:
            continue
        for i in range(1, n + 1, 10):
            rng = [str(q) for q in range(i, min(i + 10, n + 1))]
            name = '%s__c%02d' % (eid, i)
            dump({'examId': eid, 'examTitle': e.get('title', ''),
                  'group': e.get('group', ''),
                  'cropDir': os.path.join(ROOT, 'crops', eid),
                  'solPage': (os.path.join(ROOT, 'sol-final-%s.html' % eid)
                              if e.get('solFull') else ''),
                  'questions': {q: {'answer': qs[q].get('answer'),
                                    'acceptableAnswers': qs[q].get('acceptableAnswers'),
                                    'area': qs[q].get('area'),
                                    'concept': qs[q].get('concept'),
                                    'explanation': (qs[q].get('explanation') or '')[:900],
                                    'misconception': qs[q].get('misconception')}
                                for q in rng if q in qs}},
                 os.path.join(out, 'cropsrc', name + '.json'))
            keys.append(name)
    print('cropsrc %d덩어리 (크롭은 있는데 답지에 원문이 없는 회차)' % len(keys))
    return keys


def main():
    out = DEFAULT_OUT
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
    only = None
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1]
    made = {}
    for name, fn in (('twin', build_twin), ('mis', build_mis),
                     ('lec', build_lec), ('crop', build_crop)):
        if only and only != name:
            continue
        made[name] = fn(out)
    dump(made, os.path.join(out, 'keys.json'))
    print('\n%s 에 만들었다. 목록은 keys.json.' % out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
