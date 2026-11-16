# -*- coding: utf-8 -*-
"""T15 마감 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '이온화에너지'

LINK = [
    ('C15-017', 6, 'M02459'), ('C15-007', 5, 'M02460'), ('C15-024', 6, 'M02461'),
    ('C15-021', 6, 'M02462'),
]

NOTES = {
    'C15-021': (
        "★저작 주의(T15 마감)★ 각도[6](급증 폭이 첫째보다 둘째에서 더 큼)은 ★비로 재면 오히려 "
        "첫째가 크다★ — 나트륨에서 첫 급증은 9.2 배, 둘째는 4.9 배다. 차로 재야 둘째가 크다"
        "(4066 대 112430). 발문이나 정답에서 ★어느 잣대로 재는지 못 박지 않으면 정답이 둘이 "
        "된다★ — M02462 는 '뛰는 양' 으로 적고 해설에서 비와 차를 함께 보였다."),
}


def main():
    cj = json.load(open(CJ, encoding='utf-8'))
    cs = {c['id']: c for c in cj[THEME]}
    n = 0
    for cid, idx, mid in LINK:
        a = cs[cid]['angles'][idx]
        a.setdefault('by', [])
        if mid not in a['by']:
            a['by'].append(mid)
            n += 1
    for cid, note in NOTES.items():
        old = cs[cid].get('note') or ''
        if note not in old:
            cs[cid]['note'] = (old + ' ' + note).strip()
    json.dump(cj, open(CJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tot = sum(len(c['angles']) for c in cj[THEME])
    used = sum(1 for c in cj[THEME] for a in c['angles'] if a.get('by'))
    print('T15 마감 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
