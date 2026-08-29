#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""틀린 문항이 **정확히 어느 개념강의 한 강**으로 가는지 지킨다.

무슨 일이 있었나
----------------
선생님 지적(2026-08-29): «개념강의랑 틀린 문제가 잘 맞지 않는거같아.»
재어 보니 그랬다.

    문항 3,060개 · 세부개념(exams.json 의 type) 917종 · 개념강의 125강

    · final.html 의 lecFor() 는 `AREALEC[area]` 를 **먼저** 본다. area 는
      「주기율」「산화환원」처럼 넓은 이름이라, 「이온화에너지」「전기분해」 같은
      정확한 type 이 있어도 덮인다. 함수 바로 위 주석에는 「유형 우선, 없으면
      영역」이라고 적혀 있는데 코드가 반대다.
    · 활성 9회차 540문항 중 **154문항(29%)** 이 그 자리다. 전체로는
      (area,type) 조합 1,449개 중 **1,369개**가 넓은 이름만 보고 강의를 고른다.
    · 마지막 층인 lecForType() 은 글자 겹침(LCS)이라, 커브를 놓치면
      「알짜이온반응식」을 「원자이온반지름」에 붙이는 식으로 **자신 있게 틀린다.**

⚠ 한때 이 자리에 「AREA2LEC 키가 57개뿐이라 45%가 강의로 못 갔다」 고 적혀 있었다.
  그것은 index.html 의 표였다. 학부모가 여는 성적표는 final.html 이고, 그쪽
  lecFor() 는 이미 97%를 이었다. **재는 자리를 틀리면 숫자가 아니라 판단이
  통째로 틀어진다.** 여기 적힌 숫자는 전부 final.html 을 실제로 돌려 잰 값이다.

■ 왜 표기 통일로는 못 고치나

처음에는 «같은 개념이 다른 이름으로 흩어졌겠지» 라고 봤다(DT 저장소가 실제로
그랬다). 재어 보니 아니었다 — 조사·어순·공백만 다른 묶음이 **1개**뿐이고,
917종 가운데 505종(55%)이 **한 문항에만** 나온다. 이름이 갈린 것이 아니라
`type` 이 애초에 강의보다 잘게 쓰인 자유 서술 딱지다(「수소원자」·「반응의자발성」
·「용액의총괄성」). 그러니 합칠 것이 아니라 **강의로 보내는 층**이 있어야 한다.

■ 그 층이 두 몫을 한다

    ① 성적표의 틀린 문항에 붙는 «이 개념 강의 →» 링크 (1강으로)
    ② 동형문제를 고를 때 «같은 개념» 의 기준

②는 아직 안 쓴다. 동형문제는 donghyung/index.json 의 concept 로 붙고 있고
실측 커버리지는 3,060문항 중 2,869개(94%)다(tools/twin_cover.py). 강의를 기준으로
삼으면 남은 191개도 붙일 수 있지만, 그건 이 표가 다 채워진 뒤의 일이다.
(한때 여기 「39% · USNCO 2%」 라고 적혀 있었다. 엉뚱한 파일을 재고 쓴 숫자다.)

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
    python3 tools/lecture_link.py --absorb  # tools/_lecwip/*.json 을 표로 옮긴다
    python3 tools/lecture_link.py --emit    # 표를 final.html 의 TYPELEC·PAIRLEC 로
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


PAIRSEP = '|'


def by_file():
    """lec-013-….html → '013'. 표는 강의 번호로 적고, 화면은 파일 이름을 쓴다."""
    doc = json.load(io.open(MAP, encoding='utf-8'))
    return {d['file']: n for n, d in doc.get('lectures', {}).items()}, doc


def pairs_of():
    """(영역, 세부개념) 짝마다 문항 수. 같은 이름이 단원마다 다른 강의를 부를 때 쓴다."""
    xs = json.load(io.open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    c = collections.Counter()
    for e in xs:
        ar, ty = e.get('area') or [], e.get('type') or []
        for i in range(e.get('nQ') or 0):
            a = (ar[i] if i < len(ar) else '') or ''
            t = (ty[i] if i < len(ty) else '') or ''
            if t:
                c[a + PAIRSEP + t] += 1
    return c


def absorb():
    """집필해 둔 배선 조각(tools/_lecwip/*.json)을 표로 옮긴다.

    조각 하나는 {세부개념: {pick, byArea?, why}} 꼴이다.
    · pick 이 있으면          map[세부개념] = 강의번호
    · byArea 가 있으면        pairMap['영역|세부개념'] = 강의번호
    · 둘 다 없으면            unmapped[세부개념] = why  (조용히 빠지는 길을 안 남긴다)
    """
    import glob
    f2n, doc = by_file()
    mp = doc.setdefault('map', {})
    pm = doc.setdefault('pairMap', {})
    un = doc.setdefault('unmapped', {})
    parts = sorted(glob.glob(os.path.join(ROOT, 'tools', '_lecwip', '*.json')))
    if not parts:
        print('옮길 조각이 없다 (tools/_lecwip 가 비어 있다)')
        return 1
    added = paired = noted = ghosted = 0
    ghosts = []
    for p in parts:
        for ty, v in json.load(io.open(p, encoding='utf-8')).items():
            pick = (v or {}).get('pick') or ''
            why = (v or {}).get('why') or ''
            ba = (v or {}).get('byArea') or {}
            if pick:
                n = f2n.get(pick)
                if not n:
                    ghosted += 1
                    ghosts.append('%s → %s' % (ty, pick))
                    continue
                mp[ty] = n
                added += 1
            for ar, f in ba.items():
                n = f2n.get(f)
                if not n:
                    ghosted += 1
                    ghosts.append('%s(%s) → %s' % (ty, ar, f))
                    continue
                pm[ar + PAIRSEP + ty] = n
                paired += 1
            if not pick and not ba:
                un[ty] = why or '맞는 강의가 목록에 없다'
                noted += 1
    doc['map'] = dict(sorted(mp.items()))
    doc['pairMap'] = dict(sorted(pm.items()))
    doc['unmapped'] = dict(sorted(un.items()))
    io.open(MAP, 'w', encoding='utf-8').write(
        json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
    print('조각 %d개 → 이은 세부개념 %d · 단원별로 갈린 짝 %d · 강의 없음 %d'
          % (len(parts), added, paired, noted))
    if ghosts:
        print('없는 강의 파일을 가리킨 곳 %d: %s' % (ghosted, ', '.join(ghosts[:8])))
        return 1
    return 0


def emit():
    """표를 final.html 의 TYPELEC·PAIRLEC 상수로 내보낸다.

    두 상수는 **여기서만** 만든다. 손으로 고치면 표와 화면이 갈리고, 갈린 것을
    아무도 못 본다 — 화면은 잘못된 강의를 자신 있게 걸고 표는 옳은 것을 담고 있다.
    """
    doc = json.load(io.open(MAP, encoding='utf-8'))
    lec = doc.get('lectures', {})
    fn = lambda n: (lec.get(n) or {}).get('file') or ''
    tl = {t: fn(n) for t, n in sorted(doc.get('map', {}).items()) if fn(n)}
    pl = {k: fn(n) for k, n in sorted(doc.get('pairMap', {}).items()) if fn(n)}
    src = os.path.join(ROOT, 'final.html')
    s = io.open(src, encoding='utf-8').read()

    # 내보내기가 **지금 걸려 있는 것을 잃게 하지 않는다.**
    # TYPELEC 에는 손으로 적어 둔 자리가 있다(「삼투 현상」·「pH 크기 비교」…).
    # 표가 아직 그 이름을 안 담았는데 덮어쓰면, 이어져 있던 문항이 조용히 끊긴다.
    # 끊긴 자리는 화면에서 「강의 보기」 단추가 사라지는 것으로만 드러나고,
    # 아무도 그걸 안 센다. 그래서 여기서 막는다.
    now = re.search(r'const TYPELEC=\{(.*?)\n\};', s, re.S)
    if now:
        had = set(re.findall(r"'([^']+)'\s*:\s*'lec-", now.group(1)))
        lost = sorted(t for t in had
                      if t not in tl and not any(k.endswith(PAIRSEP + t) for k in pl))
        if lost:
            print('내보내면 끊긴다 — 지금 TYPELEC 에 있는데 표에 없는 세부개념 %d종:'
                  % len(lost))
            for t in lost:
                print('   %s' % t)
            print('  → concept-lecture.json 에 먼저 넣고 다시 내보낸다.')
            return 1
    out = []
    for name, table, note in (
        ('PAIRLEC', pl, '영역과 세부개념이 함께 정해 주는 강의. 같은 이름이 단원마다\n'
                        '   다른 강의를 부를 때 쓴다 — 「밀도」는 고체 단원이면 결정격자,\n'
                        '   용액 단원이면 농도 표현, 화학량론이면 몰질량이다.'),
        ('TYPELEC', tl, '세부개념 하나가 곧 강의 하나인 자리. 넓은 영역보다 먼저 본다.')):
        body = json.dumps(table, ensure_ascii=False, separators=(',', ':'))
        line = ('/* %s — tools/lecture_link.py --emit 가 concept-lecture.json 에서 만든다.\n'
                '   %s\n'
                '   ⚠ 손으로 고치지 않는다. 고치려면 concept-lecture.json 을 고치고 다시 내보낸다. */\n'
                'const %s=%s;\n') % (name, note, name, body)
        out.append((name, line))
    changed = 0
    for name, line in out:
        pat = re.compile(r'(/\* %s —.*?\*/\n)?const %s=\{.*?\};\n' % (name, name), re.S)
        if pat.search(s):
            s = pat.sub(lambda m: line, s, count=1)
        else:
            # 아직 없는 상수는 TYPELEC 자리 앞에 세운다(둘 다 lecFor 위에 있어야 한다).
            at = s.index('function lecFor(area,type){')
            s = s[:at] + line + s[at:]
        changed += 1
    io.open(src, 'w', encoding='utf-8').write(s)
    print('final.html 에 PAIRLEC %d · TYPELEC %d 를 썼다.' % (len(pl), len(tl)))
    return 0


def main():
    check = '--check' in sys.argv
    seal = '--seal' in sys.argv
    if '--absorb' in sys.argv:
        return absorb()
    if '--emit' in sys.argv:
        return emit()
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
