#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""학생이 **스스로 풀고 내는 문**이 회차마다 제대로 서 있는지 본다.

무슨 일이 있었나
----------------
`index.html` 은 선생님이 답안을 옮겨 치는 화면이다. 학생이 집에서 혼자 풀고
낼 곳은 `final-submit.html?exam=<회차>` 로 따로 있었는데 — **그 주소로 가는
문이 index.html 어디에도 없었다.** 선생님은 final.html 까지 가서 링크를
복사해 와야 했고, 그래서 실제로 학생에게 안 나갔다(2026-08-29 선생님 지적).

문을 달았으니 이제 그 문이 **빈 방으로 열리지 않게** 지켜야 한다.

무엇을 재나
-----------
index.html 의 `SUBMIT_EXAMS` 는 「이 회차는 학생 제출 화면이 있다」는 목록이다.
그 목록은 `exams.json`(= final-submit.html 이 실제로 아는 회차) 과 정확히
같아야 한다. 어긋나는 두 방향이 다 나쁘다.

    목록에 있는데 exams.json 에 없다   학생이 링크를 눌러 **빈 화면**을 만난다
    exams.json 에 있는데 목록에 없다   풀 수 있는 회차인데 문이 안 보인다

`j0`(조준모의고사 0회)는 아직 exams.json 에 없다 — 그래서 목록에도 없고,
화면에는 「이 회차는 학생 제출 화면이 아직 없습니다」가 뜬다. 그것이 맞다.

    python3 tools/submit_link.py           # 지금 어긋난 곳
    python3 tools/submit_link.py --check    # 어긋나면 빨간불 (CI)
    python3 tools/submit_link.py --write    # index.html 목록을 다시 적는다
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, 'index.html')
EXJ = os.path.join(ROOT, 'exams.json')

BEG = '/* SUBMIT_EXAMS:START */'
END = '/* SUBMIT_EXAMS:END */'
RX_IDX_EXAMS = re.compile(r'\{id:"([^"]+)",title:"')


def index_exam_ids(src):
    """index.html 의 EXAMS 배열에 실린 회차."""
    i = src.index('const EXAMS=[')
    return [m.group(1) for m in RX_IDX_EXAMS.finditer(src[i:i + 60000])]


def listed(src):
    """index.html 에 지금 적혀 있는 SUBMIT_EXAMS."""
    a = src.index(BEG) + len(BEG)
    b = src.index(END, a)
    return sorted(json.loads(re.search(r'new Set\((\[.*?\])\)', src[a:b], re.S).group(1)))


def want(src):
    """서야 하는 것 = index.html 의 회차 ∩ exams.json 의 회차."""
    have = {e['id'] for e in json.load(io.open(EXJ, encoding='utf-8'))}
    return sorted(x for x in index_exam_ids(src) if x in have)


def main():
    check = '--check' in sys.argv
    write = '--write' in sys.argv
    src = io.open(IDX, encoding='utf-8').read()
    now, need = listed(src), want(src)
    gone = [x for x in now if x not in need]
    miss = [x for x in need if x not in now]
    noneed = [x for x in index_exam_ids(src) if x not in need]

    print('index.html 회차 %d개 · 학생 제출 화면이 서는 회차 %d개'
          % (len(index_exam_ids(src)), len(need)))
    if noneed:
        print('  제출 화면 없음(문 대신 까닭을 보여 준다): ' + ', '.join(noneed))

    if not gone and not miss:
        print('\n목록이 exams.json 과 맞는다.')
        return 0

    if gone:
        print('\n빈 방으로 열리는 문 %d개 — exams.json 에 없는데 목록에 있다:' % len(gone))
        for x in gone:
            print('  ' + x)
    if miss:
        print('\n문이 안 보이는 회차 %d개 — 풀 수 있는데 목록에서 빠졌다:' % len(miss))
        for x in miss:
            print('  ' + x)

    if write:
        a = src.index(BEG) + len(BEG)
        b = src.index(END, a)
        new = ('\nconst SUBMIT_EXAMS=new Set(%s);\n'
               % json.dumps(need, ensure_ascii=False))
        io.open(IDX, 'w', encoding='utf-8').write(src[:a] + new + src[b:])
        print('\nindex.html 의 목록을 다시 적었다.')
        return 0

    print('\npython3 tools/submit_link.py --write 로 맞춘다.')
    return 1 if check else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
