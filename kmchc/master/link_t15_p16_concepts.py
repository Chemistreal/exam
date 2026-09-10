# -*- coding: utf-8 -*-
"""T15 P16 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '이온화에너지'

LINK = [
    ('C15-018', 5, 'M02449'), ('C15-018', 7, 'M02450'), ('C15-024', 5, 'M02451'),
    ('C15-011', 6, 'M02452'), ('C15-012', 6, 'M02453'), ('C15-023', 6, 'M02454'),
    ('C15-003', 4, 'M02455'), ('C15-005', 4, 'M02456'), ('C15-006', 7, 'M02457'),
    ('C15-022', 2, 'M02458'),
]

NOTES = {
    'C15-024': (
        "★저작 주의(T15 P16)★ 각도[6](이온 자료로 중성 원자의 값을 만들지 않기)과 "
        "C15-011[6](이온 자료에서 족을 되돌리기)을 ★한 배치에 두면 서로 어긋나 보인다★ — "
        "하나는 '못 한다', 다른 하나는 '된다' 이기 때문이다. 실제로는 ★값은 못 만들고 자리는 "
        "되돌릴 수 있다★ 는 것이 갈림인데, 그 갈림을 발문에 적지 않으면 학생에게는 모순으로 "
        "보인다. P16 은 011[6] 만 쓰고 024[6] 은 마감으로 미뤘다."),
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
    print('T15 P16 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
