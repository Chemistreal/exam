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
KNOWN = {
    ('donghyung-2', 48), ('hwol-2019', 46), ('hwol-2019', 52),
    ('hwol-2019', 58), ('hwol-2022', 46),
    # kch1to2 의 다섯은 **크롭만이 아니라 문제지 PDF 에도** 선지가 없다.
    # pdftotext -layout 으로 뽑아 확인했다 — 이 발문들 아래가 비어 있고
    # 바로 뒤 문항(7·35·45·47·51)의 선지는 멀쩡히 나온다. HWP 원본도
    # choices 가 빈 배열이다. 저장소 안 어디에도 옮겨 적을 원문이 없다.
    ('kch1to2', 6), ('kch1to2', 34), ('kch1to2', 44),
    ('kch1to2', 46), ('kch1to2', 50),
    # 동형본 kch1to2-b 도 같은 자리 넷이 그렇다. 2026-09-05 에 크롭을 눈으로
    # 열고, kch1to2-b-problem.pdf 를 pdftotext -layout 으로 뽑아 확인했다 —
    # 05·07·33·35·43·45·49·51번은 ①~④ 가 다 찍혀 있는데 이 넷만 발문에서
    # 끝난다. exam_kch1to2동형_HWP.json 도 choices 가 빈 배열이다.
    ('kch1to2-b', 6), ('kch1to2-b', 34), ('kch1to2-b', 44), ('kch1to2-b', 50),
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
            if qq.get('choices'):
                continue                  # 선지는 있다 — 잘린 게 아니다
            out.append((eid, q))
    return out


def main():
    check = '--check' in sys.argv
    found = scan()
    print('선지가 잘린 문항 %d개 (크롭을 읽어 본 %d회차 안에서)'
          % (len(found), len(PASSED)))
    for eid, q in found:
        mark = '' if (eid, q) in KNOWN else '   ← 새로 생겼다'
        print('  %-16s %2d번%s' % (eid, q, mark))
    fresh = [x for x in found if x not in KNOWN]
    if fresh:
        print('\n새로 생긴 %d개는 사람이 크롭을 다시 떠야 한다.' % len(fresh))
        print('고친 뒤에는 이 자의 KNOWN 에서 지운다.')
        return 1 if check else 0
    if found:
        print('\n모두 이미 아는 것이다. 크롭을 다시 뜨거나 문제지에서 다시 잘라야 '
              '채울 수 있다 — 사람을 더 붙인다고 줄지 않는다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
