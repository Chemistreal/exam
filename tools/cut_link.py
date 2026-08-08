#!/usr/bin/env python3
"""늦춘 기준이 **시험지**를 보고 늦춘 것인지, 그 회차 **사람들**을 보고 늦춘 것인지.

`gen_cut_adj.py` 는 회차별 수상 비율을 견주어 낮은 쪽을 늦춘다. 그런데 그
비율은 시험지 난이도와 응시자 실력이 섞인 값이다. 11회 수상률이 0% 인 것이
시험지가 어려워서인지, 그날 본 열여섯 명이 약했던 것인지 비율만으로는 갈리지
않는다. 뒤엣것이라면 늦추는 것은 보상이 아니라 봐주기다.

가를 수 있다. 여러 회차를 본 학생이 있기 때문이다 — 같은 사람이 4회에서 73%,
11회에서 45% 를 받았다면 그 28%p 는 사람이 아니라 시험지 몫이다. 기록을

    점수 = 그 학생의 실력 + 그 시험지의 난이도

로 놓고 교대최소제곱으로 둘을 떼어 낸다(공통응시자 연결, common-person
equating). 난이도만 남으면 응시자 구성이 달라도 회차끼리 견줄 수 있다.

실제로 떼어 보면 하나가 크게 바뀐다.

    jmchc-4   날평균 73% (가장 쉬워 보임)  →  보정 +4.2%p (-9.3%p)

4회가 쉬웠던 것이 아니라 그 다섯 명이 잘하는 학생이었다. 반대로 늦춘 여섯
회차는 보정한 뒤에도 여전히 아래쪽에 남는다 — 시험지가 어려웠던 것이 맞다.

**여기서 컷을 바꾸지 않는다.** `gen_cut_adj.py` 가 낸 값이 사람이 아니라
시험지를 따라갔는지 되짚어 보는 자리다. 어긋나면 알린다.

기준 기록(cohort/baseline.json)은 점수별 사람 수만 있고 누가 무엇을 봤는지가
없어 연결에 쓸 수 없다. 연결은 backup/ 의 채점 기록으로 한다 — 학생 이름은
없고 익명 코드만 있다.

    python3 tools/cut_link.py           # 회차별 난이도(능력 보정)를 보여 준다
    python3 tools/cut_link.py --check   # 늦춘 회차가 실은 안 어려웠으면 알린다
"""
import collections
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMS = os.path.join(ROOT, 'exams.json')
BASE = os.path.join(ROOT, 'cohort', 'baseline.json')

MIN_LINK = 3      # 이 회차를 본 사람 중 다른 회차도 본 사람이 이만큼은 있어야 연결이 선다
MIN_N = 5         # 응시가 이보다 적으면 난이도가 사람 한 명에 흔들린다
ROUNDS = 500      # 교대최소제곱 반복. 이 크기에서는 수십 번이면 굳는다
TOL = 0.03        # 늦췄는데 평균보다 이만큼 쉬우면 어긋난 것으로 본다


def load_records():
    """backup/ 에서 (코드, 회차명, 점수비율) 을 모은다.

    backup/ 은 같은 시트를 날마다 뜬 것이라 파일끼리 겹친다. (코드, 회차) 로
    묶어 가장 나중 것만 남긴다 — 안 그러면 한 사람이 닷새치로 세어져 그
    학생의 실력이 다섯 배 무겁게 반영된다.
    """
    last = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'backup', '*.json'))):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for r in (d.get('rows') or d.get('records') or []):
            if not isinstance(r, dict) or not r.get('max') or not r.get('exam'):
                continue
            key = (r.get('code'), r['exam'])
            if not key[0]:
                continue
            last[key] = (r.get('saved') or '', r['correct'] / r['max'])
    return [(c, e, p) for (c, e), (_, p) in last.items()]


def fit(rec):
    """점수 = 실력 + 난이도 로 놓고 교대최소제곱. 난이도는 평균 0 으로 맞춘다."""
    codes = sorted({c for c, _, _ in rec})
    exams = sorted({e for _, e, _ in rec})
    ability = {c: 0.0 for c in codes}
    diff = {e: 0.0 for e in exams}
    by_c = collections.defaultdict(list)
    by_e = collections.defaultdict(list)
    for c, e, p in rec:
        by_c[c].append((e, p))
        by_e[e].append((c, p))
    for _ in range(ROUNDS):
        for c in codes:
            ability[c] = statistics.mean(p - diff[e] for e, p in by_c[c])
        for e in exams:
            diff[e] = statistics.mean(p - ability[c] for c, p in by_e[e])
        m = statistics.mean(diff.values())
        for e in exams:
            diff[e] -= m
    return ability, diff, by_e


def main():
    check = '--check' in sys.argv
    rec = load_records()
    if not rec:
        print('backup/ 에 채점 기록이 없다 — 연결할 것이 없다.')
        return 0

    rounds = json.load(open(EXAMS, encoding='utf-8'))
    by_title = {e.get('title'): e for e in rounds}
    _, diff, by_e = fit(rec)
    raw = {e: statistics.mean(p for _, p in v) for e, v in by_e.items()}
    raw_mid = statistics.mean(raw.values())

    # 여러 회차를 본 사람이 몇인지 — 적으면 그 회차의 난이도는 아직 못 믿는다
    span = collections.Counter()
    for c, _, _ in rec:
        span[c] += 1
    linked = {e: sum(1 for c, _ in v if span[c] > 1) for e, v in by_e.items()}

    print('시험지 난이도 — 응시자 실력을 빼고 (%d명 · %d회차)\n'
          % (len({c for c, _, _ in rec}), len(by_e)))
    print('  %-22s %5s %8s %8s %6s' % ('회차', '응시', '날평균', '능력보정', '늦춤'))
    bad = []
    for e in sorted(by_e, key=lambda x: diff[x]):
        ex = by_title.get(e)
        adj = int((ex or {}).get('cutAdj') or 0)
        n, lk = len(by_e[e]), linked[e]
        weak = n < MIN_N or lk < MIN_LINK
        print('  %-22s %4d명 %5.0f%% %+7.1f%%p %5s%s'
              % (e, n, raw[e] * 100, diff[e] * 100, ('+%d' % adj) if adj else '·',
                 '   (연결 얇음)' if weak else ''))
        if adj and not weak and diff[e] > TOL:
            bad.append((e, adj, diff[e]))

    print('\n  · 능력보정이 음수면 그 시험지가 어렵다는 뜻이다(평균 0).')
    print('  · 날평균과 크게 어긋나는 회차는 시험지가 아니라 응시자가 달랐던 것이다.')

    missing = [ex['id'] for ex in rounds
               if not (json.load(open(BASE, encoding='utf-8')).get('exams') or {}).get(ex['id'])]
    if missing:
        print('\n기준 기록이 아예 없는 회차 %d개 — 컷을 재어 볼 길이 없다.' % len(missing))
        print('  ' + ', '.join(missing))
        print('  이 회차들의 수상 확률은 "비슷한 난이도의 실전이라면" 이라는 가정 위에 선다.')

    if bad:
        print('\n늦췄는데 실은 어렵지 않았던 회차 %d개:' % len(bad))
        for e, adj, d in bad:
            print('  %-22s %d문항 늦춤 · 능력보정 %+.1f%%p (평균보다 쉽다)' % (e, adj, d * 100))
        print('수상률이 낮았던 것은 시험지가 아니라 그날 응시자 때문일 수 있다.')
        return 1 if check else 0

    print('\n늦춘 회차는 모두 능력을 빼고도 어렵다 — 사람이 아니라 시험지를 따라갔다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
