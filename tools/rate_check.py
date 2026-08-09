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
  ④ **자리가 맞는가** — 빈칸이 폐기 문항 위에 있는가

넷째가 늦게 왔다. 여덟 회차의 정답률이 **한 칸씩 밀려 있었다**(2026-08-09).
1번 자리에 2번 값이 앉아 있었고, 그 뒤로 예순 문항이 통째로 어긋났다.
셋을 다 통과했다 — 길이도 60, 값도 0~100, 회차도 열 개였으니까.

    hwol-2018 크롭  1번 86% · 2번 79% · 3번 74% · 60번 15%
    exams.json      [79, 74, 73, …, 15, 86]   ← 왼쪽으로 한 칸 굴러 있었다

자리를 잴 방법이 있었다. **폐기된 문항에는 정답률이 인쇄되지 않는다** —
원본이 그 칸에 '삭제처리' 라고 적는다. 그러니 빈칸은 폐기 문항 위에 있어야
한다. 밀린 자료에서는 hwol-2018 의 빈칸이 25·33번에 있었고 폐기 문항은
34번이었다 — 한 칸 밀면 26·34 로 맞는다. 그 한 줄이면 잡혔다.

밀린 것을 바로잡으면서 폐기 문항 둘을 새로 찾았다. hwol-2014 57번은 문제지가
'정답률 : 삭제처리' 라고 인쇄하고 있었고, hwol-2015 20번은 답지에 삭제처리로
적혀 있었다. 둘 다 전원정답으로만 처리돼 있어 성적표가 '복수정답' 이라고
말하고 있었다 — 이제 '출제 취소' 라고 말한다.

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

# 폐기도 아닌데 원본에 정답률이 안 적혀 있는 자리. 사람이 크롭을 열어 보고
# 적는다 — 비워 두면 넷째 자가 아무것도 못 막는다.
#
#   hwol-2013 31번   문제지에 '정답률' 줄 자체가 없다(반응 차수, 정상 문항)
#   hwol-2017 27·60번 이 회차는 문제지가 '정답률 :  %' 로 숫자 없이 인쇄돼
#                    있다. 60번은 원본 채점표에서 전원정답이지만 '문제삭제'
#                    라고는 적혀 있지 않아 폐기로 넣지 않았다
HOLES = {
    'hwol-2013': {31},
    'hwol-2017': {27, 60},
}


def align_bad(eid, rate, voided):
    """자리가 어긋났으면 까닭을 적어 돌려준다. 성하면 빈 목록.

    `tools/lie_check.py` 가 이 함수를 그대로 불러 참·거짓 예시를 맞힌다 —
    규칙을 저기에 베껴 두면 자를 고쳐도 옛 규칙이 초록불을 준다.
    """
    out = []
    void = set(voided or [])
    holes = {i + 1 for i, v in enumerate(rate) if v is None}
    stray = sorted(holes - void - HOLES.get(eid, set()))
    if stray:
        out.append('%s: 폐기 문항이 아닌데 정답률이 빈 자리 %s — 자리가 '
                   '밀렸는지 크롭을 열어 본다(폐기 %s)'
                   % (eid, stray, sorted(void) or '없음'))
    filled = sorted(void - holes)
    if filled:
        out.append('%s: 폐기 문항 %s 에 정답률이 적혀 있다 — 원본은 그 칸에 '
                   "'삭제처리' 라고 쓴다. 한 칸 밀렸을 수 있다" % (eid, filled))
    return out


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

        # ④ 자리 — 폐기 문항에는 정답률이 없다. 빈칸이 딴 데 있으면 밀린 것이다.
        bad += align_bad(eid, r, ex.get('voided'))

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
