#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""틀린 문항에 **같은 개념의 동형문제**가 붙는지 회차마다 잰다.

동형문제는 어디서 오나
----------------------
`donghyung/` 아래 회차 파일에 손으로 쓴 문항 2,700개가 있고,
`donghyung/index.json` 이 그것을 두 갈래로 색인한다.

    concept  세부개념 이름 → ['<회차>:<번호>', …]   710종   ← **이쪽이 정확하다**
    broad    대영역 이름   → […]                     31종   ← 세부개념이 없을 때 대신

성적표는 틀린 문항의 `type`(세부개념)으로 concept 을 먼저 찾고, 없으면 대영역으로
내려간다. 대영역으로 내려가면 «같은 단원의 다른 개념» 문제가 붙는다 — 붙기는
붙지만 그 학생이 틀린 그 개념이 아니다.

⚠ **이 자가 한 번 엉뚱한 것을 쟀다.** 처음에는 `retry-pool.json` + `answers/*.json`
  의 줄기·보기를 세어 «39% 만 붙는다» 고 했는데, 그건 「즉시 재도전 10제」가 쓰는
  다른 자리였다. 오답노트의 동형문제는 위 `donghyung/` 은행에서 온다.
  제대로 재니 **세부개념 91% · 대영역까지 100%** 다. 재는 자리를 틀리면
  숫자가 아니라 판단이 통째로 틀어진다 — 그래서 여기 적어 둔다.

2026-08-29 실측 (52회차 3,060문항)

    세부개념으로 바로   2,772 (91%)
    대영역으로만          288 ( 9%)   ← 여기가 남은 자리
    아무것도 없음            0

    대영역으로 떨어지는 288문항은 215종의 세부개념에 걸쳐 있고, 회차로 보면
    j0 51 · KMChC 심화 2025-2 47 · 2026-1 44 · 일반 25·24 에 몰려 있다.
    그중 15종은 **공백·기호만 다른 이름**이고, 85종은 은행에 비슷한 이름이
    있으며(사람이 봐야 한다 — 「열역학3법칙」과 「열역학2법칙」처럼 닮았지만
    다른 것이 섞여 있다), 나머지는 은행에 그 개념이 아예 없다.

    python3 tools/twin_cover.py           # 회차별
    python3 tools/twin_cover.py --gaps    # 세부개념 동형이 없는 이름들
    python3 tools/twin_cover.py --check   # 세부개념 커버리지가 **떨어지면** 빨간불
    python3 tools/twin_cover.py --seal    # 지금 값을 새 바닥으로
"""
import collections
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAL = os.path.join(ROOT, 'tools', 'twin_cover.json')


def rxmap():
    """final.html 의 RXMAP(세부영역 → 대영역). 두 벌로 적으면 갈라진다."""
    s = io.open(os.path.join(ROOT, 'final.html'), encoding='utf-8').read()
    i = s.index('const RXMAP=')
    return dict(re.findall(r"'([^']+)':'([^']+)'", s[i:s.index('\n};', i)]))


def measure():
    idx = json.load(io.open(os.path.join(ROOT, 'donghyung', 'index.json'), encoding='utf-8'))
    C, B = idx['concept'], idx['broad']
    RX = rxmap()
    xs = json.load(io.open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    rows, miss = [], collections.Counter()
    for e in xs:
        A, T = e.get('area') or [], e.get('type') or []
        ct = bd = no = 0
        for k in range(e['nQ']):
            t = T[k] if k < len(T) else ''
            a = A[k] if k < len(A) else ''
            if C.get(t):
                ct += 1
            elif B.get(RX.get(a, a)) or B.get(a):
                bd += 1
                if t:
                    miss[t] += 1
            else:
                no += 1
                if t:
                    miss[t] += 1
        rows.append({'id': e['id'], 'nQ': e['nQ'], 'concept': ct, 'broad': bd, 'none': no})
    return rows, miss, C


def main():
    check = '--check' in sys.argv
    seal = '--seal' in sys.argv
    gaps = '--gaps' in sys.argv
    rows, miss, C = measure()
    tq = sum(r['nQ'] for r in rows)
    tc = sum(r['concept'] for r in rows)
    tb = sum(r['broad'] for r in rows)
    tn = sum(r['none'] for r in rows)

    if gaps:
        import difflib
        norm = lambda x: re.sub(r'[^가-힣A-Za-z0-9]', '', x)
        Cn = {norm(c): c for c in C}
        print('세부개념 동형이 없는 문항 %d개 · 세부개념 %d종\n' % (sum(miss.values()), len(miss)))
        same, near, none = [], [], []
        for t, n in miss.most_common():
            nt = norm(t)
            if nt in Cn:
                same.append((t, n, Cn[nt]))
                continue
            b = difflib.get_close_matches(nt, list(Cn), n=1, cutoff=0.72)
            (near if b else none).append((t, n, Cn[b[0]] if b else ''))
        print('■ 공백·기호만 다른 이름 %d종 (문항 %d) — 이어 주면 그대로 붙는다'
              % (len(same), sum(x[1] for x in same)))
        for t, n, c in same:
            print('   %-30s(%d) → %s' % (t, n, c))
        print('\n■ 은행에 비슷한 이름이 있는 것 %d종 (문항 %d) — **사람이 봐야 한다**'
              % (len(near), sum(x[1] for x in near)))
        for t, n, c in near[:40]:
            print('   %-30s(%d) → %s' % (t, n, c))
        print('\n■ 은행에 그 개념이 아예 없는 것 %d종 (문항 %d) — 문제를 새로 써야 한다'
              % (len(none), sum(x[1] for x in none)))
        for t, n, _ in none[:30]:
            print('   %-30s(%d)' % (t, n))
        return 0

    print('문항 %d · 세부개념으로 %d (%d%%) · 대영역으로만 %d (%d%%) · 없음 %d'
          % (tq, tc, round(100 * tc / tq), tb, round(100 * tb / tq), tn))
    rows.sort(key=lambda r: r['concept'] / r['nQ'])
    print('\n%-24s %5s %14s %8s %6s' % ('회차', '문항', '세부개념', '대영역', '없음'))
    for r in rows:
        print('%-24s %5d %8d(%3d%%) %8d %6d'
              % (r['id'], r['nQ'], r['concept'], round(100 * r['concept'] / r['nQ']),
                 r['broad'], r['none']))

    now = {r['id']: r['concept'] for r in rows}
    now['__total__'] = tc
    if seal:
        json.dump({'설명': '회차별로 **세부개념** 동형문제가 붙는 문항 수. 이 수는 '
                           '늘기만 한다 — 줄면 빨간불이다. donghyung/index.json 의 '
                           'concept 색인에 이름을 이어 주면 오른다.',
                   '바닥': now},
                  io.open(SEAL, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1, sort_keys=True)
        io.open(SEAL, 'a', encoding='utf-8').write('\n')
        print('\n지금 값을 tools/twin_cover.json 에 바닥으로 적었다.')
        return 0

    if not os.path.exists(SEAL):
        print('\n바닥이 없다 — --seal 로 적어 둔다.')
        return 1 if check else 0
    was = json.load(io.open(SEAL, encoding='utf-8')).get('바닥', {})
    down = [(k, was[k], now.get(k, 0)) for k in sorted(was)
            if k != '__total__' and now.get(k, 0) < was[k]]
    up = [(k, was[k], now.get(k, 0)) for k in sorted(was)
          if k != '__total__' and now.get(k, 0) > was[k]]
    if up:
        print('\n늘었다 (%d회차):' % len(up))
        for k, a, b in up[:20]:
            print('  %-24s %d → %d' % (k, a, b))
        print('  --seal 로 새 바닥을 적는다.')
    if down:
        print('\n**줄었다** %d회차:' % len(down))
        for k, a, b in down:
            print('  %-24s %d → %d' % (k, a, b))
        return 1 if check else 0
    if not up:
        print('\n세부개념 동형이 붙는 문항이 줄지 않았다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
