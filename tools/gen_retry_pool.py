#!/usr/bin/env python3
"""「즉시 재도전 10제」가 고를 문항 풀(`retry-pool.json`)을 만든다.

무엇에 쓰나
-----------
학생이 변형본 60제나 실전 30제를 내고 나면, **틀린 문항의 개념**만 모아
같은 개념의 다른 문항 열 개를 그 자리에서 뽑아 준다. 그 열 개를 고를 곳이
이 풀이다.

왜 미리 만드나
--------------
브라우저에서 회차 마흔셋의 답지를 다 받아 훑을 수는 없다 — 6MB 가 넘는다.
개념·정답·정답률만 남기면 한 파일에 들어간다.

무엇을 담나
-----------
`exams.json` 의 문항만 담는다. 이 문항들은 크롭이 이미 다 있어서
(`crops/<회차>/<번호>.png`, tests/wrongbook-assets.py 가 지킨다) 재도전
시험지가 그림을 빌려 쓸 수 있다. 학생별 회차(student-finals)는 안 담는다 —
그 학생이 방금 푼 문제를 다시 주면 재도전이 아니다.

전원정답·폐기 문항은 뺀다. 답이 하나로 정해지지 않으면 채점이 안 된다.

`r` 은 문제지 원본에 적혀 있던 **공식 정답률**이다(화올 10회차 600문항).
낮을수록 어렵다 — 「이 학생이 틀릴 만한」 을 고르는 잣대가 된다.

    python3 tools/gen_retry_pool.py --write
    python3 tools/gen_retry_pool.py --check
"""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'retry-pool.json'


def all_correct(e):
    """전원정답·폐기 문항 번호."""
    out = set(e.get('miss') or []) | set(e.get('voided') or [])
    for q, v in (e.get('multi') or {}).items():
        if len(v) >= 4:
            out.add(int(q))
    for i, k in enumerate(e.get('key') or [], 1):
        if k in (0, '', None, 'X', 'x'):
            out.add(i)
    return out


def build():
    exams = json.loads((ROOT / 'exams.json').read_text(encoding='utf-8'))
    out = []
    for e in exams:
        eid = e['id']
        ans = ROOT / 'answers' / ('%s.json' % eid)
        qs = json.loads(ans.read_text(encoding='utf-8')).get('questions', {}) \
            if ans.exists() else {}
        skip = all_correct(e)
        area, typ, rate = e.get('area') or [], e.get('type') or [], e.get('rate') or []
        for i, k in enumerate(e.get('key') or [], 1):
            if i in skip:
                continue
            a = area[i - 1] if i <= len(area) else ''
            t = typ[i - 1] if i <= len(typ) else ''
            if not a and not t:
                q = qs.get(str(i)) or {}
                a, t = q.get('area', ''), q.get('concept', '')
            row = {'e': eid, 'q': i, 'k': int(k), 'a': a, 't': t}
            r = rate[i - 1] if i <= len(rate) else None
            if isinstance(r, (int, float)) and r:
                row['r'] = int(r)
            out.append(row)
    return {
        'schemaVersion': 1,
        'note': 'tools/gen_retry_pool.py 가 exams.json + answers 에서 만든다. '
                '손으로 고치지 않는다. 「즉시 재도전 10제」가 여기서 문항을 고른다.',
        'q': out,
    }


def main():
    argv = sys.argv[1:]
    made = build()
    txt = json.dumps(made, ensure_ascii=False, separators=(',', ':')) + '\n'
    if '--check' in argv:
        if not OUT.exists():
            print('FAIL retry-pool.json 이 없다 — --write 로 만든다')
            return 1
        if OUT.read_text(encoding='utf-8') != txt:
            print('FAIL retry-pool.json 이 exams.json·답지와 어긋난다 — --write 로 맞춘다')
            return 1
        n = len(made['q'])
        r = sum(1 for x in made['q'] if 'r' in x)
        print('PASS 재도전 풀 %d문항 (공식 정답률 있는 것 %d) · %.0fKB'
              % (n, r, len(txt) / 1024))
        return 0
    if '--write' in argv:
        OUT.write_text(txt, encoding='utf-8')
        print('retry-pool.json 에 적었다 — %d문항 · %.0fKB'
              % (len(made['q']), len(txt) / 1024))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
