#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""틀린 문항이 **정확히 어느 개념강의 한 강**으로 가는지 지킨다.

무슨 일이 있었나
----------------
선생님 지적(2026-08-29): «개념강의랑 틀린 문제가 잘 맞지 않는거같아.»
재어 보니 그랬다.

    문항 3,060개 · 세부개념(exams.json 의 type) 917종 · 개념강의 125강

    · index.html 의 AREA2LEC 는 키가 57개뿐 → 영역 86종(문항 1,371개 = 45%)이
      개념강의로 **아예 못 갔다**.
    · 이어지는 것도 「영역 → 목차의 area 앵커」라 **10강 묶음**으로 보냈다.
      틀린 문항 하나가 어느 1강인지 못 짚었다.
    · final.html 과 index.html 이 **서로 다른 길**을 썼다.

■ 왜 표기 통일로는 못 고치나

처음에는 «같은 개념이 다른 이름으로 흩어졌겠지» 라고 봤다(DT 저장소가 실제로
그랬다). 재어 보니 아니었다 — 조사·어순·공백만 다른 묶음이 **1개**뿐이고,
917종 가운데 505종(55%)이 **한 문항에만** 나온다. 이름이 갈린 것이 아니라
`type` 이 애초에 강의보다 잘게 쓰인 자유 서술 딱지다(「수소원자」·「반응의자발성」
·「용액의총괄성」). 그러니 합칠 것이 아니라 **강의로 보내는 층**이 있어야 한다.

■ 그 층이 두 몫을 한다

    ① 성적표의 틀린 문항에 붙는 «이 개념 강의 →» 링크 (1강으로)
    ② 동형문제를 고를 때 «같은 개념» 의 기준

②가 중요하다. 지금 동형문제는 type 이 **글자까지 같아야** 붙어서, 커버리지가
3,060문항 중 1,193개(39%)뿐이다(tools/twin_cover.py). USNCO 2%·KMChC 심화 0%.
강의를 기준으로 삼으면 «같은 강을 듣는 문제» 끼리 붙어 그 수가 오른다.

■ 이 자가 지키는 것

    · map 의 강의 번호가 실제 파일(lec-NNN-*.html)을 가리키는가
    · exams.json 의 세부개념이 map 이나 unmapped 중 **한 곳에는** 있는가
      (조용히 빠지는 길을 안 남긴다 — 빠지면 그 문항은 강의 없이 흘러간다)
    · 덮는 문항 수가 **줄지 않았는가** (바닥은 늘기만 한다)

⚠ 이 자는 «배정이 옳은지» 를 안 본다. 「전기음성도」를 015강에 보낸 것이 맞는지는
  화학을 아는 사람이 본다. 여기서 재는 것은 «이어져 있는가» 뿐이다.

    python3 tools/lecture_link.py           # 지금 얼마나 이어져 있나
    python3 tools/lecture_link.py --check   # 끊기거나 줄면 빨간불 (CI)
    python3 tools/lecture_link.py --seal    # 지금 덮는 수를 새 바닥으로
"""
import collections
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, 'concept-lecture.json')
SEAL = os.path.join(ROOT, 'tools', 'lecture_link.json')


def types_of():
    xs = json.load(io.open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    c = collections.Counter()
    for e in xs:
        for t in (e.get('type') or []):
            if t:
                c[t] += 1
    return c


def main():
    check = '--check' in sys.argv
    seal = '--seal' in sys.argv
    if not os.path.exists(MAP):
        print('concept-lecture.json 이 없다.')
        return 1 if check else 0
    doc = json.load(io.open(MAP, encoding='utf-8'))
    lec, mp, un = doc.get('lectures', {}), doc.get('map', {}), doc.get('unmapped', {})
    types = types_of()
    nQ = sum(types.values())

    # ① 강의 번호가 실제 파일을 가리키는가
    ghost = sorted({v for v in mp.values() if v not in lec})
    dead = sorted(n for n, d in lec.items()
                  if not os.path.exists(os.path.join(ROOT, d.get('file', ''))))
    # ② 빠진 세부개념
    missing = sorted(t for t in types if t not in mp and t not in un)
    stale = sorted(t for t in list(mp) + list(un) if t not in types)
    # ③ 덮는 문항
    covQ = sum(types[t] for t in types if t in mp)
    covT = sum(1 for t in types if t in mp)

    print('세부개념 %d종 · 문항 %d개 · 개념강의 %d강' % (len(types), nQ, len(lec)))
    print('이어진 세부개념 %d종(%d%%) · 이어진 문항 %d개(%d%%)'
          % (covT, round(100 * covT / max(1, len(types))),
             covQ, round(100 * covQ / max(1, nQ))))
    if un:
        unQ = sum(types.get(t, 0) for t in un)
        print('못 이은 세부개념 %d종(문항 %d개) — 까닭이 적혀 있다' % (len(un), unQ))

    bad = False
    if ghost:
        bad = True
        print('\n없는 강의로 보내는 세부개념 %d개: %s' % (len(ghost), ', '.join(ghost[:10])))
    if dead:
        bad = True
        print('\n파일이 없는 강의 %d개: %s' % (len(dead), ', '.join(dead[:10])))
    if missing:
        bad = True
        print('\nmap 에도 unmapped 에도 없는 세부개념 %d종 (문항 %d개):'
              % (len(missing), sum(types[t] for t in missing)))
        for t in missing[:20]:
            print('  %-40s %d문항' % (t, types[t]))
        print('  → 강의에 잇거나, 못 잇는 까닭을 unmapped 에 적는다.')
    if stale:
        print('\n시험에 없는 세부개념이 표에 남아 있다 %d종: %s'
              % (len(stale), ', '.join(stale[:10])))

    if seal:
        json.dump({'설명': '이어진 문항 수. 이 수는 **늘기만 한다** — 줄면 빨간불이다.',
                   '바닥': {'문항': covQ, '세부개념': covT}},
                  io.open(SEAL, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1, sort_keys=True)
        io.open(SEAL, 'a', encoding='utf-8').write('\n')
        print('\n지금 값을 tools/lecture_link.json 에 바닥으로 적었다.')
        return 0

    if os.path.exists(SEAL):
        was = json.load(io.open(SEAL, encoding='utf-8')).get('바닥', {})
        if covQ < was.get('문항', 0):
            bad = True
            print('\n**줄었다** — 이어진 문항 %d → %d' % (was['문항'], covQ))
        elif covQ > was.get('문항', 0):
            print('\n늘었다 — 이어진 문항 %d → %d. --seal 로 새 바닥을 적는다.'
                  % (was['문항'], covQ))

    if bad:
        return 1 if check else 0
    print('\n끊긴 데 없다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
