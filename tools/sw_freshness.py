#!/usr/bin/env python3
"""**낡아도 되는 파일과 낡으면 안 되는 파일**을 서비스워커가 갈라 놓았는지 본다.

왜 이 자가 있나
---------------
2026-08-10, 선생님 말씀.

    "지금 성적표 보면 2017인데도 총인원이 11명으로 표시되니까 데이터가 빠진거지"

저장소를 열어 보니 `hwol-2017` 은 **100명**이 들어 있었고, 손에서 재면
`N=111 (기준 100 + 이번 11)` 이 제대로 나왔다. **파일에는 있는데 그 기기까지
가지 않은 것이다.**

까닭은 서비스워커였다. `cohort/baseline.json` 이 `REFRESHABLE` 에 들어 있어
stale-while-revalidate — **캐시를 먼저 주고** 새것은 *다음* 열람용으로만 받아
뒀다. 게다가 그 캐시는 `chemistreal-data` 로 **버전이 없어 배포해도 안
지워진다.** 기준 기록이 열두 회차 늘어난 뒤에도 옛 파일이 그 기기에 앉아
있었다.

    해설(donghyung·answers)   하루 늦게 반영돼도 된다        낡아도 된다
    석차의 분모(cohort/)      학부모 종이에 찍히는 숫자다    낡으면 안 된다

낡은 분모는 **틀린 것처럼 보이지 않으면서 틀린다.** "10/11" 은 화면이 깨진
것도 아니고 오류도 아니다 — 그냥 조용히 다른 숫자다. 그래서 아무도 안
알아채고, 알아채는 것은 늘 사람이다.

⚠ 2026-08-03 에도 같은 갈래였다(옛 `final.html` 이 캐시에서 나왔다). 그때는
  `VERSION` 을 껍데기 내용에서 짓게 해서 막았는데, **data 캐시는 그 VERSION 을
  안 탄다.** 한 번 막은 갈래가 옆문으로 다시 들어온 것이다.

무엇을 보나
-----------
  ① 숫자를 만드는 자료(`cohort/`)가 **캐시 먼저**로 잡혀 있지 않은가
  ② `chemistreal-data` 처럼 **버전 없는 캐시**에 그것이 들어가지 않는가
  ③ 그 자료가 `ASSETS` 에 있어 배포마다 이름이 바뀌는가

    python3 tools/sw_freshness.py           # 무엇이 어느 칸에 있나
    python3 tools/sw_freshness.py --check   # 숫자 자료가 캐시 먼저면 빨간불
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SW = os.path.join(ROOT, 'sw.js')

# **낡으면 안 되는 것.** 사람이 보는 숫자를 만드는 자료.
# 여기 이름을 늘릴 때는 "이게 하루 낡으면 누가 무엇을 잘못 읽나" 를 먼저 묻는다.
MUST_BE_FRESH = ['cohort/']


def main():
    check = '--check' in sys.argv
    try:
        s = open(SW, encoding='utf-8').read()
    except OSError:
        print('sw.js 가 없다 — 잴 것이 없다.')
        if check:
            print('PASS')
        return 0

    def rx(name):
        m = re.search(r'const %s = (/[^;]+/)' % name, s)
        return m.group(1) if m else None

    imm, refr, fresh = rx('IMMUTABLE'), rx('REFRESHABLE'), rx('FRESH')
    print('서비스워커가 가른 칸')
    print('  IMMUTABLE   (한 번 받으면 그만)      %s' % (imm or '(없다)'))
    print('  REFRESHABLE (캐시 먼저 · 다음에 반영) %s' % (refr or '(없다)'))
    print('  FRESH       (망 먼저 · 못 닿을 때만)  %s' % (fresh or '(없다)'))

    bad = []
    for path in MUST_BE_FRESH:
        stem = path.strip('/')
        in_refr = bool(refr and stem in refr)
        in_imm = bool(imm and stem in imm)
        in_fresh = bool(fresh and stem in fresh)
        where = ('REFRESHABLE' if in_refr else
                 'IMMUTABLE' if in_imm else
                 'FRESH' if in_fresh else '(아무 칸에도 없다)')
        print('\n  %-12s → %s' % (path, where))
        if in_refr or in_imm:
            bad.append('`%s` 가 **캐시 먼저**(%s)로 잡혀 있다. 이건 사람이 보는 '
                       '숫자를 만드는 자료라,\n    낡은 사본이 나가면 "총인원 11명" '
                       '처럼 **틀린 것처럼 보이지 않으면서 틀린다.**' % (path, where))
        elif not in_fresh:
            bad.append('`%s` 가 FRESH 에 없다 — 어느 칸으로 가는지 이 파일만 '
                       '보고는 알 수 없다.' % path)

    # ③ 배포마다 이름이 바뀌는가 (gen_sw_version 이 ASSETS 를 해시한다)
    m = re.search(r'const ASSETS = \[([^\]]*)\]', s, re.S)
    assets = re.findall(r"'([^']+)'", m.group(1)) if m else []
    for path in MUST_BE_FRESH:
        if not any(path.strip('/') in a for a in assets):
            bad.append('`%s` 가 ASSETS 에 없다 — 배포해도 캐시 이름이 안 바뀐다'
                       % path)

    # ② 버전 없는 캐시에 넣고 있지 않은가
    if re.search(r'FRESH\.test[^}]{0,200}put\(\s*DATA', s, re.S):
        bad.append('FRESH 자료를 **버전 없는 캐시(DATA)** 에 넣고 있다 — '
                   '배포해도 안 지워진다')

    if bad:
        print('\n⚠ 낡으면 안 되는 자료가 잘못 잡혀 있다 %d곳' % len(bad))
        for b in bad:
            print('  ' + b)
        print('\n해설은 하루 늦어도 된다. 석차의 분모는 아니다.')
        if check:
            print('\nFAIL')
            return 1
        return 0

    print('\n낡으면 안 되는 자료가 망 먼저로 잡혀 있다.')
    if check:
        print('PASS')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
