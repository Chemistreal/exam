#!/usr/bin/env python3
"""**모든 시험에 기준 기록(연도누적 인원)이 들어 있는지** 본다.

왜 이 자가 있나
---------------
2026-08-10, 선생님 말씀.

    "연도누적석차가 **또** 데이터가 빠진거같아"

**'또' 가 핵심이다.** 이력을 보면 이 파일은 조용히 줄어든 적이 여러 번이고,
그때마다 사람이 알아채서 되돌렸다.

    2db30bc  기준 기록을 갱신 전으로 되돌린다 (또래 정답률 10회차 복구)
    5f40a2c  기준 기록을 되돌린다 — 자동 갱신이 387명을 225명으로 깎았다
    71a2670  화올·기출동형 열두 회차 827명을 기준 기록에 넣는다

**줄어드는 것을 막는 자가 없었다.** 그래서 매번 사람이 성적표를 보다가
"인원이 이상한데" 하고 알아차렸다.

무엇이 걸리나
-------------
`cohort/baseline.json` 에 기준 기록이 없으면 석차의 모집단이 **"지금 이
브라우저에서 채점한 사람"** 만 남는다. `MINP=1` 이라 한 명만 채점해도 —

    연도누적 총석차 1/1 · 상위 0% · 백분위 100

이 숫자가 학부모에게 나간다. 틀린 게 아니라 **뜻이 없는** 숫자다.

⚠ 같은 파일의 `rankPoolYear` 는 이미 이렇게 적어 두었다 —
  *"올해 채점한 사람이 자기 혼자면 1/1 이 된다. 그건 등수가 아니라 아직
  아무도 없다는 뜻이라, 적지 않는다"* (`ready: p.length>=2`).
  **반석차는 그 규칙을 지키는데 총석차만 안 지키고 있었다.**

무엇을 보나
-----------
  ① `exams.json` 의 모든 시험이 `cohort/baseline.json` 에 있는가
     (별칭 COHORT_ALIAS 를 따라간 뒤에 본다)
  ② 기준 기록이 **줄어들지 않았는가** — 회차마다 인원을 박아 둔다.
     자동 갱신이 387명을 225명으로 깎던 그 일을 여기서 잡는다

아직 응시 기록이 **없는 것이 맞는** 시험은 `NO_COHORT` 에 까닭과 함께
적는다. 비워 두면 잊히고, 적어 두면 다음 사람이 판단할 수 있다.

    python3 tools/cohort_cover.py           # 어느 시험에 기준 기록이 없나
    python3 tools/cohort_cover.py --check   # 빠졌거나 줄었으면 빨간불
    python3 tools/cohort_cover.py --seal    # 지금 인원을 기준으로 다시 박는다
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'cohort', 'baseline.json')
EXAMS = os.path.join(ROOT, 'exams.json')
SEAL = os.path.join(ROOT, 'cohort', 'seal.json')

# 아직 응시 기록이 **없는 것이 맞는** 시험.
NO_COHORT = {
    'kmchc-2026-1-simhwa': '2026-08-10 에 들여온 심화 문제편 — 아직 응시 전',
    'kmchc-2025-2-simhwa': '같음',
    'kmchc-2025-1-simhwa': '같음',
    # 2026-08-08 에 뺐다가 2026-08-18 에 되살린 일반 회차. 뺀 동안에도
    # 응시 기록은 안 쌓였으므로 기준 기록이 없는 것이 맞다.
    'kmchc-2025-1-ilban': '2026-08-18 에 되살린 일반 문제편 — 아직 응시 전',
    'kmchc-2025-2-ilban': '같음',
    'kmchc-2026-1-ilban': '같음',
    # 2026-08-20 에 들어온 USNCO 실전 세트 — 미국 대회 기출이라 우리 학원
    # 기준 기록(성적표 엑셀)이 애초에 없다. 응시가 쌓이면 그것이 곧 모집단이다.
    'usnco-2026-natl-1': '2026-08-20 에 들여온 USNCO 세트 — 우리 쪽 응시 전',
}

# 있어야 하는데 **없는** 시험. 여기 적힌 것은 빨간불을 내지 않지만 매번 보인다.
#
# ⚠ 왜 빨간불로 안 두나 — 이건 **엑셀이 있어야 고쳐진다.** 못 고치는 것을 매일
#   빨간불로 켜 두면 사람이 알림을 안 보게 되고, 그러면 **진짜 새로 빠진 것**도
#   같이 못 보게 된다. 초록불이 뜻하는 것은 "다 있다" 가 아니라 **"알고 있는
#   것 말고 더 빠지거나 줄어든 것은 없다"** 이다.
#   여기서 이름을 지우려면 엑셀을 받아 `gen_cohort_baseline.py` 를 돌린다.
WAITING = dict(
    # 선생님이 정하셨다(2026-08-10) — "화올 2009-2016은 엑셀없는대로 놔두고".
    # 엑셀이 없으니 만들 수 없다. **그대로 두기로 한 것**이지 잊은 것이 아니다.
    {i: '엑셀이 없다 — 그대로 두기로 정함(2026-08-10)'
     for i in ('hwol-2009', 'hwol-2010', 'hwol-2011', 'hwol-2012',
               'hwol-2013', 'hwol-2014', 'hwol-2015', 'hwol-2016')},
    # 2017~2026 은 엑셀이 있으면 다 들어가야 한다. 이 셋은 아직 못 받았다.
    **{i: '⚖ A8 — 2017~2026 인데 엑셀을 아직 못 받았다'
       for i in ('kmchc-2025-1-simhwa', 'kmchc-2025-2-simhwa',
                 'kmchc-2026-1-simhwa')},
    # 조준모의고사 0회 — 총점 40개 가운데 11개가 **3의 배수가 아니다**.
    # 문항당 3점으로 채점된 것이 아니라는 뜻이라, 3으로 나눠 맞은 문항 수를
    # 만들면 없는 등수를 지어내게 된다(tools/gen_cohort_from_seeds.py 가
    # 그래서 이 회차만 건너뛴다). 원본 채점 기준을 아는 사람이 정할 자리다.
    **{'j0': '총점이 문항당 3점으로 안 나누어떨어진다 — 채점 기준을 확인해야 한다'})


def alias_map():
    """final.html 의 COHORT_ALIAS 를 그대로 읽는다. 두 벌로 적으면 갈라진다."""
    try:
        s = open(os.path.join(ROOT, 'final.html'), encoding='utf-8').read()
    except OSError:
        return {}
    m = re.search(r'const COHORT_ALIAS=\{([^}]*)\}', s)
    if not m:
        return {}
    return dict(re.findall(r"'([^']+)'\s*:\s*'([^']+)'", m.group(1)))


def load():
    ex = json.loads(open(EXAMS, encoding='utf-8').read())
    lst = ex if isinstance(ex, list) else ex.get('exams', ex)
    base = json.loads(open(BASE, encoding='utf-8').read()).get('exams', {})
    return lst, base


def counts(base):
    """회차별 인원. hist 의 합을 쓴다 — n 만 믿으면 hist 가 비어도 안 걸린다."""
    out = {}
    for k, v in base.items():
        h = (v or {}).get('hist') or {}
        out[k] = sum(int(c) for c in h.values())
    return out


def rate_only(base):
    """정답률만 있고 석차 모집단은 없는 회차.

    엑셀이 없어도 **또래 정답률**은 세울 수 있다 — 그 회차 정답률과 응시 인원이
    등기에 있으면 문항별 정답자 수가 나온다(tools/ingest_legacy_exam.py).
    하지만 석차·백분위는 «몇 점이 몇 명인가»(hist)가 있어야 하고 그것은 엑셀에만
    있다. 반쪽인 것을 온전한 것으로 세면 «있다» 고 잘못 읽힌다 — 따로 센다."""
    return sorted(k for k, v in base.items()
                  if (v or {}).get('qc') and not (v or {}).get('hist'))


def main():
    check = '--check' in sys.argv
    seal = '--seal' in sys.argv
    lst, base = load()
    ali = alias_map()
    now = counts(base)

    missing = []
    for e in lst:
        i = e.get('id')
        k = ali.get(i, i)
        if k in base:
            continue
        missing.append((i, NO_COHORT.get(i)))

    known = [m for m in missing if m[1]]
    waiting = [(i, WAITING[i]) for i, _ in missing if i in WAITING]
    unknown = [m for m in missing if not m[1] and m[0] not in WAITING]

    print('시험 %d개 · 기준 기록 %d개 · 응시 인원 합 %d명'
          % (len(lst), len(base), sum(now.values())))

    # 회차마다 몇 명인지 눈으로 볼 수 있게 적는다. 합계만 적으면 한 회차가
    # 통째로 얇아도 안 보인다 — 그게 이번에 걸린 자리다.
    if not check:
        title = {e.get('id'): (e.get('title') or e.get('id')) for e in lst}
        rows = []
        for e in lst:
            i = e.get('id')
            k = ali.get(i, i)
            if k in base:
                rows.append((now.get(k, 0), i, title.get(i)))
        print('\n회차별 인원 (적은 순 — 얇은 곳이 위로 온다)')
        for n, i, t in sorted(rows):
            mark = '  ← 얇다' if n < 10 else ''
            print('  %5d명  %-22s %s%s' % (n, i, t, mark))

    half = rate_only(base)
    if half:
        print('\n또래 정답률만 있는 시험 %d개 — 석차·백분위는 아직 이 브라우저 기준이다'
              % len(half))
        for k in half:
            print('  %-24s 응시 %s명 · 문항별 정답률 있음 · hist 없음'
                  % (k, (base.get(k) or {}).get('n', '?')))
        print('  → 성적표 엑셀을 받으면 tools/gen_cohort_baseline.py 가 채운다.')

    if known:
        print('\n아직 응시 전이라 없는 것이 맞는 시험 %d개' % len(known))
        for i, why in known:
            print('  %-24s %s' % (i, why))

    if waiting:
        print('\n⚠ 있어야 하는데 **없는** 시험 %d개 — 그 회차는 석차 모집단이'
              % len(waiting))
        print('  "지금 이 브라우저에서 채점한 사람" 뿐이다.')
        for i, why in waiting:
            print('  %-24s %s' % (i, why))
        print('  → 성적표 엑셀을 받아 `python3 tools/gen_cohort_baseline.py` 를 돌린다.')

    bad = []
    if unknown:
        bad.append('기준 기록이 **없는** 시험 %d개 — 그 회차는 석차 모집단이 '
                   '"지금 이 브라우저에서 채점한 사람" 뿐이다:\n    '
                   % len(unknown) + '\n    '.join(i for i, _ in unknown))

    # ② 줄어들지 않았는가
    if seal:
        os.makedirs(os.path.dirname(SEAL), exist_ok=True)
        open(SEAL, 'w', encoding='utf-8').write(
            json.dumps({'note': '회차별 응시 인원. 줄어들면 빨간불이다.',
                        'counts': now}, ensure_ascii=False, indent=1) + '\n')
        print('\n지금 인원을 박았다 — %s' % os.path.relpath(SEAL, ROOT))
        return 0

    if os.path.exists(SEAL):
        was = json.loads(open(SEAL, encoding='utf-8').read()).get('counts', {})
        shrunk = [(k, was[k], now.get(k, 0)) for k in was
                  if now.get(k, 0) < was[k]]
        if shrunk:
            bad.append('기준 기록이 **줄었다** %d곳 — 자동 갱신이 387명을 225명으로 '
                       '깎던 그 일이다:\n    ' % len(shrunk)
                       + '\n    '.join('%s  %d명 → %d명' % r for r in shrunk))
        gained = [(k, was.get(k, 0), now[k]) for k in now if now[k] > was.get(k, 0)]
        if gained and not check:
            print('\n늘어난 곳 %d (늘어나는 것은 막지 않는다)' % len(gained))
            for k, a, b in gained[:6]:
                print('  %-24s %d명 → %d명' % (k, a, b))
    else:
        print('\n※ 인원을 박아 둔 파일이 없다 — `--seal` 로 한 번 박아 두면')
        print('  그 뒤로 줄어드는 것을 막는다.')

    if bad:
        print('\n' + '\n'.join('⚠ ' + b for b in bad))
        print('\n기준 기록은 성적표 엑셀에서만 나온다(tools/gen_cohort_baseline.py).')
        print('엑셀이 없으면 만들 수 없다 — 선생님께 그 회차 파일을 받아야 한다.')
        if check:
            print('\nFAIL')
            return 1
        return 0

    # 초록불이 "다 있다" 로 읽히면 안 된다. 기다리는 것이 남아 있으면 그렇게 말한다.
    if waiting:
        print('\n알고 있는 %d개 말고 **새로 빠지거나 줄어든 곳은 없다.**'
              % len(waiting))
        print('(초록불은 "다 있다" 가 아니라 "더 나빠지지 않았다" 는 뜻이다)')
    else:
        print('\n모든 시험에 기준 기록이 있고, 줄어든 곳이 없다.')
    if check:
        print('PASS')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
