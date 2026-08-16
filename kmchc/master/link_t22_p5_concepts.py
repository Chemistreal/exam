# -*- coding: utf-8 -*-
"""T22 P5 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-001', 7, 'M02667'), ('C22-003', 5, 'M02668'), ('C22-004', 4, 'M02669'),
        ('C22-006', 8, 'M02670'), ('C22-007', 6, 'M02671'), ('C22-010', 5, 'M02672'),
        ('C22-011', 4, 'M02673'), ('C22-013', 3, 'M02674'), ('C22-015', 2, 'M02675'),
        ('C22-017', 0, 'M02676')]

NOTES = {
    'C22-017': (
        "★대장 주의(T22 P5)★ 각도[1](브로민 물의 색이 사라지는지로 가려내기)은 ★015[2](할로젠을 "
        "더할 때 색이 사라짐)와 같은 자리★ 다 — M02675 가 015[2] 로 물었으므로 봉인. 낱말이 "
        "달라 대장 맞댐이 잡지 못한 짝이라 ★build_c22_concepts.py 의 SAME 에 적어 두어야 할 "
        "자리★ 였다. 자카드가 못 보는 겹침은 여전히 사람이 찾는다."),
    'C22-004': (
        "★저작 주의(T22 P5)★ 각도[4](회전이 막힘)의 정답을 '이중 결합 자리는 돌지 못해 굳어 "
        "있다' 로 적으면 발문의 낱말을 셋이나 되받아 ★겹침이 정답에서 최다★ 가 된다(㉪). "
        "'두 겹이 붙들어 굳어 있는 것이다' 로 적어 발문을 비켜 갔다(M02669)."),
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
    print('T22 P5 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
