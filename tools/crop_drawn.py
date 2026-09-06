#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""크롭이 **PDF 를 자른 것인가, 글을 그린 것인가**를 잰다.

왜 —
  「모든 문항을 PDF 크롭으로」가 규칙이다. 그런데 교재에서 옮겨 온 회차들은
  HWPX 에서 캔 글을 HTML 로 그려 그림으로 뽑은 것이었다. 겉보기에는 똑같이
  crops/<회차>/<번호>.png 라서 파일만 봐서는 안 갈린다. 그 사이에 원문의
  표·오비탈 상자·첨자·분수가 통째로 빠지고 문장 부호까지 사라졌다.

  더 나빴던 것은 그 구멍을 **원본의 구멍으로 착각**한 것이다. 「시험지에도
  선지가 없다」고 아홉 문항을 못 하는 것으로 적어 두었는데, 선생님이 원본
  시험지를 주시니 아홉 다 선지가 멀쩡히 있었다(2026-09-06).

무엇으로 가르나
  그린 크롭은 머리글 아래에 **가로줄**을 하나 긋는다. 자른 크롭에는 그 줄이
  없다 — 시험지에는 그런 선이 없기 때문이다. 그림 하나만 보면 되므로 답지도
  PDF 도 안 읽는다.

  ⚠ 처음에는 「폭의 90% 이상」·「먹이 120보다 진한 줄」로 잡았다가 학생 회차
    스물셋을 통째로 놓쳤다(954장 가운데 534장). 그 회차들은 줄이 조금 짧고
    (83%) 조금 옅다. 문턱을 75%·200 으로 늘리니 서른 회차가 다 걸리고,
    **진짜로 자른 회차는 하나도 안 걸린다** — 시험지에는 그런 줄이 없어서
    문턱을 늘려도 헛걸림이 안 생긴다.

    python3 tools/crop_drawn.py            # 잰다
    python3 tools/crop_drawn.py --check    # 남아 있으면 알린다(빨간불은 아니다)
"""
import collections
import glob
import io
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 원본 시험지가 저장소에 없어 아직 그린 채로 둘 수밖에 없는 회차.
# 학생마다 다른 변형본이라 원본은 HWPX 뿐이다 — 선생님이 그 HWPX 를 PDF 로
# 내보내 주시면 다른 회차와 똑같이 자를 수 있다.
NO_SOURCE_YET = {
    's1e3u232r0e5-2', 's1e3u232r0e5-3', 's1e3u232r0e5-4',
    's2h5j6i15602-3', 's2h5j6i15602-4', 's2p0c114x5f2-2',
    's2p0c114x5f2-3', 's2p0c114x5f2-4', 's2u0z3u5x6h6-2',
    's2u0z3u5x6h6-3', 's2u0z3u5x6h6-4', 's2z6y5b253u5-2',
    's2z6y5b253u5-3', 's2z6y5b253u5-4', 's313f105c6h3-3',
    's32243g212j0-2', 's32243g212j0-3', 's32243g212j0-4',
    's4o0j400e3g0-2', 's4o0j400e3g0-3', 's4o0j400e3g0-4',
    's4w000h6h6l0-2', 's4w000h6h6l0-3', 's4w000h6h6l0-4',
    's6h5o00163f6-3', 's6j5g674r1p2-3', 's6w2y5y2i485-2',
    's6w2y5y2i485-3', 's6w2y5y2i485-4', 's6y3i28160a2-3',
}


def is_drawn(path) -> bool:
    a = np.asarray(Image.open(path).convert('L'))
    if a.shape[0] < 60:
        return False
    for y in range(4, 80):
        if (a[y] < 200).sum() > 0.75 * a.shape[1]:
            return True
    return False


def scan():
    tot = collections.Counter()
    drawn = collections.Counter()
    for p in sorted(glob.glob(os.path.join(ROOT, 'crops', '*', '*.png'))):
        eid = os.path.basename(os.path.dirname(p))
        if not os.path.basename(p)[:-4].isdigit():
            continue
        tot[eid] += 1
        if is_drawn(p):
            drawn[eid] += 1
    return tot, drawn


def main():
    check = '--check' in sys.argv
    tot, drawn = scan()
    rows = sorted(((drawn[e], tot[e], e) for e in tot if drawn[e]), reverse=True)
    waiting = [r for r in rows if r[2] in NO_SOURCE_YET]
    fresh = [r for r in rows if r[2] not in NO_SOURCE_YET]
    print('크롭 %d장 · 그 가운데 글로 그린 것 %d장'
          % (sum(tot.values()), sum(d for d, _, _ in rows)))
    for d, t, e in waiting:
        print('  🔒 %-22s %3d/%d  원본 시험지를 기다린다' % (e, d, t))
    for d, t, e in fresh:
        print('  ◻  %-22s %3d/%d  ← 원본이 있는데 아직 안 잘랐다' % (e, d, t))
    if waiting and not fresh:
        print('\n남은 것은 모두 원본 시험지(HWPX 뿐)를 기다리는 자리다 —'
              ' 사람을 더 붙인다고 줄지 않는다.')
    if not rows:
        print('\n모든 문항이 시험지 원문 크롭이다.')
    return 1 if (check and fresh) else 0


if __name__ == '__main__':
    raise SystemExit(main())
