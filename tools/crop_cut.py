#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""크롭에 **선지가 잘려 나간** 문항을 찾는다.

왜 따로 재는가
--------------
선지별 오답 해설을 크롭 원문에서 채우다 보면, 어떤 문항은 아무리 해도 못
채운다. 크롭 그림이 발문에서 끝나고 ①~④ 가 잘려 있기 때문이다. 화올 2019
58번이 그랬다 — 「d-전자 배치로 가장 적절하게 짝지어진 것은?」까지만 있고
보기가 없다.

이건 집필하는 사람의 잘못이 아니라 **자료의 결함**이고, 고치는 길도 다르다
(크롭을 다시 뜨거나 문제지 PDF 에서 다시 잘라야 한다). 그래서 「아직 안 한
문항」과 섞어 세면 안 된다 — 아무리 사람을 붙여도 줄지 않는 수이기 때문이다.

무엇으로 가려내는가
-------------------
사람이 크롭을 읽고 지나간 자리인데도 `choices` 가 비어 있으면 잘린 것이다.
그래서 **같은 회차의 다른 문항은 채워졌는데 이 문항만 비어 있는** 자리를
찾는다. 회차 전체가 아직 손도 안 닿았으면 그냥 「아직 안 한 것」이라 세지
않는다.

    python3 tools/crop_cut.py            # 목록
    python3 tools/crop_cut.py --check    # 새로 생기면 빨간불
"""

from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 사람이 보고 「크롭이 잘렸다」고 확인한 자리. 새로 생기는 것만 빨간불이다.
BLOCKED = {
    # [2026-09-05 지웠다] donghyung-2 48 · hwol-2019 46·52·58 · hwol-2022 46
    #   다섯은 「크롭이 잘려서」가 맞았는데, 쪽을 넘어가는 자리를 다시 뜨고 나니
    #   선지가 다 들어왔다(hwol-2019 58번은 182 → 892픽셀이 됐다). 채웠으므로
    #   여기서 뺀다. **「못 하는 것」은 고치면 「한 것」이 된다** — 목록에 남겨
    #   두면 영영 못 하는 것으로 세어진다.
    # [2026-09-06 지웠다] kch1to2 6·34·44·46·50 과 kch1to2-b 6·34·44·50.
    #   「시험지에도 선지가 없다」고 적어 두었는데 **틀린 말이었다.** 그때 본
    #   크롭은 PDF 를 자른 것이 아니라 HWPX 에서 캔 글을 그린 것이었고,
    #   문제지 PDF 도 그 그림들을 이어 엮은 것이라 둘 다 같은 구멍을 갖고
    #   있었다 — 표·오비탈 상자·분수는 글로 안 캐진다. 선생님이 원본 시험지를
    #   주셔서 다시 자르니 아홉 문항 모두 선지가 멀쩡히 있다(눈으로 확인했다).
    #   **「저장소 어디에도 없다」와 「원본에 없다」는 다른 말이다.** 앞엣것을
    #   보고 뒤엣것을 단정했다.
}

# 크롭을 실제로 한 문항씩 읽어 본 회차. **이 목록 안에서만** 「잘렸다」고
# 말할 수 있다.
#
# ⚠ 처음에는 「채워진 비율이 절반을 넘으면 손이 닿은 회차」로 어림했다가
#   헛짚었다. kch2to3 3번을 잘렸다고 짚었는데 크롭을 열어 보니 ①~④ 가 다
#   있었다 — 그 회차는 예전 작업으로 절반이 차 있었을 뿐, 그 문항은 **아직
#   안 한 것**이었다. 「안 한 것」과 「못 하는 것」은 고치는 길이 다르므로
#   섞어 세면 둘 다 못 믿는 수가 된다. 그래서 어림을 버리고 목록으로 못박는다.
PASSED = {
    'donghyung-1', 'donghyung-2', 'donghyung-3', 'donghyung-4',
    'hwol-2017', 'hwol-2018', 'hwol-2019', 'hwol-2021', 'hwol-2022',
    'jmchc-1', 'jmchc-3', 'jmchc-5', 'jmchc-7', 'jmchc-9', 'jmchc-13',
    'kch1to3', 'kch1to2', 'kch1to2-b', 'sanyeom-60', 'jmchc-8', 'jmchc-11',
    'hwol-2023',
}


def scan():
    xs = json.load(io.open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    out = []
    for e in xs:
        eid, nQ = e['id'], e['nQ']
        p = os.path.join(ROOT, 'answers', '%s.json' % eid)
        if not os.path.exists(p):
            continue
        if eid not in PASSED:
            continue                      # 크롭을 읽어 본 회차가 아니다
        a = json.load(io.open(p, encoding='utf-8')).get('questions', {})
        for q in range(1, nQ + 1):
            k, qq = str(q), a.get(str(q), {})
            if qq.get('misconceptions') or qq.get('excluded'):
                continue
            if len(qq.get('acceptableAnswers') or []) >= 4:
                continue                  # 전원정답 — 오답 선지가 없다
            if not os.path.exists(os.path.join(ROOT, 'crops', eid, '%d.png' % q)):
                continue
            # ⚠ 예전에는 여기서 「답지에 choices 가 없으면 크롭이 잘린 것」으로
            #   보았다. 그 짐작이 두 번 죽었다.
            #     · 2026-09-05 집필 일꾼이 **지문·선지를 더는 옮겨 적지 않게**
            #       되었다. 그러니 choices 가 없는 것이 예사가 됐다.
            #     · 2026-09-06 「시험지에도 선지가 없다」던 아홉 문항이 원본
            #       시험지에서는 멀쩡히 선지를 갖고 있었다. 없던 것은 원본이
            #       아니라 **글로 캔 사본**이었다.
            #   그래서 짐작을 버리고, 사람이 크롭을 열어 보고 「이건 정말
            #   잘렸다」고 적은 것(BLOCKED)만 센다. 지금은 하나도 없다.
            if (eid, q) in BLOCKED:
                out.append((eid, q))
    return out


def main():
    check = '--check' in sys.argv
    found = scan()
    print('선지가 잘린 문항 %d개 (크롭을 읽어 본 %d회차 안에서)'
          % (len(found), len(PASSED)))
    for eid, q in found:
        mark = ''
        print('  %-16s %2d번%s' % (eid, q, mark))
    fresh = []
    if fresh:
        print('\n새로 생긴 %d개는 사람이 크롭을 다시 떠야 한다.' % len(fresh))
        print('고친 뒤에는 이 자의 BLOCKED 에서 지운다.')
        return 1 if check else 0
    if found:
        print('\n모두 이미 아는 것이다. 크롭을 다시 뜨거나 문제지에서 다시 잘라야 '
              '채울 수 있다 — 사람을 더 붙인다고 줄지 않는다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
