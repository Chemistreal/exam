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

    python3 tools/gen_chunks.py [--out <폴더>] [--only twin|mis|lec|crop|thin]

만드는 것
    twinsrc/<시험>__<범위>.json   동형문제 집필용 — 원문 지문·선지·정답·개념·해설
    twinsrc/j0-haeseol.txt        j0 는 지문이 없어 해설 PDF 를 글로 뽑아 함께 둔다
    misrc/<시험>__m<n>.json       선지별 오답 해설용 — 아직 안 채운 문항만
    lecsrc/L<nn>.json             유형→강의 배선용 — 유형마다 단원·개념·문항 조각
    lecsrc/lectures.txt           강의 125편의 «파일이름<탭>제목»
    cropsrc/<시험>__c<n>.json     크롭에서 지문·선지를 옮길 때 — 정답·개념·해설만
    thinsrc/<시험>__<범위>.json   많이 틀렸는데 해설이 얇은 문항 — 증보용
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


# 채울 수 없다고 확인된 문항(시험지에 선지가 인쇄돼 있지 않다). 목록은
# crop_cut.py 가 가진다 — 여기서 다시 적으면 두 곳이 갈라진다.
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from crop_cut import KNOWN as CANNOT
except Exception:                                    # 자가 없으면 아무것도 안 뺀다
    CANNOT = frozenset()


def build_crop(out):
    """크롭은 있는데 **선지별 오답 해설이 없는** 회차.

    ⚠ 예전에는 「지문·선지가 없는 회차」로 골랐다. 두 군데가 어긋났다.

      · 집필 일꾼은 이제 지문·선지를 옮겨 적지 않는다(2026-09-05). 옮겨
        적어서 얻는 것은 없고 새 오류만 났다 — 문항은 크롭 원문이 보여 준다.
        그러니 「선지가 채워졌는가」로는 일이 끝난 줄을 영영 모른다.
      · 시험지에 **선지가 인쇄돼 있지 않은** 문항이 있다(kch1to2·kch1to2-b
        각 넷). 그 회차는 선지 수가 절대 nQ 에 못 미쳐, 다 끝난 뒤에도
        같은 조각을 계속 다시 내보냈다.

    그래서 「오답 해설이 있는가」로 세고, 채울 수 없다고 확인된 문항은
    crop_cut.py 의 목록을 빌려 뺀다 — 두 곳에 같은 목록을 두지 않는다.
    """
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
        if not qs:
            continue
        done = sum(1 for k, v in qs.items()
                   if v.get('misconceptions') or v.get('excluded')
                   or (eid, int(k)) in CANNOT)
        if done >= n:
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
    print('cropsrc %d덩어리 (크롭은 있는데 선지별 오답 해설이 없는 회차)' % len(keys))
    return keys


# ── 증보 대상: 많이 틀렸는데 해설이 얇은 문항 ──────────────────────────
# 왜 이 두 조건인가. 「해설이 짧다」만 보면 564문항이 걸리는데, 그 대부분은
# 한 줄로 끝나는 것이 맞는 쉬운 문항이다. 「많이 틀렸다」만 보면 이미 두꺼운
# 해설이 딸린 어려운 문항까지 들어온다. 고쳐야 하는 것은 **겹치는 자리** 다 —
# 절반 넘게 틀렸는데 해설은 메모 한 줄인 문항.
#
# ⚠ 응시 8명 미만인 회차는 뺀다. MINP 는 선생님 결정으로 1이지만(적은 인원도
#   보여 달라), **여기서 쓰는 것은 화면에 보여 줄 값이 아니라 「어느 문항을
#   고칠까」 를 정하는 값**이다. 한 사람이 틀린 것을 정답률 0% 라고 읽으면
#   엉뚱한 문항 열한 개가 목록 맨 위에 올라온다(kmchc-2024-2 가 그랬다).
THIN_MIN_N = 8       # 이만큼은 응시해야 정답률로 친다
THIN_MAX_RATE = 0.5  # 절반 넘게 틀린 문항
THIN_MAX_LEN = 150   # 해설이 이보다 짧으면 «메모» 로 본다


def build_thin(out):
    d = os.path.join(out, 'thinsrc')
    base = load(os.path.join(ROOT, 'cohort', 'baseline.json')).get('exams') or {}
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))):
        eid = os.path.basename(f)[:-5]
        if eid.startswith('_'):
            continue
        b = base.get(eid) or {}
        qc, n = b.get('qc') or [], b.get('n') or 0
        if not qc or n < THIN_MIN_N:
            continue
        qs = load(f).get('questions') or {}
        for k, q in qs.items():
            no = int(k)
            if not (1 <= no <= len(qc)):
                continue
            rate = qc[no - 1] / n
            if rate >= THIN_MAX_RATE:
                continue
            if len((q.get('explanation') or '').strip()) >= THIN_MAX_LEN:
                continue
            rows.append((eid, no, rate, q))
    by = collections.defaultdict(list)
    for eid, no, rate, q in rows:
        by[eid].append((no, rate, q))
    keys = []
    for eid, part in by.items():
        part.sort()
        for i in range(0, len(part), 10):
            grp = part[i:i + 10]
            key = '%s__%02d-%02d' % (eid, grp[0][0], grp[-1][0])
            body = {}
            for no, rate, q in grp:
                one = {k: q[k] for k in KEEP_MIS + ('misconceptions', 'learningPoint',
                                                    'reviewNote') if q.get(k) is not None}
                one['_정답률'] = '%d%%' % round(rate * 100)
                one['_크롭'] = 'crops/%s/%d.png' % (eid, no)
                body[str(no)] = one
            dump({'exam': eid, 'questions': body}, os.path.join(d, key + '.json'))
            keys.append(key)
    keys.sort()
    print('thinsrc %d덩어리 · %d문항' % (len(keys), len(rows)))
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
                     ('lec', build_lec), ('crop', build_crop),
                     ('thin', build_thin)):
        if only and only != name:
            continue
        made[name] = fn(out)
    dump(made, os.path.join(out, 'keys.json'))
    print('\n%s 에 만들었다. 목록은 keys.json.' % out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
