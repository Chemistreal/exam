"""보기(가·나·다·라)가 크롭에서 통째로 빠진 문항을 찾는다.

왜 필요한가
-----------
2026-09-07 에 학생별 파이널 변형본의 크롭을 눈으로 훑다가 나왔다.
`crops/s32243g212j0-2/5.png` 는 이렇게 생겼다.

    동종 이원자 화학종의 분자 오비탈 에너지 도표를 기반으로 한 …
    ┌──────────────────────────────┐
    │ 나. B₂는 상자성이고, C₂는 반자성이다.        │
    │ 다. 결합 차수는 N₂⁺가 N₂보다 크다.          │
    │ 라. 산소 원자 사이의 결합 길이는 …           │
    └──────────────────────────────┘
    ① 가, 나   ② 가, 다   ③ 나, 라   ④ 다, 라

**「가」가 없다.** 그런데 ①·②가 「가」를 가리킨다. 답지에는 「가. O₂는 π*에
홀전자 2개 …」 가 멀쩡히 들어 있다 — 잃어버린 것은 크롭 한 장뿐이고,
그 한 장이 학생이 보는 전부다. 이 문항은 지금 **풀 수가 없다.**

어떻게 재나
-----------
글자를 읽지 않는다(이 기계에 OCR 이 없다). 대신 둘을 견준다.

  ① 답지 해설이 이름 붙인 보기 딱지 — 「가.」 「나 (○)」 꼴을 센다
  ② 크롭 안 **보기 표의 줄 수** — 일정한 간격으로 이어진 가로줄을 세면
     칸 수가 나온다

표로 그린 보기만 잴 수 있다. 줄글로 쓴 보기는 그을 줄이 없어 못 센다 —
그 자리는 **못 잰다고 말하지, 통과시켰다고 말하지 않는다.**

실행
----
    python3 tools/crop_boki.py            # 재기만 한다
    python3 tools/crop_boki.py --check    # 하나라도 있으면 1 로 끝난다
"""

from __future__ import annotations

import json
import os
import re
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABELS = '가나다라마'

# 보기 표의 줄은 검은 글자가 아니라 **연한 회색 괘선**이다. 진하게 잡으면
# 하나도 안 걸리고(그래서 처음에 놓쳤다), 너무 연하게 잡으면 글자 줄이
# 걸린다. 245 / 90% 가 그 사이다.
INK, COVER = 245, 0.90
GAP_MIN, GAP_MAX, GAP_TOL = 18, 70, 7
# 표 아래로 남은 높이. 보기가 통째로 빠진 크롭은 **표 바로 밑이 선지 줄**이라
# 꼬리가 한 줄(45px 안팎)뿐이다. 보기가 멀쩡한 문항은 표와 선지 사이에 보기
# 줄글이 들어가 꼬리가 150px 을 넘는다. 눈으로 아홉 장을 다 보고 정한 값이다 —
# 44·45 대 154~251 로 갈렸다.
TAIL_MAX = 90

# ── 이미 알고 있고, 여기서는 못 고치는 자리 ──────────────────────────────
# 빠진 보기는 답지에 그대로 있지만, 학생이 보는 것은 크롭 한 장이다. 그 장을
# 제대로 만들려면 선생님 한글 원본이 다시 있어야 한다(hwpx 는 들여올 때 쓰고
# 저장소에 남기지 않는다). 그래서 이 둘은 **새로 생긴 것이 아니라 기다리는
# 것**으로 두고, `--check` 는 여기 없는 것이 나올 때만 빨간불을 켠다.
# 답지에는 확인 필요로 적어 두었다 — 학생·학부모 화면에도 그대로 뜬다.
BLOCKED = {('s32243g212j0-2', 5), ('s32243g212j0-2', 49)}


def named(expl: str) -> list[str]:
    """해설이 이름 붙인 보기 딱지."""
    out = []
    for lab in LABELS:
        if re.search(r'(?:^|[\s(])%s\s*[.．)]' % lab, expl):
            out.append(lab)
    return out


def hrules(path: str) -> list[int]:
    a = np.asarray(Image.open(path).convert('L'))
    w = a.shape[1]
    dark = (a < INK).sum(axis=1)
    ys, out = [y for y in range(a.shape[0]) if dark[y] > COVER * w], []
    for y in ys:
        if not out or y - out[-1] > 3:
            out.append(y)
    return out


def table_rows(path: str):
    """(보기 표의 칸 수, 표 밑에 남은 높이). 표가 아니면 (None, 0)."""
    ys = hrules(path)
    high = np.asarray(Image.open(path).convert('L')).shape[0]
    best = None
    i = 0
    while i < len(ys) - 1:
        run = [ys[i]]
        j = i
        while j < len(ys) - 1:
            gap = ys[j + 1] - ys[j]
            if not (GAP_MIN <= gap <= GAP_MAX):
                break
            if len(run) > 1 and abs(gap - (run[1] - run[0])) > GAP_TOL:
                break
            run.append(ys[j + 1])
            j += 1
        if len(run) > (len(best) if best else 0):
            best = run
        i = max(j, i + 1)
    if not best or len(best) < 3:      # 칸이 둘 미만이면 표라고 볼 수 없다
        return None, 0
    return len(best) - 1, high - best[-1]


def rounds() -> list[str]:
    p = os.path.join(ROOT, 'student-finals.json')
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8') as f:
        return [e['id'] for e in json.load(f)['exams']]


def scan(ids: list[str]):
    short, unmeasured, looked = [], 0, 0
    for eid in ids:
        ap = os.path.join(ROOT, 'answers', eid + '.json')
        if not os.path.exists(ap):
            continue
        with open(ap, encoding='utf-8') as f:
            qs = (json.load(f).get('questions') or {})
        for k, q in qs.items():
            labs = named(q.get('explanation') or '')
            if len(labs) < 3:
                continue
            cp = os.path.join(ROOT, 'crops', eid, k + '.png')
            if not os.path.exists(cp):
                continue
            looked += 1
            rows, tail = table_rows(cp)
            if rows is None or tail > TAIL_MAX:
                # 표 밑에 줄글이 더 있으면 그 표는 보기 표가 아니다(자료 표다).
                unmeasured += 1
            elif rows < len(labs):
                short.append((eid, int(k), rows, len(labs), ''.join(labs)))
    return short, unmeasured, looked


def main() -> int:
    ids = rounds()
    if not ids:
        print('학생별 파이널 회차를 못 찾았다 — student-finals.json 이 없다.')
        return 0
    short, unmeasured, looked = scan(ids)
    waiting = [x for x in short if (x[0], x[1]) in BLOCKED]
    fresh = [x for x in short if (x[0], x[1]) not in BLOCKED]
    print('가·나·다 꼴 문항 %d개 · 표로 그린 것 %d개 · 줄글이라 못 잰 것 %d개'
          % (looked, looked - unmeasured, unmeasured))
    for tag, group, tail in (('◻ ', fresh, '새로 생겼다 — 봐야 한다.'),
                             ('🔒', waiting, '원본 시험지를 기다린다.')):
        if not group:
            continue
        print('\n%s 보기가 빠진 문항 %d개 — 학생은 이 문항을 풀 수 없다. %s'
              % (tag, len(group), tail))
        for eid, n, rows, want, labs in sorted(group):
            print('  %s %-18s %2d번  표는 %d줄인데 보기는 %d개(%s)'
                  % (tag, eid, n, rows, want, labs))
    if not short:
        print('\n표로 그린 보기는 줄 수가 모두 맞는다.')
    else:
        print('\n답지에는 빠진 보기가 그대로 있다 — 잃은 것은 크롭 한 장이다.')
    gone = sorted(BLOCKED - {(x[0], x[1]) for x in short})
    if gone:
        print('\n낫은 자리가 있다 — BLOCKED 에서 빼라: %s'
              % ', '.join('%s %d번' % g for g in gone))
    if '--check' in sys.argv:
        return 1 if fresh else 0
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
