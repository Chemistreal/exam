# -*- coding: utf-8 -*-
"""T22 P6 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-002', 8, 'M02677'), ('C22-003', 8, 'M02678'), ('C22-004', 5, 'M02679'),
        ('C22-005', 5, 'M02680'), ('C22-007', 8, 'M02681'), ('C22-009', 6, 'M02682'),
        ('C22-012', 5, 'M02683'), ('C22-014', 4, 'M02684'), ('C22-016', 3, 'M02685'),
        ('C22-018', 2, 'M02686')]

NOTES = {
    'C22-016': (
        "★저작 주의(T22 P6)★ 각도[3](치환 뒤 탄소 수가 그대로)의 정답을 '바뀐 것은 곁가지라 "
        "그대로 있다' 로 적으면 발문의 '바뀌었다·것은' 을 되받아 ★겹침이 정답에서 최다★ 가 "
        "된다(㉪). '뼈대가 그대로라 탄소도 그대로다' 로 적어 비켜 갔다(M02685)."),
    'C22-004': (
        "★저작 주의(T22 P6)★ 각도[5](이중 결합 둘레가 평면)는 004[4](회전이 막힘)와 한 배치에 "
        "두면 ★서로의 해설이 된다★ — 평면인 까닭이 곧 돌지 못하기 때문이다(㉬). P5 에 [4] 를, "
        "P6 에 [5] 를 두어 갈랐고, [5] 는 '방향이 셋이라 평평하게 뻗는다' 는 다른 결로 물었다."),
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
    print('T22 P6 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
