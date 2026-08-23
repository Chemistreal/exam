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

import hashlib, json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'retry-pool.json'

# 단원별 회차가 화올에서 빌려 온 문항 — 풀에는 **같은 문제가 두 번** 실린다
# (kch1u1 55번 == hwol-2012 44번). 재도전 10제가 둘 다 뽑으면 같은 문제를
# 두 번 주고, 방금 kch1u1 을 낸 학생에게 hwol 쪽 쌍둥이를 '새 문항' 으로
# 준다. 출처 문구로 짝을 묶는다.
SRC = re.compile(r'화학올림피아드\s*(\d{4})년\s*(\d+)번')


def _norm(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(s or '')))


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
    ids = {e['id'] for e in exams}
    # 또래 실측 정답률 — 공식 정답률이 없는 회차의 난이도 구멍을 메운다.
    # 표본이 스물은 넘어야 잣대로 쓴다(성적표 MINP 와 같은 바닥).
    try:
        base = json.loads((ROOT / 'cohort' / 'baseline.json')
                          .read_text(encoding='utf-8')).get('exams', {})
    except (OSError, ValueError):
        base = {}
    out = []
    stems = {}          # 지문+보기 지문 해시 → 먼저 실린 문항의 (e, q)
    for e in exams:
        eid = e['id']
        ans = ROOT / 'answers' / ('%s.json' % eid)
        qs = json.loads(ans.read_text(encoding='utf-8')).get('questions', {}) \
            if ans.exists() else {}
        skip = all_correct(e)
        # 복수정답 문항도 뺀다 — 재도전 봉투는 정답을 **하나만** 싣는다.
        # 원본이 ①·② 를 다 인정하는 문항을 실으면, 인정되는 답을 고르고도
        # 오답으로 채점된다. 열한 문항이 그랬다.
        multi = {int(q) for q in (e.get('multi') or {})}
        # exams.json 의 multi 만 믿으면 안 된다. 그 표는 손으로 적는 것이고,
        # **답지(answers/)에도 같은 사실이 따로 적혀 있다** — acceptableAnswers
        # 가 둘 이상이거나 excluded 가 켜진 문항이다. 지금은 두 출처가 딱
        # 맞지만 그것을 강제하는 것이 없어서, 답지에 「①② 모두 인정」 을 적고
        # exams.json 에 안 옮기면 검사는 통과하면서 그 문항이 단일 정답으로
        # 풀에 실린다 — 인정되는 답을 고르고도 오답이 되는 그 버그가 조용히
        # 되살아난다. 그래서 **두 출처를 합쳐서** 뺀다.
        for q, v in qs.items():
            if not isinstance(v, dict):
                continue
            acc = v.get('acceptableAnswers')
            if (isinstance(acc, (list, tuple)) and len(acc) > 1) or v.get('excluded'):
                try:
                    multi.add(int(q))
                except (TypeError, ValueError):
                    pass
        area, typ, rate = e.get('area') or [], e.get('type') or [], e.get('rate') or []
        for i, k in enumerate(e.get('key') or [], 1):
            if i in skip or i in multi:
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
            else:
                # 공식 정답률이 없으면 또래 실측(맞힌 수/응시 수)으로 메운다.
                b = base.get(eid) or {}
                qc, n = b.get('qc') or [], b.get('n') or 0
                if n >= 20 and i <= len(qc) and isinstance(qc[i - 1], (int, float)):
                    row['r'] = max(1, min(99, round(qc[i - 1] / n * 100)))
            # ── 쌍둥이 묶기 ──────────────────────────────────────────
            # ① 출처 문구가 저장소에 있는 화올 회차를 가리키면 그 짝으로.
            q = qs.get(str(i)) or {}
            m = SRC.search(str(q.get('sourceSolution') or '')) if isinstance(q, dict) else None
            if m:
                sid = 'hwol-%s' % m.group(1)
                if sid in ids and sid != eid:
                    row['g'] = '%s:%d' % (sid, int(m.group(2)))
            # ② 출처 표기가 없어도 지문·보기가 글자까지 같으면 같은 문제다.
            if 'g' not in row and isinstance(q, dict):
                sig = _norm(q.get('stem')) + '|' + _norm(q.get('choices'))
                if len(sig) > 40:
                    h = hashlib.md5(sig.encode()).hexdigest()
                    first = stems.setdefault(h, (eid, i))
                    if first != (eid, i) and first[0] != eid:
                        row['g'] = '%s:%d' % first
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
        g = sum(1 for x in made['q'] if 'g' in x)
        print('PASS 재도전 풀 %d문항 (정답률 있는 것 %d · 쌍둥이 표시 %d) · %.0fKB'
              % (n, r, g, len(txt) / 1024))
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
