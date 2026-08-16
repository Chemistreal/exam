# -*- coding: utf-8 -*-
"""make_ledger.py — 에이전트가 갈래별로 지어 온 개념 대장 초안을 하나로 세워 맞댄다

  쓰임:  python3 make_ledger.py <초안.json> <테마이름> <접두사> [맞댈 개념 id …]
  보기:  python3 make_ledger.py ledger_t18.json '분자의 구조' C18 C17-014 C17-015 C17-016

  초안 JSON(에이전트 스키마와 같다)
    [{"area":"가","title":"…","concepts":[{"name","stmt","kind","prereq","values","note",
      "angles":[{"a","t","b"}, …]}, …]}, …]

  ★대장을 세우는 자리에서 맞댄다★ — T12·T15·T16 이 세 번 값을 치르고 얻은 규약이다.
    ① 이 대장 ★안에서★ 각도끼리 자카드 0.55 이상이면 저장하지 않고 죽는다
    ② ★앞 테마가 이미 가져간 각도★ 와도 맞댄다(인자로 받은 개념 id) — 겨냥이 겹치면
       저작 단계에 가서야 드러나고, 그때는 이미 문항이 서른 개 나와 있다
    ③ 넘긴 짝은 화면에 그대로 뿌린다. 사람이 보고 한쪽을 고쳐 다시 돌린다.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CJ = os.path.join(HERE, 'concepts.json')


def toks(s):
    return {w for w in re.findall(r'[가-힣]{2,}', s)}


def jac(a, b):
    A, B = toks(a), toks(b)
    return len(A & B) / len(A | B) if A and B else 0.0


def main():
    src, theme, prefix = sys.argv[1:4]
    cross_ids = sys.argv[4:]
    draft = json.load(open(src, encoding='utf-8'))

    concepts = []
    for area in draft:
        for c in area.get('concepts', []):
            concepts.append(c)
    print('갈래 %d · 개념 %d · 각도 %d'
          % (len(draft), len(concepts), sum(len(c['angles']) for c in concepts)))

    rows = []
    out = []
    for i, c in enumerate(concepts, 1):
        cid = '%s-%03d' % (prefix, i)
        angles = [{'a': a['a'], 't': a['t'], 'b': bool(a.get('b'))} for a in c['angles']]
        out.append({'id': cid, 'page': 0, 'kind': c['kind'], 'prereq': c.get('prereq', []),
                    'stmt': '%s — %s' % (c['name'], c['stmt']) if '—' not in c['stmt'] else c['stmt'],
                    'values': c.get('values', ''), 'note': c.get('note', ''), 'angles': angles})
        for k, a in enumerate(angles):
            rows.append(('%s[%d]' % (cid, k), a['a']))

    cj = json.load(open(CJ, encoding='utf-8'))
    prev = []
    for _th, cs in cj.items():
        for c in cs:
            if c['id'] in cross_ids:
                for k, a in enumerate(c['angles']):
                    prev.append(('%s[%d]' % (c['id'], k), a['a']))

    inner = [(jac(a[1], b[1]), a, b)
             for i, a in enumerate(rows) for b in rows[i + 1:]
             if jac(a[1], b[1]) >= 0.55]
    cross = [(jac(r[1], p[1]), r, p) for r in rows for p in prev if jac(r[1], p[1]) >= 0.55]

    if inner or cross:
        if inner:
            print('\n  ❌ 대장 안에서 겹침 %d 짝 — 저장하지 않는다' % len(inner))
            for s, a, b in sorted(inner, reverse=True)[:25]:
                print('     %.2f  %s %s\n           %s %s' % (s, a[0], a[1], b[0], b[1]))
        if cross:
            print('\n  ❌ 앞 테마가 가져간 자리와 겹침 %d 짝 — 저장하지 않는다' % len(cross))
            for s, a, b in sorted(cross, reverse=True)[:25]:
                print('     %.2f  %s %s\n           %s %s' % (s, a[0], a[1], b[0], b[1]))
        raise SystemExit(1)

    cj[theme] = out
    json.dump(cj, open(CJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('  ✅ %d 각도를 모두 맞대었다 — 안에서도, 앞 테마 %d 각도와도 0.55 이상 없음'
          % (len(rows), len(prev)))
    print('  ✅ concepts.json 에 %s (%s-001~%s) 로 저장' % (theme, prefix, out[-1]['id'][-3:]))


if __name__ == '__main__':
    main()
