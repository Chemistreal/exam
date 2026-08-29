#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""틀린 문항이 **실제로 있는 강의**로 가는지 지킨다.

무슨 일이 있었나
----------------
성적표는 틀린 문항마다 「이 개념 강의 →」 링크를 붙인다. 그 링크를 정하는 곳이
`final.html` 의 `lecFor(area, type)` 이고, 네 단계로 내려간다.

    AREALEC[area]      영역 권위 매핑        101개
    TYPELEC[type]      세부개념 권위 매핑     19개   ← 2026-08-29 에 새로 뒀다
    lecForType(type)   강의 제목과 흐릿 맞춤
    LEC[대분류].u       그 단원 대표 강의(최후)

2026-08-29 에 실측하니 문항 3,060개 가운데 **15개**만 정밀한 강의로 못 갔고,
그 15개는 125강 어디에도 없는 주제였다(크로마토그래피·세라믹·콜로이드·산성비·
온실기체·유효숫자·정밀도·순물질 혼합물). 없는 것을 가까운 강의로 보내지 않는다.

■ 하마터면 큰일 날 뻔한 것

`lecture_curriculum_125.md` 는 **강의를 짓기 전의 계획**이다. 실제 파일과
제목이 맞는 것이 125강 중 42강뿐이고 번호도 어긋난다 — 그 문서의
`034. 원자량·분자량·화학식량` 자리에 실제로 있는 파일은 `lec-034-mole-avogadro`
(몰과 아보가드로 수)다. 개념을 그 번호로 이었다면 학생이 딴 강의를 봤을 것이다.
문서 머리에 경고를 달아 뒀고, 이 자는 **파일과 목차**만 정본으로 본다.

■ 지키는 것

  · AREALEC·TYPELEC 이 가리키는 파일이 실제로 있는가
  · lecture-index.html 의 링크가 다 살아 있고, 빠진 파일이 없는가
  · 정밀한 강의로 가는 문항 수가 **줄지 않았는가** (바닥은 늘기만 한다)

⚠ 이 자는 «그 강의가 맞는 강의인지» 를 안 본다. 「전기음성도」를 015강에 보낸
  것이 옳은지는 화학을 아는 사람이 본다. 여기서 재는 것은 «닿는가» 뿐이다.

    python3 tools/lecture_sync.py           # 지금 어디까지 닿나
    python3 tools/lecture_sync.py --check   # 끊기거나 줄면 빨간불 (CI)
    python3 tools/lecture_sync.py --seal    # 지금 값을 새 바닥으로
"""
import collections
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAL = os.path.join(ROOT, 'tools', 'lecture_sync.json')


def maps():
    s = io.open(os.path.join(ROOT, 'final.html'), encoding='utf-8').read()
    out = {}
    for name in ('AREALEC', 'TYPELEC', 'RXMAP'):
        i = s.index('const %s=' % name)
        out[name] = dict(re.findall(r"'([^']+)':'([^']+)'", s[i:s.index('\n};', i)]))
    # ⚠ LECLIST 는 **한 줄**로 적혀 있다. '\n];' 를 찾으면 못 만나 파일 끝까지
    #   집어삼키고, 엉뚱한 배열까지 강의 목록으로 센다(처음에 125가 755가 됐다).
    i = s.index('const LECLIST=')
    out['LECLIST'] = re.findall(r'\["(lec-\d{3}-[^"]+\.html)","([^"]+)"\]',
                                s[i:s.index('];', i) + 2])
    i = s.index('const LEC=')
    out['LECU'] = dict(re.findall(r'"u":\s*"([^"]+)"', s[i:s.index('\n};', i)]) and
                       [(k, v) for k, v in re.findall(r'"([^"]+)":\s*\{[^{}]*?"u":\s*"([^"]+)"',
                                                      s[i:s.index('\n};', i)], re.S)])
    return out


def files():
    return {f for f in os.listdir(ROOT) if re.match(r'^lec-\d{3}-.+\.html$', f)}


def main():
    check = '--check' in sys.argv
    seal = '--seal' in sys.argv
    M = maps()
    F = files()
    bad = False

    print('강의 파일 %d개 · AREALEC %d · TYPELEC %d · LECLIST %d'
          % (len(F), len(M['AREALEC']), len(M['TYPELEC']), len(M['LECLIST'])))

    # ① 가리키는 파일이 실제로 있는가
    for name in ('AREALEC', 'TYPELEC'):
        ghost = sorted({v for v in M[name].values() if v not in F})
        if ghost:
            bad = True
            print('\n%s 이 없는 파일을 가리킨다 %d개: %s' % (name, len(ghost), ', '.join(ghost[:8])))
    ghostL = sorted({f for f, _ in M['LECLIST'] if f not in F})
    if ghostL:
        bad = True
        print('\nLECLIST 에 없는 파일 %d개: %s' % (len(ghostL), ', '.join(ghostL[:8])))
    ghostU = sorted({v for v in M['LECU'].values() if v not in F})
    if ghostU:
        bad = True
        print('\nLEC 대표 강의가 없는 파일을 가리킨다: %s' % ', '.join(ghostU[:8]))

    # ② 목차가 파일과 맞는가
    idx = io.open(os.path.join(ROOT, 'lecture-index.html'), encoding='utf-8').read()
    linked = set(re.findall(r'href="(lec-\d{3}-[^"]+\.html)"', idx))
    dead = sorted(linked - F)
    orphan = sorted(F - linked)
    if dead:
        bad = True
        print('\n목차의 죽은 링크 %d개: %s' % (len(dead), ', '.join(dead[:8])))
    if orphan:
        bad = True
        print('\n목차에 안 걸린 강의 %d개: %s' % (len(orphan), ', '.join(orphan[:8])))

    # ③ 문항이 정밀한 강의로 닿는가
    xs = json.load(io.open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    clean = lambda t: re.sub(r'[^가-힣A-Za-z0-9]', '', str(t or ''))

    def lcs(a, b):
        m = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        best = 0
        for x in range(1, len(a) + 1):
            for y in range(1, len(b) + 1):
                if a[x - 1] == b[y - 1]:
                    m[x][y] = m[x - 1][y - 1] + 1
                    best = max(best, m[x][y])
        return best

    def fuzzy(t):
        t = clean(t)
        if len(t) < 2:
            return None
        best, bs = None, 0
        for f, name in M['LECLIST']:
            sc = lcs(t, clean(name))
            if sc > bs:
                bs, best = sc, f
        return best if bs >= 3 else None

    hit = 0
    miss = collections.Counter()
    tot = 0
    for e in xs:
        A, T = e.get('area') or [], e.get('type') or []
        for i in range(e['nQ']):
            tot += 1
            a = A[i] if i < len(A) else ''
            t = T[i] if i < len(T) else ''
            if M['AREALEC'].get(a) or M['TYPELEC'].get(t) or fuzzy(t):
                hit += 1
            else:
                miss['%s / %s' % (a, t)] += 1

    print('\n정밀한 강의로 닿는 문항 %d/%d (%d%%)' % (hit, tot, round(100 * hit / tot)))
    if miss:
        print('못 닿는 문항 %d개 · %d종 — 125강에 그 주제가 없는 자리다:'
              % (sum(miss.values()), len(miss)))
        for k, n in miss.most_common(20):
            print('  %-40s %d' % (k, n))

    if seal:
        json.dump({'설명': '정밀한 강의로 닿는 문항 수. 늘기만 한다 — 줄면 빨간불.',
                   '바닥': hit}, io.open(SEAL, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        io.open(SEAL, 'a', encoding='utf-8').write('\n')
        print('\n지금 값을 tools/lecture_sync.json 에 바닥으로 적었다.')
        return 0
    if os.path.exists(SEAL):
        was = json.load(io.open(SEAL, encoding='utf-8')).get('바닥', 0)
        if hit < was:
            bad = True
            print('\n**줄었다** — 닿는 문항 %d → %d' % (was, hit))
        elif hit > was:
            print('\n늘었다 — %d → %d. --seal 로 새 바닥을 적는다.' % (was, hit))

    if bad:
        return 1 if check else 0
    print('\n끊긴 데 없다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
