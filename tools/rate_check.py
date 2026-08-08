#!/usr/bin/env python3
"""문제지에 적혀 있던 **공식 정답률**이 성한지 본다 — `exams.json` 의 `rate`.

응시 기록이 얼마 없는 회차는 문항 난이도를 짐작해야 한다. 여태는 다른 회차의
같은 영역 평균으로 짐작했다 — '산화환원 문항은 대체로 이쯤' 이라는 뭉뚱그린
값이라, 그 회차에서 유난히 어려웠던 문항도 평범하게 나왔다.

화올 문제지 원본(HWP)에는 문항마다 실제 정답률이 적혀 있다. 전국 응시자가
실제로 푼 결과라, 있으면 짐작할 까닭이 없다. 그것을 뽑아 `rate` 로 적어 두었다.

    hwol-2013  58/60문항 · 평균 49% · 최저 14%
    hwol-2018  58/60문항 · 평균 59% · 최저  8%

원본 문제지는 대회 문제라 저장소에 두지 않는다(tools/hwp_text.py 주석 참고).
그래서 이 값은 **다시 만들 수 없다** — 지우거나 어긋나면 되돌릴 길이 없다.
여기서 지킨다.

  ① 길이가 문항 수와 같은가
  ② 0~100 안에 드는가
  ③ 한 회차라도 통째로 사라지지 않았는가(회차 수 바닥값)

    python3 tools/rate_check.py           # 회차별로 얼마나 있는지
    python3 tools/rate_check.py --check   # 어긋나면 빨간불
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMS = os.path.join(ROOT, 'exams.json')

# 정답률을 담은 회차 수의 바닥값. 늘면 여기도 올린다 — 올려야 사라진 것을 안다.
FLOOR = 6
MIN_FILL = 0.8      # 문항의 이만큼은 값이 있어야 쓸모가 있다


def main():
    check = '--check' in sys.argv
    rounds = json.load(open(EXAMS, encoding='utf-8'))
    bad, have = [], []
    for ex in rounds:
        r = ex.get('rate')
        if r is None:
            continue
        eid, nQ = ex['id'], int(ex['nQ'])
        have.append(eid)
        if len(r) != nQ:
            bad.append('%s: 길이 %d — 문항 수 %d 와 다르다' % (eid, len(r), nQ))
            continue
        vals = [v for v in r if v is not None]
        out = [v for v in vals if not (isinstance(v, int) and 0 <= v <= 100)]
        if out:
            bad.append('%s: 0~100 밖의 값 %s' % (eid, out[:5]))
        if len(vals) < nQ * MIN_FILL:
            bad.append('%s: 값이 있는 문항 %d/%d — 너무 적다' % (eid, len(vals), nQ))
        if vals:
            print('  %-22s %2d/%d문항 · 평균 %2.0f%% · 최저 %2d%% · 최고 %2d%%'
                  % (eid, len(vals), nQ, sum(vals) / len(vals), min(vals), max(vals)))

    print('\n공식 정답률을 담은 회차 %d개 (바닥값 %d)' % (len(have), FLOOR))
    if len(have) < FLOOR:
        bad.append('회차가 %d개로 줄었다 — 바닥값은 %d 다. 원본 문제지가 저장소에 '
                   '없어 다시 만들 수 없는 값이다.' % (len(have), FLOOR))

    if bad:
        print('\n어긋난 곳 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        return 1 if check else 0

    print('정답률 자료가 성하다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
