#!/usr/bin/env python3
"""오답 카드의 **한 줄**이 비어 나가지 않는지 센다.

성적표의 '오답 개념 클리닉' 은 틀린 문항마다 두 줄을 쓴다.

    · 완충용액
      완충 용액은 약산과 그 짝염기가 함께 있어야 만들어진다는 조건을 놓침.

윗줄은 `exams.json` 의 `type` 이고, 아랫줄은 `final.html` 의 `OMLIB` 에서
찾아 온다. `OMLIB` 에 그 유형이 없으면 **윗줄만 뜨고 아래가 빈다** — 학생은
자기가 무엇을 잘못 알았는지 못 읽는다. 조용히 비기 때문에 아무도 모른다.

한때 2220문항의 유형 가운데 일흔두 가지가 그랬다. 회차를 새로 넣을 때마다
같은 일이 되풀이되므로, 여기서 센다.

`OMLIB` 는 **부분 문자열**로 걸린다(`omFor` 가 위에서부터 훑어 처음 걸리는
것을 쓴다). 그래서 '완충용액의pH' 처럼 두 키에 다 걸리는 유형이 생긴다 —
그건 잘못이 아니라 **순서로 정하는 일**이다. 여기서는 걸리느냐만 본다.

    python3 tools/om_cover.py            # 안 걸리는 유형을 보여 준다
    python3 tools/om_cover.py --check    # 하나라도 있으면 빨간불
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMS = os.path.join(ROOT, 'exams.json')
FINAL = os.path.join(ROOT, 'final.html')


def omlib_keys():
    """final.html 안의 OMLIB 에서 앞칸(유형 키)만 순서대로 뽑는다."""
    src = open(FINAL, encoding='utf-8').read()
    i = src.find('const OMLIB=[')
    if i < 0:
        sys.exit('OMLIB 를 못 찾았다 — final.html 이 바뀌었나')
    j = src.find('\n];', i)
    if j < 0:
        sys.exit('OMLIB 의 끝을 못 찾았다')
    body = src[i:j]
    # ["키","설명"] 의 앞칸만. 주석 줄에는 [" 가 없다.
    return re.findall(r'\["([^"]+)"\s*,', body)


def exam_types():
    """회차별 유형을 (유형, 회차, 문항번호)로 편다."""
    data = json.load(open(EXAMS, encoding='utf-8'))
    rounds = data if isinstance(data, list) else data.get('exams', [])
    out = []
    for ex in rounds:
        for i, t in enumerate(ex.get('type') or []):
            if t:
                out.append((t, ex.get('id', '?'), i + 1))
    return out


def per_question():
    """문항마다 따로 쓴 misconception 이 얼마나 채워졌는지 센다.

    OMLIB 의 줄은 **유형 하나에 하나**라, 같은 유형의 두 문항은 같은 말을 받는다.
    문항마다 쓴 misconception 이 있으면 오답노트가 그것을 먼저 쓴다(더 좁게 맞다).
    OMLIB 는 그것이 없을 때 받쳐 주는 자리다 — 여기서는 어디까지 왔는지만 센다.
    """
    data = json.load(open(EXAMS, encoding='utf-8'))
    rounds = data if isinstance(data, list) else data.get('exams', [])
    have = total = 0
    thin = []
    for ex in rounds:
        p = os.path.join(ROOT, 'answers', '%s.json' % ex.get('id'))
        if not os.path.exists(p):
            continue
        qs = (json.load(open(p, encoding='utf-8')).get('questions') or {})
        h = n = 0
        for i in range(1, int(ex.get('nQ') or 0) + 1):
            q = qs.get(str(i))
            if not q:
                continue
            n += 1
            if (q.get('misconception') or '').strip():
                h += 1
        have += h
        total += n
        if h < n:
            thin.append((ex.get('id'), h, n))
    return have, total, thin


def main():
    check = '--check' in sys.argv
    keys = omlib_keys()
    rows = exam_types()

    miss = {}
    for t, eid, q in rows:
        if not any(k in t for k in keys):
            miss.setdefault(t, []).append('%s %d번' % (eid, q))

    types = sorted({t for t, _, _ in rows})
    print('유형 %d종 · 문항 %d개 · OMLIB %d줄' % (len(types), len(rows), len(keys)))

    have, total, thin = per_question()
    print('문항별 오개념 %d/%d문항' % (have, total))
    for eid, h, n in thin:
        print('    %-22s %d/%d' % (eid, h, n))

    # 2026-08-07 에 2220문항이 모두 자기 오개념을 갖게 됐다. 여기서부터는
    # 빠지는 것을 빨간불로 막는다 — 새 회차를 넣을 때 한 문항이라도 비면
    # 그 학생은 유형 단위의 일반적인 말만 받게 된다.
    if thin:
        print('\n문항별 오개념이 빠진 회차가 있다.')
        print('answers/<회차>.json 의 그 문항에 misconception 을 써 넣어라.')
        if check:
            return 1

    if not miss:
        print('한 줄이 비는 유형: 없음')
        return 0

    print('\n한 줄이 비는 유형 %d종:' % len(miss))
    for t in sorted(miss):
        where = miss[t]
        tail = '' if len(where) <= 3 else ' 외 %d곳' % (len(where) - 3)
        print('  %-22s %s%s' % (t, ', '.join(where[:3]), tail))
    print('\nfinal.html 의 OMLIB 에 그 유형의 오개념 한 줄을 넣어라.')
    print('넣을 자리는 표의 **맨 뒤**다 — 앞에 끼우면 이미 맞던 유형을 가로챈다.')
    return 1 if check else 0


if __name__ == '__main__':
    sys.exit(main())
