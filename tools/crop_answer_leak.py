#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""크롭에 **정답이 인쇄돼 있는지** 센다.

왜 —
  문제지 가운데는 문항 딱지 오른쪽에 정답을 동그라미 숫자로 찍어 둔 것이 있다.
  빨간 표식은 크롭을 뜨는 자가 지우는데, 까맣게 찍힌 것은 안 지워졌다.
  화올 2024(KMChC 2024 제1차)는 **예순 장이 전부** 답을 보여 주고 있었다
  (2026-09-05에 드러났다. 1~6번과 30번을 눈으로 읽어 정답표와 대조했고
   ④④③②④② · ④ 로 전부 일치했다).

  pdf_answer_leak.py 는 **문제지 PDF** 를 본다. 학생이 보는 것은 크롭이다.
  둘은 다른 물건이라 따로 세야 한다.

무엇을 세나 —
  크롭 맨 위에서 회색 딱지를 찾고, 그 **오른쪽 좁은 띠**(딱지 오른쪽 6~44px)에
  먹이 뭉쳐 있는지 본다. 같은 자리에 「정답률 : 15%」·「(전원정답)」을 찍는
  회차가 여럿이라(화올 2010~2013·기출동형 4회), 그런 것은 띠보다 오른쪽에서
  시작하므로 안 걸린다. 그래도 새로 걸리는 것은 **사람이 한 번 열어 봐야 한다.**

    python3 tools/crop_answer_leak.py            # 센다
    python3 tools/crop_answer_leak.py --check    # 새로 생기면 빨간불
"""
import glob
import io
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 사람이 열어 보고 「답이 아니다」로 판정한 자리. 여기 있는 것은 안 센다.
# 값은 (회차, 문항). 대개 「정답률 : NN%」 이나 「(전원정답)」 이 띠에 걸친
# 것이다 — 답을 알려 주지 않으므로 지울 까닭이 없다.
BENIGN = {
    ('hwol-2010', 39), ('hwol-2011', 26), ('hwol-2013', 52),
    ('hwol-2012', 3), ('hwol-2012', 5), ('hwol-2012', 6),
    ('hwol-2012', 9), ('hwol-2012', 26),
    ('hwol-2019', 23),          # 지우다 만 빨간 「문제 삭제」
    ('jmchc-4', 36),            # (전원정답)
    # 묶음 문두를 얹은 크롭 — 얹힌 딱지가 띠에 걸린다. 답이 아니다.
    ('jmchc-9', 39), ('jmchc-9', 40), ('jmchc-9', 56), ('jmchc-9', 57),
    ('jmchc-10', 38), ('jmchc-10', 39), ('jmchc-10', 55), ('jmchc-10', 56),
    ('jmchc-13', 40), ('jmchc-13', 41),
    ('jmchc-14', 40), ('jmchc-14', 41),
}

# 이 자가 크롭을 뜬 회차만 센다. 교재에서 옮겨 온 회차·미국 원판·j0 는
# 회색 딱지 자체가 없어 띠를 잡을 자리가 없다.
def _eligible_ids():
    # ⚠ importlib 로 파일에서 직접 불러오면 @dataclass 가 죽는다
    #   (sys.modules 에 안 올라가서 제 모듈을 못 찾는다). 경로에 넣고
    #   여느 모듈처럼 부른다 — crop_align.py 도 그렇게 한다.
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import build_wrongbook_assets as B
    xs = json.load(io.open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    # exams.json 에 없는 폴더(학생별 파이널 s*)는 애초에 제 크롭이 아니라
    # 다른 회차 것을 빌려 쓴다 — 원본 회차에서 이미 세므로 여기서 또 세면
    # 같은 그림을 두 번 세는 셈이다.
    return {e['id'] for e in xs if not B.no_grey_labels(e)}


# 딱지 오른쪽 띠의 자리. 그림에서 딱지를 찾아내려다 헛짚었다 — 회색이
# 딱지 말고도 여기저기 있어(표 머리·음영) 엉뚱한 자리를 재고 453개를
# 내놓았다. 이 문제지들은 딱지 자리가 한결같다: 크롭 왼끝이 60pt, 딱지
# 오른끝이 157pt 언저리, 배율 2배 → 그림에서 194px 즈음이다. 그러니
# 자리를 **못박는다.** 재는 자가 흔들리면 세는 수도 못 믿는다.
BAND = (192, 290, 8, 56)      # x0, x1, y0, y1 (그림 픽셀)


def scan():
    ok = _eligible_ids()
    out = []
    x0, x1, y0, y1 = BAND
    for p in sorted(glob.glob(os.path.join(ROOT, 'crops', '*', '*.png'))):
        eid = os.path.basename(os.path.dirname(p))
        if eid not in ok:
            continue
        base = os.path.basename(p)[:-4]
        if not base.isdigit():
            continue
        gray = np.asarray(Image.open(p).convert('L'))
        if gray.shape[0] < y1 or gray.shape[1] < x1:
            continue
        if (gray[y0:y1, x0:x1] < 120).sum() > 40:
            out.append((eid, int(base)))
    return out


def main():
    check = '--check' in sys.argv
    found = scan()
    fresh = [x for x in found if x not in BENIGN]
    print('딱지 오른쪽에 먹이 있는 크롭 %d개 · 그 가운데 아직 못 본 것 %d개'
          % (len(found), len(fresh)))
    for eid, q in fresh:
        print('  %-18s %2d번   ← 열어 봐야 한다' % (eid, q))
    if fresh:
        print('\n크롭을 열어 보고, 정답이면 build_wrongbook_assets.py 의 ANSWER_MARK 에')
        print('그 회차를 넣어 다시 떠라. 정답이 아니면 이 자의 BENIGN 에 적어라.')
        return 1 if check else 0
    print('정답이 인쇄된 채로 나가는 크롭은 없다.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
