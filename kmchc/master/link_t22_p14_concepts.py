# -*- coding: utf-8 -*-
"""T22 P14 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-001', 8, 'M02757'), ('C22-005', 1, 'M02758'), ('C22-007', 7, 'M02759'),
        ('C22-010', 6, 'M02760'), ('C22-011', 8, 'M02761'), ('C22-012', 8, 'M02762'),
        ('C22-014', 7, 'M02763'), ('C22-016', 7, 'M02764'), ('C22-018', 5, 'M02765'),
        ('C22-020', 6, 'M02766')]

NOTES = {
    'C22-020': (
        "★대장 주의(T22 P14)★ C22-020 은 '자주 어긋나는 자리' 를 모은 개념이라 각도 여럿이 다른 "
        "개념의 각도와 ★겨냥이 겹치도록 지어져 있다★. 이미 물은 자리는 봉인해 둔다 — [0]≡003[4] · "
        "[1]≡015[8] · [3]≡007[1] · [4]≡001[8] · [7]≡017[4]. P14 는 [6](완전·불완전 가르기)만 썼다."),
    'C22-006': (
        "★대장 주의(T22 P14)★ 각도[2](고리형에 사슬형 일반식을 쓰지 않기)와 [5](분자식만으로는 "
        "꼴을 못 정함)는 각각 003[4]/M02728 과 [6]/M02739 가 이미 물은 자리다 — ★봉인★. "
        "C22-006 은 이로써 소진으로 본다."),
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
    print('T22 P14 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
