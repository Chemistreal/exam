#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""남은 일 — 한 자리에서 **재어서** 답한다.

왜 이 자를 두나
---------------
「다 됐나?」 를 물었을 때 기억으로 답하면 틀린다. 이 세션에서만도 다 끝난 줄
알았던 자리 뒤에서 진짜 결함이 셋 나왔다(j0 단위 · 동형 은행 다섯 · 기체상수).
그래서 목록을 **글로 적어 두지 않고 세어서** 낸다. 항목마다 «무엇을 세는가» 가
코드로 박혀 있으므로, 저장소가 바뀌면 이 화면이 저절로 따라 바뀐다.

읽는 법
-------
    ✅  다 됐다
    ◻   아직이다 — 몇 개 남았는지 옆에 적힌다
    🔒  선생님 답을 기다린다 — 기계가 정할 수 없는 자리다

    python3 tools/todo_status.py            # 판을 본다
    python3 tools/todo_status.py --check    # CI 용(판이 만들어지는지만 본다)

DT 저장소 항목은 여기서 못 잰다(다른 저장소다). 재는 명령을 대신 적는다.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _j(*p):
    return json.load(io.open(os.path.join(ROOT, *p), encoding='utf-8'))


def answers():
    xs = _j('exams.json')
    out = {}
    for e in xs:
        p = os.path.join(ROOT, 'answers', '%s.json' % e['id'])
        out[e['id']] = (_j('answers', '%s.json' % e['id']).get('questions', {})
                        if os.path.exists(p) else {})
    return xs, out


def item_misc4():
    """선지별 오답 해설 — 왜 그 선지를 골랐는지."""
    xs, ans = answers()
    tot = sum(e['nQ'] for e in xs)
    have = sum(1 for eid in ans for k in ans[eid] if ans[eid][k].get('misconceptions'))
    rounds = sorted((e['id'], e['nQ'] - sum(1 for k in ans[e['id']]
                                            if ans[e['id']][k].get('misconceptions')))
                    for e in xs)
    short = [(i, n) for i, n in rounds if n > 0]
    return have, tot, short


def item_twins():
    """동형문제 은행 — 회차 이름의 은행이 있는가."""
    xs = _j('exams.json')
    miss = [e['id'] for e in xs
            if not os.path.exists(os.path.join(ROOT, 'donghyung', '%s.json' % e['id']))]
    q = sum(e['nQ'] for e in xs if e['id'] in miss)
    return len(xs) - len(miss), len(xs), miss, q


def item_lecquiz():
    """강의마다 확인 문제가 붙었는가.

    ⚠ **여기서 다시 세지 않는다.** 「풀에 맞는 문항이 두 개 있는가」는
    lecture_quiz.py 가 문항 풀을 읽어서 정하는 것이라, 화면에서 표식을 찾는
    식으로 흉내내면 그 자와 **다른 수**가 나온다(처음에 그렇게 짜서 125강이
    모두 비었다고 나왔다 — 실제로는 하나였다). 두 자가 다른 말을 하면 목록을
    믿을 수 없게 되므로, 세는 일은 그 자에게 맡기고 답만 읽는다.
    """
    import subprocess
    try:
        r = subprocess.run([sys.executable,
                            os.path.join(ROOT, 'tools', 'lecture_quiz.py'), '--check'],
                           capture_output=True, text=True, timeout=300, cwd=ROOT)
    except Exception:
        return None
    out = r.stdout
    m = re.search(r'확인 문제가 붙은 강의 (\d+)강 / (\d+)강', out)
    if not m:
        return None
    have, tot = int(m.group(1)), int(m.group(2))
    e = re.search(r'비운 강의 \d+강[^:]*: (.+)', out)
    empty = [x.strip() for x in e.group(1).split(',')] if e else []
    return have, tot, empty


def item_reviewnote():
    """확인 필요(reviewNote) 를 한자리에서 볼 곳이 있는가."""
    _, ans = answers()
    n, where = 0, {}
    for eid in ans:
        c = sum(1 for k in ans[eid] if str(ans[eid][k].get('reviewNote') or '').strip())
        if c:
            where[eid] = c
            n += c
    page = os.path.exists(os.path.join(ROOT, 'review-notes.html'))
    return n, len(where), page


def item_teacher():
    """선생님 답을 기다리는 칸."""
    p = os.path.join(ROOT, 'docs', '선생님이-정할-칸.md')
    if not os.path.exists(p):
        return 0, 0
    s = io.open(p, encoding='utf-8').read()
    import re
    heads = re.findall(r'^### (~~)?(A\d+)', s, re.M)
    done = sum(1 for a, _ in heads if a)
    return len(heads) - done, len(heads)


ROW = '  %s %-28s %s'


def main():
    check = '--check' in sys.argv
    print('남은 일 — %s 에서 재었다\n' % os.path.basename(ROOT))

    print('exam 저장소')

    have, tot, short = item_misc4()
    ok = not short
    print(ROW % ('✅' if ok else '◻ ', '선지별 오답 해설',
                 '%d/%d문항 (%d%%)%s' % (have, tot, round(100 * have / tot),
                                        '' if ok else ' · %d문항 남음' % (tot - have))))
    if short:
        top = ', '.join('%s %d' % t for t in sorted(short, key=lambda x: -x[1])[:6])
        print('       모자란 회차 %d개 — %s …' % (len(short), top))

    hv, tt, miss, q = item_twins()
    print(ROW % ('✅' if not miss else '◻ ', '동형문제 은행',
                 '%d/%d회차%s' % (hv, tt, '' if not miss
                                  else ' · %s (%d문항)' % (', '.join(miss), q))))

    lq = item_lecquiz()
    if lq:
        hv, tt, empty = lq
        print(ROW % ('✅' if not empty else '◻ ', '강의별 확인 문제',
                     '%d/%d강%s' % (hv, tt, '' if not empty
                                    else ' · 비어 있는 강의 ' + ', '.join(empty))))
        if empty == ['116']:
            # 이건 고장이 아니다. 은행 전체에 「작용기」가 지문에 든 검수 문항이
            # **둘뿐**이고, 그 둘도 하나는 아미노산(→118), 하나는 탄화수소(→115)
            # 쪽이다. lecture_quiz 의 규칙이 「두 문항도 못 찾으면 비운다 —
            # 억지로 채우면 『이 강의를 들으면 이걸 풀 수 있다』가 거짓이 된다」이므로
            # 비운 것이 맞다. 채우려면 **작용기 문항을 은행에 써 넣어야** 한다.
            print('       116(작용기 개론)은 은행에 맞는 문항이 둘뿐이라 비운 것이다 —')
            print('       억지로 채우지 않는 것이 규칙이다. 채우려면 문항을 써 넣어야 한다.')

    n, r, page = item_reviewnote()
    print(ROW % ('✅' if page else '◻ ', '확인 필요를 한자리에서',
                 '%d건 · %d회차%s' % (n, r, '' if page else ' · 모아 보는 곳이 없다')))

    left, allc = item_teacher()
    print(ROW % ('🔒', '선생님이 정할 칸',
                 '%d/%d 칸이 답을 기다린다' % (left, allc)))

    print('\nDT 저장소 (여기서는 못 잰다 — 그 저장소에서 재세요)')
    print('  ?  개념↔강의 잇기               cd ../dt && python3 tools/lec_link.py --check')
    print('  ?  검사 스무 개                 cd ../dt && node tests/run.js')

    print('\n검사 전부                        '
          'ls tools/*.py | xargs -I{} python3 {} --check')
    print('\n✅ 다 됐다 · ◻ 아직이다 · 🔒 선생님 답을 기다린다')
    return 0 if check else 0


if __name__ == '__main__':
    sys.exit(main())
